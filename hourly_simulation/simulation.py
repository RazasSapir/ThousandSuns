from typing import Tuple, Callable

import pandas as pd


def get_solar_production_profile(single_solar_profile: pd.DataFrame, num_solar_panels: int) -> pd.DataFrame:
    """
    :param single_solar_profile: single solar hourly production pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param num_solar_panels: int number of solar panels
    :return: total production of solar panels pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    pass


def calculate_cost(electricity_usage: pd.DataFrame, battery_size: float, num_solar_panels: int) -> float:
    """

    :param num_solar_panels: int number of solar panels
    :param battery_size: float size of batteries
    :param electricity_usage: pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    :return: float cost of the given electricity usage
    """
    pass


def simulate_use(demand: pd.DataFrame, num_solar_panels: int, battery_storage: float, strategy: Callable, year: int) -> Tuple[
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
