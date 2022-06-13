import copy
import typing
from typing import Tuple

import numpy as np
import pandas as pd

from df_objects.df_objects import DemandDf, ProductionDf, ElectricityUseDf, CostElectricityDf
from hourly_simulation.parameters import Params, ELECTRICITY_COST, BINARY_SELLING_COST, ELECTRICITY_SELLING_INCOME
from hourly_simulation.shift_day_in_year import shift_day_of_year


# todo: add documentation

def get_index(day_index: int, hour_index: int):
    return day_index * 24 + hour_index


def first_selling_strategy(demand: DemandDf, production: ProductionDf, param: Params, number_of_batteries,
                           predict_demand_in_year: int,
                           binary_cost_profile: CostElectricityDf = BINARY_SELLING_COST,
                           cost_profile: CostElectricityDf = ELECTRICITY_COST,
                           sell_profile: CostElectricityDf = ELECTRICITY_SELLING_INCOME) -> ElectricityUseDf:
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
    len_simulation = len(demand.df[demand.HourOfYear])
    if not len_simulation % 24 == 0:
        raise ValueError("Length of input should be a whole number of days")
    sale_max_power = param.MAX_SELLING_POWER * param.BATTERY_EFFECTIVE_SIZE
    battery_power = param.CHARGE_POWER * number_of_batteries * param.BATTERY_EFFECTIVE_SIZE
    battery_capacity = param.BATTERY_CAPACITY * number_of_batteries * param.BATTERY_EFFECTIVE_SIZE
    battery_efficiency = param.BATTERY_EFFICIENCY
    # Helpful definitions
    bin_cost = binary_cost_profile.df[binary_cost_profile.Cost].to_numpy()
    production = copy.deepcopy(production.df[production.SolarProduction].to_numpy())  # overwriting
    demand = shift_day_of_year(copy.deepcopy(demand.df[demand.Demand].to_numpy()),
                               predict_demand_in_year)  # shift demand to start on sunday
    hour_of_year = sell_profile.df[CostElectricityDf.HourOfYear] # to use later in the returned df
    cost_profile = shift_day_of_year(copy.deepcopy(cost_profile.df[cost_profile.Cost]).to_numpy(), 2018)
    sell_profile = shift_day_of_year(copy.deepcopy(sell_profile.df[sell_profile.Cost]).to_numpy(), 2018)
    # production = copy.deepcopy(production.df[production.SolarProduction].to_numpy())
    # demand = copy.deepcopy(demand.df[demand.Demand].to_numpy())
    day_use = {c: np.zeros(len(demand)) for c in ElectricityUseDf.COLUMNS}
    total_stored = 0
    # Iterating days
    for day_index in range(0, len_simulation // 24):
        # iterate expensive hours and use all the production for the demand
        expensive_hours = [i for i, x in enumerate(bin_cost[day_index * 24: (day_index + 1) * 24]) if x == 1]
        cheap_hours = [i for i, x in enumerate(bin_cost[day_index * 24: (day_index + 1) * 24]) if x == 0]
        if not len(expensive_hours) == 0:
            total_stored = day_with_expansive_hours(expensive_hours, day_index, demand, production, day_use,
                                                    sale_max_power, battery_power,
                                                    total_stored,
                                                    battery_capacity, battery_efficiency, binary_cost_profile,
                                                    cheap_hours, cost_profile,
                                                    sell_profile)
        else:
            total_stored = no_expansive_hours_day(demand, production, day_index, battery_capacity, total_stored,
                                                  sale_max_power, battery_efficiency, battery_power, day_use)
    return combine_to_df(day_use, hour_of_year)


def day_with_expansive_hours(expensive_hours, day_index, demand, production, day_use, sale_max_power,
                             battery_power, total_stored,
                             battery_capacity, battery_efficiency, binary_cost_profile, cheap_hours, cost_profile,
                             sell_profile):
    """
    @param expensive_hours: list of indexes of the expansive hours in the current day
    @param day_index: index of the current day
    @param demand: list of the demand for every hour in the year
    @param production: list of the solar production (for all the panels combined) for every hour in the year
    @param day_use: dictionary with the energy lists names as keys (solar usage, solar sold...), and the lists to fill throughout the simulation
    @param sale_max_power: maximum power to sell back to the IEC
    @param battery_power: maximum power to charge and discharge from the batteries
    @param total_stored: the total energy in the batteries, until the current day
    @param battery_capacity: the batteries' capacity (all of them combined)
    @param battery_efficiency: the ratio between the energy used for charging, to the energy charged
    @param binary_cost_profile: binary classification of all the hours in the year, to expansive and cheap hours
    @param cheap_hours: list of indexes of the cheap hours in the current day
    @param cost_profile: list of the buying cost per kwh for each hour in the year
    @param sell_profile: list of the selling cost per kwh for each hour in the year
    @return: total_stored: updated total stored, after current day
    """
    expansive_completion, expansive_use_completion = (0, 0)
    expansive_completion, expansive_use_completion = get_affective_expansive_demand(expensive_hours, day_index,
                                                                                    demand, production, day_use,
                                                                                    sale_max_power,
                                                                                    expansive_completion,
                                                                                    battery_power,
                                                                                    expansive_use_completion)
    total_stored = store_overproduction_to_fill_battery(expensive_hours, total_stored, battery_capacity,
                                                        day_index, demand, production, battery_efficiency,
                                                        battery_power, day_use)
    if get_is_buying_profitable(battery_efficiency, binary_cost_profile, get_index(day_index, cheap_hours[0]),
                                get_index(day_index, expensive_hours[0]), cost_profile, sell_profile):
        total_stored = buy_in_cheap_hours(battery_capacity, expansive_completion, cheap_hours, total_stored,
                                          day_index,
                                          battery_power, day_use, sell_profile, cost_profile)
    total_stored = fill_expansive_hours(expensive_hours, day_index, demand, battery_power, day_use,
                                        total_stored, expansive_use_completion, sale_max_power, sell_profile)
    fill_cheap_hours(cheap_hours, day_index, production, demand, sale_max_power, day_use)
    return total_stored


def get_affective_expansive_demand(expensive_hours, day_index, demand, production, day_use, sale_max_power,
                                   expansive_completion, battery_power, expansive_use_completion):
    """

    @param expensive_hours: list of indexes of the expansive hours in the current day
    @param day_index: index of the current day
    @param demand: list of the demand for every hour in the year
    @param production: list of the solar production (for all the panels combined) for every hour in the year
    @param day_use: dictionary with the energy lists names as keys (solar usage, solar sold...), and the lists to fill throughout the simulation
    @param sale_max_power: maximum power to sell back to the IEC
    @param expansive_completion: amount of kwh to fill in cheap hours to cover the demand and selling in expansive hours
    @param battery_power:
    @param expansive_use_completion: amount of kwh to fill in cheap hours to cover only the selling in expansive hours
    @return: updated expansive_completion and expansive_use_completion
    """
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
    return expansive_completion, expansive_use_completion


def store_overproduction_to_fill_battery(expensive_hours, total_stored, battery_capacity, day_index, demand, production,
                                         battery_efficiency, battery_power, day_use):
    """

    @param expensive_hours: list of indexes of the expansive hours in the current day
    @param total_stored: the total energy in the batteries, until the current day
    @param battery_capacity: the batteries' capacity (all of them combined)
    @param day_index: index of the current day
    @param demand: list of the demand for every hour in the year
    @param production: list of the solar production (for all the panels combined) for every hour in the year
    @param battery_efficiency: the ratio between the energy used for charging, to the energy charged
    @param battery_power: maximum power to charge and discharge from the batteries
    @param day_use: dictionary with the energy lists names as keys (solar usage, solar sold...), and the lists to fill throughout the simulation
    @return: total_stored: updated total stored, after filling overproduction
    """
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
        production[i] = production[i] - storing
    return total_stored


def buy_in_cheap_hours(battery_capacity, expansive_completion, cheap_hours, total_stored, day_index, battery_power,
                       day_use, sell_profile, cost_profile):
    """

    @param battery_capacity: the batteries' capacity (all of them combined)
    @param expansive_completion: amount of kwh to fill in cheap hours to cover the demand and selling in expansive hours
    @param cheap_hours: list of indexes of the cheap hours in the current day
    @param total_stored: the total energy in the batteries, until the current day
    @param day_index: index of the current day
    @param battery_power: maximum power to charge and discharge from the batteries
    @param day_use: dictionary with the energy lists names as keys (solar usage, solar sold...), and the lists to fill throughout the simulation
    @param sell_profile: list of the selling cost per kwh for each hour in the year
    @param cost_profile: list of the buying cost per kwh for each hour in the year
    @return: total_stored: updated total stored, after buying in cheap hours
    """
    effective_battery_capacity = min(battery_capacity, expansive_completion)
    for i in ordered_cheap_hours(cheap_hours, cost_profile, day_index):
        # print(f"energy bought in hour {i}", end=" ")
        # i = get_index(day_index, hour_index)
        if total_stored >= effective_battery_capacity:
            break
        # i = get_index(day_index, hour_index)
        solar_buy = min(battery_power - day_use[ElectricityUseDf.SolarStored][i], effective_battery_capacity
                        - total_stored)
        total_stored += solar_buy
        day_use[ElectricityUseDf.GasStored][i] = solar_buy
    return total_stored


def fill_expansive_hours(expensive_hours, day_index, demand, battery_power, day_use, total_stored,
                         expansive_use_completion, sale_max_power, sell_profile):
    expansive_sell_completion = total_stored - expansive_use_completion
    for i in ordered_hours(expensive_hours, sell_profile, day_index):
        # i = get_index(day_index, hour_index)
        stored_used = min(demand[i], battery_power, total_stored)
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
    return total_stored


def fill_cheap_hours(cheap_hours, day_index, production, demand, sale_max_power, day_use):
    for hour_index in cheap_hours:
        i = get_index(day_index, hour_index)
        solar_used = min(production[i], demand[i])
        day_use[ElectricityUseDf.SolarUsage][i] = solar_used
        solar_sold = min(production[i] - solar_used, sale_max_power)
        day_use[ElectricityUseDf.SolarSold][i] = solar_sold
        day_use[ElectricityUseDf.SolarLost][i] += production[i] - solar_used - solar_sold
        day_use[ElectricityUseDf.GasUsage][i] = demand[i] - solar_used


def no_expansive_hours_day(demand, production, day_index, battery_capacity, total_stored, sale_max_power,
                           battery_efficiency, battery_power, day_use):
    for i in range(day_index * 24, (day_index + 1) * 24):
        needed_power = demand[i]
        solar_used = min(production[i], needed_power)
        day_use[ElectricityUseDf.SolarUsage][i] = solar_used
        needed_power -= solar_used
        solar_stored_natural = min(production[i] - solar_used, (battery_capacity - total_stored) / battery_efficiency,
                                   battery_power / battery_efficiency)
        day_use[ElectricityUseDf.SolarStored][i] = solar_stored_natural * battery_efficiency
        total_stored += solar_stored_natural * battery_efficiency
        # energy lost when charging the battery
        solar_stored_lost = solar_stored_natural * (1 - battery_efficiency)
        solar_sold = min(production[i] - solar_used - solar_stored_natural, sale_max_power)
        day_use[ElectricityUseDf.SolarSold][i] = solar_sold
        solar_lost = production[i] + solar_stored_lost - solar_used - solar_stored_natural - solar_sold
        day_use[ElectricityUseDf.SolarLost][i] = solar_lost
        stored_used = min(total_stored, needed_power, battery_power)
        day_use[ElectricityUseDf.StoredUsage][i] = stored_used
        total_stored -= stored_used
        needed_power -= stored_used
        day_use[ElectricityUseDf.GasUsage][i] = needed_power
    return total_stored


def get_is_buying_profitable(battery_efficiency, binary_cost_profile, low_index, peak_index, cost_profile,
                             sell_profile):
    low_buy_price = cost_profile[low_index]
    peak_sell_price = sell_profile[peak_index]
    return low_buy_price < peak_sell_price * battery_efficiency


def combine_to_df(day_use, hour_of_year):
    hourly_use = ElectricityUseDf(pd.DataFrame())
    hourly_use.df[hourly_use.GasUsage] = day_use[ElectricityUseDf.GasUsage]
    hourly_use.df[hourly_use.SolarUsage] = day_use[ElectricityUseDf.SolarUsage]
    hourly_use.df[hourly_use.StoredUsage] = day_use[ElectricityUseDf.StoredUsage]
    hourly_use.df[hourly_use.SolarStored] = day_use[ElectricityUseDf.SolarStored]
    hourly_use.df[hourly_use.SolarLost] = round_array(day_use[ElectricityUseDf.SolarLost], 6)
    hourly_use.df[hourly_use.SolarSold] = day_use[ElectricityUseDf.SolarSold]
    hourly_use.df[hourly_use.StoredSold] = day_use[ElectricityUseDf.StoredSold]
    hourly_use.df[hourly_use.GasStored] = day_use[ElectricityUseDf.GasStored]
    hourly_use.df[hourly_use.HourOfYear] = hour_of_year
    return hourly_use


def ordered_hours(hours, sell_profile, day_index, reverse=True):
    daily_sell_profile = [sell_profile[get_index(day_index, i)] for i in hours]
    # print(f"day = {day_index}, unordered indices = {hours}", end="   ")
    # print(f"ordered indices = {[val for _, val in sorted(zip(daily_sell_profile, hours))]}")
    ordered_hours_array = [val for _, val in sorted(zip(daily_sell_profile, hours), reverse=reverse)]
    # print(f"in day {day_index} daily sell profile = {daily_sell_profile},\n hours are = {hours} \n and sorted hours = {[get_index(day_index, i) for i in ordered_hours_array]}")
    return [get_index(day_index, i) for i in ordered_hours_array]
    # return [get_index(day_index, i) for i in hours]


def ordered_cheap_hours(hours, cost_profile, day_index, threshold_day=20):
    early_hours = [i for i in hours if i < threshold_day]  # to buy before the expansive hours
    return ordered_hours(early_hours, cost_profile, day_index, reverse=False)
    # return hours


def round_array(arr, decimal):
    new_arr = copy.deepcopy(arr)
    # print(new_arr)
    for i in range(len(new_arr)):
        if 0 < abs(new_arr[i]) < 10 ^ (-decimal):
            # print(f"index {i} is negative and equals to {arr[i]}")
            new_arr[i] = 0

    return new_arr
