from df_objects.df_objects import DemandDf, ProductionDf, ElectricityUseDf, CostElectricityDf
from hourly_simulation.strategies import greedy_strategy


def smart_storing_strategy(demand: DemandDf, production: ProductionDf, cost_profile: CostElectricityDf,
                           battery_capacity: float, battery_power: float) -> ElectricityUseDf:
    """
    Given a Rect cost function CostElectricityDf
    :param demand: DemandDf: pd.DataFrame(columns=[HourOfYear, 'Demand'])
    :param production: ProductionDf: pd.DataFrame(columns=[HourOfYear, 'SolarProduction'])
    :param cost_profile: CostElectricityDf wrapper of pd.DataFrame with Cost and HourOfYear
    :param battery_capacity: float capacity of battery
    :param battery_power: power of the battery
    :return: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    """
    greedy_usage_df = greedy_strategy.greedy_use_strategy(demand, production, battery_capacity, battery_power).df

    needed_to_purchase = []
    pos = -2
    storage_space = 0
    for hour, price in zip(greedy_usage_df.itertuples(), cost_profile.df):
        needed_to_purchase.append(0)
        storage_space += hour[ElectricityUseDf.SolarStored] - hour[ElectricityUseDf.StoredUsage]
        if cost_profile.df['Cost']:
            needed_to_purchase[pos] += hour[ElectricityUseDf.GasUsage]
            needed_to_purchase[pos] = min(needed_to_purchase[pos] + hour[ElectricityUseDf.GasUsage], storage_space)
            pos -= 1
        else:
            pos = -2

    for i in range(len(needed_to_purchase), 0, -1):
        charge_bought = min(battery_power, needed_to_purchase[i])
        greedy_usage_df[ElectricityUseDf.GasUsage][i] += charge_bought
        greedy_usage_df[ElectricityUseDf.SolarStored][i] += charge_bought
        if charge_bought != needed_to_purchase[i]:
            needed_to_purchase[i - 1] = needed_to_purchase[i] - charge_bought
