from numba import jit

from df_objects.df_objects import *


@jit(nopython=True)
def greedy_use_strategy(demand: DemandDf, production: ProductionDf, battery_capacity: int) -> ElectricityUseDf:
    """
    This is the implementation of the greedy use strategy - using the solar stored whenever possible
    :param demand: DemandDf: pd.DataFrame(columns=[HourOfYear, 'Demand'])
    :param production: ProductionDf: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
    :param battery_capacity: int size of battery
    :return: ElectricityUseDf: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    """
    current_battery_capacity = 0
    next_hour = {ElectricityUseDf.GasUsage: [], ElectricityUseDf.SolarUsage: [], ElectricityUseDf.StoredUsage: [],
                 ElectricityUseDf.SolarStored: [], ElectricityUseDf.SolarLost: []}
    electricity_data = pd.merge(demand.df, production.df, on=ElectricityUseDf.HourOfYear)
    for row in electricity_data.itertuples():
        needed_power = row.Demand
        # Handle Early Stored Energy
        if current_battery_capacity > 0:
            stored_used = min(current_battery_capacity, needed_power)
            next_hour[ElectricityUseDf.StoredUsage].append(stored_used)
            needed_power -= stored_used
            current_battery_capacity -= stored_used
        else:
            next_hour[ElectricityUseDf.StoredUsage].append(0)
        # Handle Produced Energy
        if row.SolarProduction >= needed_power:
            next_hour[ElectricityUseDf.GasUsage].append(0)
            next_hour[ElectricityUseDf.SolarUsage].append(needed_power)
            solar_stored = min(row.SolarProduction - needed_power, battery_capacity - current_battery_capacity)
            next_hour[ElectricityUseDf.SolarStored].append(solar_stored)
            next_hour[ElectricityUseDf.SolarLost].append(max(row.SolarProduction - needed_power - solar_stored, 0))
        else:
            next_hour[ElectricityUseDf.GasUsage].append(needed_power - row.SolarProduction)
            next_hour[ElectricityUseDf.SolarUsage].append(row.SolarProduction)
            next_hour[ElectricityUseDf.SolarStored].append(0)
            next_hour[ElectricityUseDf.SolarLost].append(0)
        current_battery_capacity += next_hour[ElectricityUseDf.SolarStored][-1]
    hourly_use = pd.DataFrame.from_dict(next_hour)
    hourly_use[ElectricityUseDf.HourOfYear] = electricity_data[ElectricityUseDf.HourOfYear]
    return ElectricityUseDf(hourly_use)
