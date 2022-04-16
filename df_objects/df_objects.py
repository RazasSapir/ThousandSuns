import pandas as pd


class DataFrameWrapper:
    HourOfYear = 'HourOfYear'

    def __init__(self, df: pd.DataFrame):
        self.df = df


class ElectricityUseDf(DataFrameWrapper):
    GasUsage = 'GasUsage'
    SolarUsage = 'SolarUsage'
    StoredUsage = 'StoredUsage'
    SolarStored = 'SolarStored'
    SolarLost = 'SolarLost'

    def __init__(self, inner_df: pd.DataFrame):
        DataFrameWrapper.__init__(self, inner_df)


class DemandDf(DataFrameWrapper):
    Demand = 'Demand'

    def __init__(self, inner_df: pd.DataFrame):
        DataFrameWrapper.__init__(self, inner_df)
        self.Demand = inner_df.columns[1]


class ProductionDf(DataFrameWrapper):
    SolarProduction = 'SolarProduction'

    def __init__(self, inner_df: pd.DataFrame):
        DataFrameWrapper.__init__(self, inner_df)


class CostElectricityDf(DataFrameWrapper):
    Cost = "Cost ILS/Kwh"

    def __init__(self, inner_df: pd.DataFrame):
        DataFrameWrapper.__init__(self, inner_df)
