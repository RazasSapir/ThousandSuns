from typing import Tuple, Callable

import pandas as pd

from parameters import *


# todo: add units to parameters

def get_solar_production_profile(single_solar_profile: pd.DataFrame, num_solar_panels: int) -> pd.DataFrame:
    """
    :param single_solar_profile: single solar hourly production pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param num_solar_panels: int number of solar panels
    :return: total production of solar panels pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    pass


def calculate_cost(electricity_usage: pd.DataFrame, battery_capacity: float, num_solar_panels: int,
                   time_span: float) -> float:
    """

    :param time_span: the time of the run
    :param num_solar_panels: int number of solar panels
    :param battery_capacity: float capacity of batteries in Kwh
    :param electricity_usage: pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    :return: float cost of the given electricity usage
    """
    gas_usage = electricity_usage.loc[:, "GasUsage"]
    gas_cost_per_hour = ELECTRICITY_COST.loc[:, "Cost ILS/Kwh"]
    total_gas_cost = gas_usage.dot(gas_cost_per_hour)
    total_solar_opex = num_solar_panels * SOLAR_PANEL_AREA_DUNAM * SOLAR_KWH_PER_DUNAM * SOLAR_OPEX
    total_solar_capex = num_solar_panels * SOLAR_PANEL_AREA_DUNAM * SOLAR_KWH_PER_DUNAM * SOLAR_CAPEX / time_span
    total_battery_opex = battery_capacity * BATTERY_OPEX
    total_battery_capex = battery_capacity * BATTERY_CAPEX / time_span
    return total_gas_cost + total_solar_opex + total_solar_capex + total_battery_opex + total_battery_capex


def calculate_pollution(electricity_usage: pd.DataFrame):
    """
    Calculate the total pollution created by the gas in the given year.
    :param electricity_usage: pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    :return: float pollution in units? # todo: define the wanted units
    """
    pass


def simulate_use(demand: pd.DataFrame, num_solar_panels: int, battery_storage: float, strategy: Callable, year: int) -> \
Tuple[
    float, float]:
    """
    simulate the usages based of demand. number of solar panels and number of panels.
    :param num_solar_panels: int number of solar panels
    :param demand: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param battery_storage: float size of battery
    :param strategy: function responsible for handling the cost
    :return: (total_cost, total_pollution)
    """
    pass
