import pandas as pd
from hourly_simulation.parameters import *

from hourly_simulation.constants import *


def greedy_use_strategy(demand: pd.DataFrame, production: pd.DataFrame, battery_capacity: int) -> pd.DataFrame:
    """
    This is the implementation of the greedy use strategy - using the solar stored whenever possible
    :param demand: pd.DataFrame(columns=[HourOfYear, 'Demand'])
    :param production: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
    :param battery_capacity: int size of battery
    :return: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    """
    current_battery_capacity = 0
    next_hour = {GasUsage: [], SolarUsage: [], StoredUsage: [], SolarStored: [], SolarLost: []}
    electricity_data = pd.merge(demand, production, on=HourOfYear)
    for row in electricity_data.itertuples():
        needed_power = row.Demand
        # Handle Early Stored Energy
        if current_battery_capacity > 0:
            stored_used = min(current_battery_capacity, needed_power)
            next_hour[StoredUsage].append(stored_used)
            needed_power -= stored_used
            current_battery_capacity -= stored_used
        else:
            next_hour[StoredUsage].append(0)
        # Handle Produced Energy
        if row.SolarProduction >= needed_power:
            next_hour[GasUsage].append(0)
            next_hour[SolarUsage].append(needed_power)
            solar_stored = min(row.SolarProduction - needed_power, battery_capacity - current_battery_capacity)
            next_hour[SolarStored].append(solar_stored)
            next_hour[SolarLost].append(max(row.SolarProduction - needed_power - solar_stored, 0))
        else:
            next_hour[GasUsage].append(needed_power - row.SolarProduction)
            next_hour[SolarUsage].append(row.SolarProduction)
            next_hour[SolarStored].append(0)
            next_hour[SolarLost].append(0)
        current_battery_capacity += next_hour[SolarStored][-1]
    hourly_use = pd.DataFrame.from_dict(next_hour)
    hourly_use[HourOfYear] = electricity_data[HourOfYear]
    return hourly_use


def better_use_strategy(demand: pd.DataFrame, production: pd.DataFrame, battery_storage: int) -> pd.DataFrame:
    """
    This is the implementation of the better use strategy - using the solar produced whenever possible,
    then the stored energy and only then using gas power
    note: this would be the perfect strategy if the price for gas power would be the same during all hours
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

        solar_used = min(row.SolarProduction, needed_power)
        next_hour[SolarUsage].append(solar_used)
        needed_power -= solar_used

        solar_stored = min(min(row.SolarProduction - solar_used, battery_storage - storage), CHARGE_POWER_MAGIC_NUMBER)
        next_hour[SolarStored].append(solar_stored)
        storage += solar_stored

        solar_lost = row.SolarProduction - solar_used - solar_stored
        next_hour[SolarLost].append(solar_lost)

        stored_used = min(storage, needed_power)
        next_hour[StoredUsage].append(stored_used)
        storage -= stored_used
        needed_power -= stored_used

        next_hour[GasUsage].append(needed_power)

    hourly_use = pd.DataFrame.from_dict(next_hour)
    hourly_use[HourOfYear] = electricity_data[HourOfYear]
    return hourly_use
