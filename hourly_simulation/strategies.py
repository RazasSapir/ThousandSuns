import pandas as pd
import typing


def greedy_use_strategy(demand: pd.DataFrame, production: pd.DataFrame, battery_storage: int) -> pd.DataFrame:
    """
    This is the implementation of the greedy use strategy - using the solar stored whenever possible
    :param demand: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param production: pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param battery_storage: int size of battery
    :return: pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    """
    hourly_use = pd.DataFrame(columns=['GasUsage', 'SunUsage', 'StoredUsage', 'SunStored', 'SunLost'])
    # TODO: implement
    return hourly_use
