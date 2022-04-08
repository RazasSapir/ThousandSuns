import pandas as pd


def greedy_use_strategy(demand: pd.DataFrame, production: pd.DataFrame, battery_storage: int) -> pd.DataFrame:
    """
    This is the implementation of the greedy use strategy - using the solar stored whenever possible
    :param demand: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param production: pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param battery_storage: int size of battery
    :return: pd.DataFrame(columns=['DayOfYear', 'GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    """
    hourly_use = pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    storage = 0
    next_hour = {'HourOfYear': 0, 'GasUsage': 0, 'SolarUsage': 0, 'StoredUsage': 0, 'SolarStored': 0, 'SolarLost': 0}
    electricity_data = pd.merge(demand, production, on="HourOfYear")
    for row in electricity_data.itertuples():
        next_hour['HourOfYear'] = row.HourOfYear
        needed_power = row.Demand
        if storage > 0:
            next_hour["StoredUsage"] = min(storage, needed_power)
            needed_power -= next_hour["StoredUsage"]
            storage -= next_hour["StoredUsage"]
        else:
            next_hour["StoredUsage"] = 0
        if row.SolarProduction >= needed_power:
            next_hour["GasUsage"] = 0
            next_hour["SolarUsage"] = needed_power
            next_hour["SolarStored"] = min(row.SolarProduction - needed_power, battery_storage - storage)
            next_hour["SolarLost"] = max(row.SolarProduction - needed_power - next_hour["SolarStored"], 0)
        else:
            next_hour["GasUsage"] = needed_power - row.SolarProduction
            next_hour["SolarUsage"] = row.SolarProduction
            next_hour["SolarStored"] = 0
            next_hour["SolarLost"] = 0
        storage = next_hour["SolarStored"]
        hourly_use = hourly_use.append(next_hour, ignore_index=True)
    return hourly_use
