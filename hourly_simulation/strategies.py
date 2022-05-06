import numpy as np
import pandas as pd
from numba import jit

from df_objects.df_objects import DemandDf, ProductionDf, ElectricityUseDf, CostElectricityDf
from hourly_simulation.parameters import Params


# def store_first_strategy(demand: DemandDf, production: ProductionDf, battery_capacity: int) -> ElectricityUseDf:
#     """
#     Deprecated: not useful.
#     This is the implementation of the greedy use strategy - using the solar stored whenever possible
#     :param demand: DemandDf: pd.DataFrame(columns=[HourOfYear, 'Demand'])
#     :param production: ProductionDf: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
#     :param battery_capacity: int size of battery
#     :return: ElectricityUseDf: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
#     """
#     current_battery_capacity = 0
#     next_hour = {ElectricityUseDf.GasUsage: [], ElectricityUseDf.SolarUsage: [], ElectricityUseDf.StoredUsage: [],
#                  ElectricityUseDf.SolarStored: [], ElectricityUseDf.SolarLost: []}
#     electricity_data = pd.merge(demand.df, production.df, on=ElectricityUseDf.HourOfYear)
#     for row in electricity_data.itertuples():
#         needed_power = row.Demand
#         # Handle Early Stored Energy
#         if current_battery_capacity > 0:
#             stored_used = min(current_battery_capacity, needed_power)
#             next_hour[ElectricityUseDf.StoredUsage].append(stored_used)
#             needed_power -= stored_used
#             current_battery_capacity -= stored_used
#         else:
#             next_hour[ElectricityUseDf.StoredUsage].append(0)
#         # Handle Produced Energy
#         if row.SolarProduction >= needed_power:
#             next_hour[ElectricityUseDf.GasUsage].append(0)
#             next_hour[ElectricityUseDf.SolarUsage].append(needed_power)
#             solar_stored = min(row.SolarProduction - needed_power, battery_capacity - current_battery_capacity)
#             next_hour[ElectricityUseDf.SolarStored].append(solar_stored)
#             next_hour[ElectricityUseDf.SolarLost].append(max(row.SolarProduction - needed_power - solar_stored, 0))
#         else:
#             next_hour[ElectricityUseDf.GasUsage].append(needed_power - row.SolarProduction)
#             next_hour[ElectricityUseDf.SolarUsage].append(row.SolarProduction)
#             next_hour[ElectricityUseDf.SolarStored].append(0)
#             next_hour[ElectricityUseDf.SolarLost].append(0)
#         current_battery_capacity += next_hour[ElectricityUseDf.SolarStored][-1]
#     hourly_use = pd.DataFrame.from_dict(next_hour)
#     hourly_use[ElectricityUseDf.HourOfYear] = electricity_data[ElectricityUseDf.HourOfYear]
#     return ElectricityUseDf(hourly_use)


def greedy_use_strategy(demand: DemandDf, production: ProductionDf, params: Params, battery_capacity: float,
                        battery_power: float) -> ElectricityUseDf:
    """
    This is the implementation of the better use strategy - using the solar produced whenever possible,
    then the stored energy and only then using gas power
    note: this would be the perfect strategy if the price for gas power would be the same during all hours
    :param demand: DemandDf: pd.DataFrame(columns=[HourOfYear, 'Demand'])
    :param production: ProductionDf: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
    :param battery_capacity: float capacity of battery
    :param battery_power: power of the battery
    :return: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    """
    len_simulation = len(demand.df[demand.HourOfYear])
    gas_usage_arr, solar_usage_arr, stored_usage_arr, solar_stored_arr, \
    solar_lost_arr = __greedy_use_loop(len_simulation,
                                       battery_capacity,
                                       battery_power,
                                       params.BATTERY_EFFICIENCY,
                                       demand.df[demand.Demand].to_numpy(),
                                       production.df[production.SolarProduction].to_numpy())

    hourly_use = ElectricityUseDf(pd.DataFrame())
    hourly_use.df[hourly_use.GasUsage] = gas_usage_arr
    hourly_use.df[hourly_use.SolarUsage] = solar_usage_arr
    hourly_use.df[hourly_use.StoredUsage] = stored_usage_arr
    hourly_use.df[hourly_use.SolarStored] = solar_stored_arr
    hourly_use.df[hourly_use.SolarLost] = solar_lost_arr
    hourly_use.df[hourly_use.HourOfYear] = demand.df[ElectricityUseDf.HourOfYear]
    # no selling in this strategy
    hourly_use.df[ElectricityUseDf.SolarSold] = 0
    hourly_use.df[ElectricityUseDf.StoredSold] = 0
    return hourly_use


@jit
def __greedy_use_loop(len_simulation, battery_capacity, battery_power, battery_efficiency, demand, production):
    storage: float = 0
    gas_usage_arr = np.zeros(len_simulation)
    solar_usage_arr = np.zeros(len_simulation)
    stored_usage_arr = np.zeros(len_simulation)
    solar_stored_arr = np.zeros(len_simulation)
    solar_lost_arr = np.zeros(len_simulation)
    for i in range(len_simulation):
        needed_power = demand[i]
        solar_used = min(production[i], needed_power)
        solar_usage_arr[i] = solar_used
        needed_power -= solar_used
        solar_stored = min(production[i] - solar_used, battery_capacity - storage,
                           battery_power) * battery_efficiency
        solar_stored_arr[i] = solar_stored
        storage += solar_stored
        solar_lost = production[i] - solar_used - solar_stored
        solar_lost_arr[i] = solar_lost
        stored_used = min(min(storage, needed_power), battery_power)
        stored_usage_arr[i] = stored_used
        storage -= stored_used
        needed_power -= stored_used
        gas_usage_arr[i] = needed_power
    return gas_usage_arr, solar_usage_arr, stored_usage_arr, solar_stored_arr, solar_lost_arr


def smart_storing_strategy(demand: DemandDf, production: ProductionDf, cost_profile: CostElectricityDf,
                           battery_capacity: float, battery_power: float) -> ElectricityUseDf:
    """
    Given a Rect cost function CostElectricityDf
    :param demand: DemandDf: pd.DataFrame(columns=[HourOfYear, 'Demand'])
    :param production: ProductionDf: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
    :param cost_profile: CostElectricityDf wrapper of pd.DataFrame with Cost and HourOfYear
    :param battery_capacity: float capacity of battery
    :param battery_power: power of the battery
    :return: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    """
    greedy_usage_df = greedy_use_strategy(demand, production, battery_capacity, battery_power).df

    needed_to_purchase = []
    pos = -2
    storage_space = 0
    for hour, price in zip(greedy_usage_df.itertuples(), cost_profile.df):
        needed_to_purchase.append(0)
        storage_space += hour[ElectricityUseDf.SolarStored] - hour[ElectricityUseDf.StoredUsage]
        if cost_profile.df['Cost']:
            needed_to_purchase[pos] += hour[ElectricityUseDf.GasUsage]
            needed_to_purchase[pos] = min(needed_to_purchase[pos] + hour[ElectricityUseDf.GasUsage], storage_space)
            pos -= 1
        else:
            pos = -2

    for i in range(len(needed_to_purchase), 0, -1):
        charge_bought = min(battery_power, needed_to_purchase[i])
        greedy_usage_df[ElectricityUseDf.GasUsage][i] += charge_bought
        greedy_usage_df[ElectricityUseDf.SolarStored][i] += charge_bought
        if charge_bought != needed_to_purchase[i]:
            needed_to_purchase[i - 1] = needed_to_purchase[i] - charge_bought


def first_selling_strategy(demand: DemandDf, production: ProductionDf, cost_profile: CostElectricityDf,
                           sell_profile: CostElectricityDf, battery_capacity: float,
                           battery_power: float) -> ElectricityUseDf:
    """
        Given a matching rect cost and sell function
        :param demand: DemandDf: pd.DataFrame(columns=[HourOfYear, 'Demand'])
        :param production: ProductionDf: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
        :param cost_profile: CostElectricityDf wrapper of pd.DataFrame with Cost and HourOfYear
        :param sell_profile: CostElectricityDf wrapper of pd.DataFrame with selling price and HourOfYear
        :param battery_capacity: float capacity of battery
        :param battery_power: power of the battery
        :return: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
        """
