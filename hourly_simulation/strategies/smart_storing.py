import pandas as pd

from df_objects.df_objects import DemandDf, ProductionDf, ElectricityUseDf, CostElectricityDf
from hourly_simulation.parameters import Params

from hourly_simulation.strategies import greedy_strategy


def smart_storing_strategy(demand: DemandDf, production: ProductionDf, params: Params,
                        num_batteries: float, predict_demand_in_year: int) -> ElectricityUseDf:
    """
    This is an implementation of the smart storing strategy - saving up just enough energy in batteries during cheap
    electricity hours to then use it during the expensive hours (only if we use gas-power during those hours), in order
    to be as cost-efficient as the panels & batteries allow us to be.

    :param demand: DemandDf: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param production: ProductionDf: pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param num_batteries: float number of batteries to simulate
    :param params: named tuple of parameters from parameters.csv
    :return: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage', 'StoredUsage',
                'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    """
    greedy_usage_df = greedy_strategy.greedy_use_strategy(demand, production, params, num_batteries, predict_demand_in_year).df
    binary_cost_df = CostElectricityDf(pd.read_csv(r'data/electricity_cost_binary.csv', index_col=0)).df
    battery_power = params.CHARGE_POWER
    needed_to_purchase = []
    pos = -2
    storage_space = num_batteries * params.BATTERY_CAPACITY

    # creates a list (needed_to_purchase) that on every index corresponding to an hour before the expensive electricity hours, the amount of additional electricity that should be stored in the batteries before the expensive hours is saved (on top of greedy_stratedy).
    for hour, price in zip(greedy_usage_df.itertuples(), binary_cost_df.itertuples()):
        needed_to_purchase.append(0)
        storage_space += getattr(hour, ElectricityUseDf.StoredUsage) - getattr(hour, ElectricityUseDf.SolarStored)

        if getattr(price, CostElectricityDf.Cost) and getattr(hour, CostElectricityDf.HourOfYear) > 1:
            needed_to_purchase[pos] += min(getattr(hour, ElectricityUseDf.GasUsage), battery_power)
            needed_to_purchase[pos] = min(needed_to_purchase[pos], storage_space)
            pos -= 1
        else:
            pos = -2

    # modifies greedy_usage_df, changes GasUsage and StoredUsage for the expensive hours.
    used_purchased = 0
    for hour, purchased in zip(greedy_usage_df.itertuples(), needed_to_purchase):
        used_purchased += purchased
        hourly_usage = min(used_purchased, battery_power, getattr(hour, ElectricityUseDf.GasUsage))
        used_purchased -= hourly_usage

        greedy_usage_df.at[getattr(hour, 'Index'), ElectricityUseDf.GasUsage] -= hourly_usage
        greedy_usage_df.at[getattr(hour, 'Index'), ElectricityUseDf.StoredUsage] += hourly_usage

    # modifies greedy_usage_df, changes GasStored for before the expensive hours.
    for i in range(len(needed_to_purchase) - 1, 0, -1):
        charge_bought = min(battery_power, needed_to_purchase[i])
        greedy_usage_df.at[i, ElectricityUseDf.GasStored] += charge_bought
        if charge_bought != needed_to_purchase[i]:
            needed_to_purchase[i - 1] = needed_to_purchase[i] - charge_bought

    return ElectricityUseDf(greedy_usage_df)
