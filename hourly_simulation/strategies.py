import pandas as pd

from constants import *


def greedy_use_strategy(demand: pd.DataFrame, production: pd.DataFrame, battery_storage: int) -> pd.DataFrame:
    """
    This is the implementation of the greedy use strategy - using the solar stored whenever possible
    :param demand: pd.DataFrame(columns=[HourOfYear, 'Demand'])
    :param production: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
    :param battery_storage: int size of battery
    :return: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    """
    storage = 0
    next_hour = {GasUsage: [], SolarUsage: [], StoredUsage: [], SolarStored: [], SolarLost: []}
    electricity_data = pd.merge(demand, production, on=HourOfYear)
    for row in electricity_data.itertuples():
        needed_power = row.Demand
        if storage > 0:
            stored_used = min(storage, needed_power)
            next_hour[StoredUsage].append(stored_used)
            needed_power -= stored_used
            storage -= stored_used
        else:
            next_hour[StoredUsage].append(0)
        if row.SolarProduction >= needed_power:
            next_hour[GasUsage].append(0)
            next_hour[SolarUsage].append(needed_power)
            solar_stored = min(row.SolarProduction - needed_power, battery_storage - storage)
            next_hour[SolarStored].append(solar_stored)
            next_hour[SolarLost].append(max(row.SolarProduction - needed_power - solar_stored, 0))
        else:
            next_hour[GasUsage].append(needed_power - row.SolarProduction)
            next_hour[SolarUsage].append(row.SolarProduction)
            next_hour[SolarStored].append(0)
            next_hour[SolarLost].append(0)
        storage = next_hour[SolarStored][-1]
    hourly_use = pd.DataFrame.from_dict(next_hour)
    hourly_use[HourOfYear] = electricity_data[HourOfYear]
    return hourly_use
