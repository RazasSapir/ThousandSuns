import pandas as pd


def greedy_use_strategy(demand: pd.DataFrame, production: pd.DataFrame, battery_storage: int) -> pd.DataFrame:
    """
    This is the implementation of the greedy use strategy - using the solar stored whenever possible
    :param demand: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param production: pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param battery_storage: int size of battery
    :return: pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    """
    hourly_use = pd.DataFrame(columns=['GasUsage', 'SunUsage', 'StoredUsage', 'SunStored', 'SunLost'])
    storage = 0
    next_hour = {'GasUsage': 0, 'SunUsage': 0, 'StoredUsage': 0, 'SunStored': 0, 'SunLost': 0}
    electricity_data = pd.merge(demand, production, on="HourOfYear")
    for row in electricity_data.itertuples():
        if storage > 0:
            next_hour["StoredUsage"] = min(storage, row.Demand)
            storage -= min(storage, row.Demand)
            row.Demand -= min(storage, row.Demand)
        else:
            next_hour["StoredUsage"] = 0
        if row.SolarProduction >= row.Demand:
            next_hour["GasUsage"] = 0
            next_hour["SunUsage"] = row.Demand
            next_hour["SunStored"] = max(row.SolarProduction - row.Demand, battery_storage - storage)
            next_hour["SunLost"] = row.SolarProduction - row.Demand - next_hour["SunStored"]
        else:
            next_hour["GasUsage"] = row.Demand - row.SolarProduction
            next_hour["SunUsage"] = row.SolarProduction
            next_hour["SunStored"] = 0
            next_hour["SunLost"] = 0
        storage = next_hour["SunStored"]
        hourly_use = hourly_use.append(next_hour, ignore_index=True)
    return hourly_use
