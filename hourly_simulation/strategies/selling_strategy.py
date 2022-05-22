import numpy as np
import pandas as pd
from numba import jit

from df_objects.df_objects import DemandDf, ProductionDf, ElectricityUseDf, CostElectricityDf
from hourly_simulation.parameters import Params, SELLING_COST, BINARY_SELLING_COST, BUY_COST


# todo: add documentation

@jit
def get_index(day_index: int, hour_index: int):
    return day_index * 24 + hour_index


def first_selling_strategy(demand: DemandDf, production: ProductionDf, param: Params, number_of_batteries,
                           binary_cost_profile:
                           CostElectricityDf = BINARY_SELLING_COST, cost_profile: CostElectricityDf = SELLING_COST,
                           sell_profile:
                           CostElectricityDf = BUY_COST) -> ElectricityUseDf:
    """
        Given a matching rect cost and sell function
        :param demand: DemandDf: pd.DataFrame(columns=[HourOfYear, 'Demand'])
        :param production: ProductionDf: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
        :param cost_profile: CostElectricityDf wrapper of pd.DataFrame with Cost and HourOfYear
        :param sell_profile: CostElectricityDf wrapper of pd.DataFrame with selling price and HourOfYear
        :param binary_cost_profile: CostElectricityDf wrapper of pd.DataFrame with Cost and HourOfYear as binary
            (peak / low)
        :param battery_capacity: float capacity of battery
        :param battery_power: power of the battery
        :return: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost, SolarSold, StoredSold]
        """
    sale_max_power = param.MAX_SELLING_POWER
    battery_power = param.CHARGE_POWER * number_of_batteries
    battery_capacity = param.BATTERY_CAPACITY * number_of_batteries
    battery_efficiency = param.BATTERY_EFFICIENCY

    len_simulation = len(demand.df[demand.HourOfYear])
    if not len_simulation % 24 == 0:
        raise ValueError("Length of input should be a whole number of days")

    # Helpful definitions
    bin_cost = binary_cost_profile.df[binary_cost_profile.Cost].to_numpy()
    production = production.df[production.SolarProduction].to_numpy()  # overwriting
    demand = demand.df[demand.Demand].to_numpy()
    day_use = {c: np.zeros(len(demand)) for c in ElectricityUseDf.COLUMNS}
    total_stored = 0
    # Iterating days
    for day_index in range(0, len_simulation // 24):
        # iterate expensive hours and use all the production for the demand
        expensive_hours = [i for i, x in enumerate(bin_cost[day_index * 24: (day_index + 1) * 24]) if x == 1]
        cheap_hours = [i for i, x in enumerate(bin_cost[day_index * 24: (day_index + 1) * 24]) if x == 0]
        expansive_completion = 0
        expansive_use_completion = 0
        if not len(expensive_hours) == 0:
            for hour_index in expensive_hours:
                i = get_index(day_index, hour_index)
                needed_power = demand[i]
                solar_used = min(production[i], needed_power)
                day_use[ElectricityUseDf.SolarUsage][i] += solar_used
                demand[i] -= solar_used
                solar_sold = min(production[i] - solar_used, sale_max_power)
                day_use[ElectricityUseDf.SolarSold][i] = solar_sold
                solar_lost = production[i] - solar_used - solar_sold  # not storing in expansive hours
                day_use[ElectricityUseDf.SolarLost][i] += solar_lost
                production[i] -= (solar_used + solar_sold + solar_lost)
                expansive_completion += min(demand[i] + sale_max_power - solar_sold,
                                            battery_power)  # to buy in cheap hours later
                expansive_use_completion += min(demand[i], battery_power)
            # Storing over production
            for hour_index in range(expensive_hours[0] - 1, -1, -1):
                if total_stored >= battery_capacity:  # trying to fill the battery
                    break
                i = get_index(day_index, hour_index)
                needed_power = demand[i]
                overproduction = production[i] - min(production[i], needed_power)
                storing = min(overproduction, (battery_capacity - total_stored) / battery_efficiency, battery_power /
                              battery_efficiency)
                total_stored += storing * battery_efficiency  # when using battery, some power disappears
                day_use[ElectricityUseDf.SolarStored][i] = storing * battery_efficiency
                day_use[ElectricityUseDf.SolarLost][i] = storing * (1 - battery_efficiency)
                print(f"before production [{hour_index+1}] = {production[i]}", end="   ")
                print(f"and storing is {storing}", end="    ")
                print(f"{production[i]} => {production[i]} - {storing}", end="   ")
                production[i] = production[i] - storing
                print(f"after production [{hour_index + 1}] = {production[i]}")

            is_buying_profitable = get_is_buying_profitable(battery_efficiency, binary_cost_profile, cost_profile,
                                                            sell_profile)
            if is_buying_profitable:
                effective_battery_capacity = min(battery_capacity, expansive_completion)
                for hour_index in range(expensive_hours[0] - 1, -1, -1):
                    if total_stored >= effective_battery_capacity:
                        break
                    i = get_index(day_index, hour_index)
                    solar_buy = min(battery_power - day_use[ElectricityUseDf.SolarStored][i], effective_battery_capacity
                                    - total_stored)
                    total_stored += solar_buy
                    day_use[ElectricityUseDf.GasStored][i] = solar_buy
            expansive_sell_completion = total_stored - expansive_use_completion
            for hour_index in expensive_hours:
                i = get_index(day_index, hour_index)
                stored_used = min(demand[i], battery_power - day_use[ElectricityUseDf.SolarSold][i], total_stored)
                total_stored -= stored_used
                day_use[ElectricityUseDf.StoredUsage][i] = stored_used
                if expansive_sell_completion > 0:  # in case that the stored power won't last to the last expansive hour
                    stored_sell = min(sale_max_power - day_use[ElectricityUseDf.SolarSold][i], battery_power -
                                      day_use[ElectricityUseDf.StoredUsage][i], expansive_sell_completion)
                    expansive_sell_completion -= stored_sell
                else:
                    stored_sell = 0
                day_use[ElectricityUseDf.StoredSold][i] = stored_sell
                total_stored -= stored_sell
                day_use[ElectricityUseDf.GasUsage][i] = demand[i] - stored_used

            for hour_index in cheap_hours:
                i = get_index(day_index, hour_index)
                solar_used = min(production[i], demand[i])
                day_use[ElectricityUseDf.SolarUsage][i] = solar_used
                solar_sold = min(production[i] - solar_used, sale_max_power)
                day_use[ElectricityUseDf.SolarSold][i] = solar_sold
                day_use[ElectricityUseDf.SolarLost][i] += production[i] - solar_used - solar_sold
                day_use[ElectricityUseDf.GasUsage][i] = demand[i] - solar_used

        else:
            # greedy_with_sale
            for i in range(day_index * 24, (day_index + 1) * 24):
                needed_power = demand[i]
                solar_used = min(production[i], needed_power)
                day_use[ElectricityUseDf.SolarUsage][i] = solar_used
                needed_power -= solar_used
                solar_stored = min(production[i] - solar_used, battery_capacity - total_stored,
                                   battery_power) * battery_efficiency
                day_use[ElectricityUseDf.SolarStored][i] = solar_stored
                total_stored += solar_stored
                solar_sold = min(production[i] - solar_used - solar_stored, sale_max_power)
                day_use[ElectricityUseDf.SolarSold][i] = solar_sold
                solar_lost = production[i] - solar_used - solar_stored - solar_sold
                day_use[ElectricityUseDf.SolarLost][i] = solar_lost
                stored_used = min(total_stored, needed_power, battery_power)
                day_use[ElectricityUseDf.StoredUsage][i] = stored_used
                total_stored -= stored_used
                needed_power -= stored_used
                day_use[ElectricityUseDf.GasUsage][i] = needed_power

    hourly_use = ElectricityUseDf(pd.DataFrame())
    hourly_use.df[hourly_use.GasUsage] = day_use[ElectricityUseDf.GasUsage]
    hourly_use.df[hourly_use.SolarUsage] = day_use[ElectricityUseDf.SolarUsage]
    hourly_use.df[hourly_use.StoredUsage] = day_use[ElectricityUseDf.StoredUsage]
    hourly_use.df[hourly_use.SolarStored] = day_use[ElectricityUseDf.SolarStored]
    hourly_use.df[hourly_use.SolarLost] = day_use[ElectricityUseDf.SolarLost]
    hourly_use.df[hourly_use.SolarSold] = day_use[ElectricityUseDf.SolarSold]
    hourly_use.df[hourly_use.StoredSold] = day_use[ElectricityUseDf.StoredSold]
    hourly_use.df[hourly_use.GasStored] = day_use[ElectricityUseDf.GasStored]

    hourly_use.df[hourly_use.HourOfYear] = sell_profile.df[CostElectricityDf.HourOfYear]
    return hourly_use


def get_is_buying_profitable(battery_efficiency, binary_cost_profile, cost_profile, sell_profile):
    low_index = binary_cost_profile.df.loc[binary_cost_profile.df[binary_cost_profile.Cost] == 0].index.tolist()[0]
    peak_index = binary_cost_profile.df.loc[binary_cost_profile.df[binary_cost_profile.Cost] == 1].index.tolist()[0]
    low_buy_price = cost_profile.df[cost_profile.Cost].loc[low_index]
    peak_sell_price = sell_profile.df[sell_profile.Cost].loc[peak_index]
    return low_buy_price * battery_efficiency < peak_sell_price
