import copy

import numpy as np
import pandas as pd

from df_objects.df_objects import DemandDf, ProductionDf, ElectricityUseDf
from hourly_simulation.parameters import Params
from hourly_simulation.shift_day_in_year import shift_day_of_year


def greedy_use_strategy(demand: DemandDf, production: ProductionDf, params: Params,
                        num_batteries: float, predict_demand_in_year: int) -> ElectricityUseDf:
    """
    This is the implementation of the greedy use strategy - using the solar produced whenever possible,
    then the stored energy and only then using gas power. This Strategy does not include selling electricity
    note: this would be the perfect strategy if the price for gas power would be the same during all hours.

    :param demand: DemandDf: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param production: ProductionDf: pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param num_batteries: float number of batteries to simulate
    :param params: named tuple of parameters from parameters.csv
    :return: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage', 'StoredUsage',
                'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    """
    demand_shifted = shift_day_of_year(copy.deepcopy(demand.df[demand.Demand].to_numpy()),
                                       predict_demand_in_year)  # shift demand to start on sunday
    gas_usage_arr, solar_usage_arr, stored_usage_arr, solar_stored_arr, solar_lost_arr = __greedy_use_loop(
        num_batteries * params.BATTERY_CAPACITY * params.BATTERY_EFFECTIVE_SIZE,
        num_batteries * params.CHARGE_POWER,
        params.BATTERY_EFFICIENCY,
        demand_shifted,
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
    hourly_use.df[ElectricityUseDf.GasStored] = 0
    return hourly_use


def __greedy_use_loop(battery_capacity_kwh: float, battery_power_kw: float, battery_efficiency: float, demand,
                      production):
    """
    Helper function for the greedy_use_strategy using faster jit

    :param battery_capacity_kwh: float Battery Capacity [Kwh]
    :param battery_power_kw: float battery max charging/discharging power limit [Kw]
    :param battery_efficiency: float ratio of (Kwh available to discharge / Kwh charged)
    :param demand: np array of DemandDf.df['Demand']
    :param production: np array of ProductionDf.df['SolarProduction']
    :return: Tuple of Five np.Array for each relevant colum in ElectricityUseDf: 'GasUsage', 'SolarUsage',
            'StoredUsage', 'SolarStored', 'SolarLost',
    """
    storage: float = 0
    # define useful structures
    len_simulation = len(demand)
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
        solar_stored = min(production[i] - solar_used, battery_capacity_kwh - storage,
                           battery_power_kw) * battery_efficiency
        solar_stored_arr[i] = solar_stored
        storage += solar_stored
        solar_lost = production[i] - solar_used - solar_stored
        solar_lost_arr[i] = solar_lost
        stored_used = min(min(storage, needed_power), battery_power_kw)
        stored_usage_arr[i] = stored_used
        storage -= stored_used
        needed_power -= stored_used
        gas_usage_arr[i] = needed_power
    return gas_usage_arr, solar_usage_arr, stored_usage_arr, solar_stored_arr, solar_lost_arr
