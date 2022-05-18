import pandas as pd


class DataFrameWrapper:
    def __init__(self, df: pd.DataFrame):
        self.df = df


class InputDataFrameWrapper(DataFrameWrapper):
    HourOfYear = 'HourOfYear'

    def __init__(self, df: pd.DataFrame):
        DataFrameWrapper.__init__(self, df)


class SimulationResults(DataFrameWrapper):
    PowerSolar = 'PowerSolar'
    NumBatteries = 'NumBatteries'
    Cost = 'Cost'

    def __init__(self, df: pd.DataFrame):
        DataFrameWrapper.__init__(self, df)


class ElectricityUseDf(InputDataFrameWrapper):
    GasUsage = 'GasUsage'
    GasStored = 'GasStored'
    SolarUsage = 'SolarUsage'
    StoredUsage = 'StoredUsage'
    SolarStored = 'SolarStored'
    SolarLost = 'SolarLost'
    SolarSold = 'SolarSold'
    StoredSold = 'StoredSold'

    COLUMNS = [InputDataFrameWrapper.HourOfYear,
               GasUsage,
               GasStored,
               SolarUsage,
               StoredUsage,
               SolarStored,
               SolarLost,
               SolarSold,
               StoredSold]

    def __init__(self, df: pd.DataFrame):
        InputDataFrameWrapper.__init__(self, df)


class DemandDf(InputDataFrameWrapper):
    Demand = 'Demand'

    def __init__(self, df: pd.DataFrame):
        InputDataFrameWrapper.__init__(self, df)
        self.Demand = df.columns[1]


class ProductionDf(InputDataFrameWrapper):
    SolarProduction = 'SolarProduction'

    def __init__(self, df: pd.DataFrame):
        InputDataFrameWrapper.__init__(self, df)


class CostElectricityDf(InputDataFrameWrapper):
    Cost = "Cost ILS/Kwh"

    def __init__(self, df: pd.DataFrame):
        InputDataFrameWrapper.__init__(self, df)
