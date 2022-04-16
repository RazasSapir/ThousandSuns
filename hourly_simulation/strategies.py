from df_objects.df_objects import *


def greedy_use_strategy(demand: DemandDf, production: ProductionDf, battery_capacity: int) -> ElectricityUseDf:
    """
    Deprecated: not useful.
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


def better_use_strategy(demand: DemandDf, production: ProductionDf, battery_capacity: float,
                        battery_power: float) -> ElectricityUseDf:
    """
    This is the implementation of the better use strategy - using the solar produced whenever possible,
    then the stored energy and only then using gas power
    note: this would be the perfect strategy if the price for gas power would be the same during all hours
    :param demand: pd.DataFrame(columns=[HourOfYear, 'Demand'])
    :param production: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
    :param battery_capacity: float capacity of battery
    :param battery_power: power of the battery
    :return: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    """
    storage = 0
    next_hour = {ElectricityUseDf.GasUsage: [], ElectricityUseDf.SolarUsage: [], ElectricityUseDf.StoredUsage: [],
                 ElectricityUseDf.SolarStored: [], ElectricityUseDf.SolarLost: []}
    electricity_data = pd.merge(demand.df, production.df, on=ElectricityUseDf.HourOfYear)
    for row in electricity_data.itertuples():
        needed_power = row.Demand

        solar_used = min(row.SolarProduction, needed_power)
        next_hour[ElectricityUseDf.SolarUsage].append(solar_used)
        needed_power -= solar_used

        solar_stored = min(min(row.SolarProduction - solar_used, battery_capacity - storage), battery_power)
        next_hour[ElectricityUseDf.SolarStored].append(solar_stored)
        storage += solar_stored

        solar_lost = row.SolarProduction - solar_used - solar_stored
        next_hour[ElectricityUseDf.SolarLost].append(solar_lost)

        stored_used = min(min(storage, needed_power), battery_power)
        next_hour[ElectricityUseDf.StoredUsage].append(stored_used)
        storage -= stored_used
        needed_power -= stored_used

        next_hour[ElectricityUseDf.GasUsage].append(needed_power)

    hourly_use = ElectricityUseDf(pd.DataFrame.from_dict(next_hour))
    hourly_use.df[ElectricityUseDf.HourOfYear] = electricity_data[ElectricityUseDf.HourOfYear]
    return hourly_use
