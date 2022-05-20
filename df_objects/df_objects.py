import pandas as pd


class DataFrameWrapper:
    """
    DataFrameWrapper Object that hold data frames, isn't used directly, but inherited.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df


class InputDataFrameWrapper(DataFrameWrapper):
    """
    InputDataFrameWrapper object that hold "simulation input" pd.DataFrames all with 'HourOfYear' column
    """
    HourOfYear = 'HourOfYear'

    def __init__(self, df: pd.DataFrame):
        DataFrameWrapper.__init__(self, df)


class SimulationResults(DataFrameWrapper):
    """
    SimulationResults object that hold pd.DataFrame of 'Find Optimum' simulation results
    """
    PowerSolar = 'PowerSolar'
    NumBatteries = 'NumBatteries'
    Cost = 'Cost'

    def __init__(self, df: pd.DataFrame):
        DataFrameWrapper.__init__(self, df)


class ElectricityUseDf(InputDataFrameWrapper):
    """
    ElectricityUseDf object that hold pd.DataFrame of  the results of the use strategy
    """
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
    """
    DemandDf object that hold pd.DataFrame of the electricity comsumption demand
    """
    Demand = 'Demand'

    def __init__(self, df: pd.DataFrame):
        InputDataFrameWrapper.__init__(self, df)
        self.Demand = df.columns[1]


class ProductionDf(InputDataFrameWrapper):
    """
    ProductionDf object that hold pd.DataFrame of the PV solar production
    """
    SolarProduction = 'SolarProduction'

    def __init__(self, df: pd.DataFrame):
        InputDataFrameWrapper.__init__(self, df)


class CostElectricityDf(InputDataFrameWrapper):
    """
    ProductionDf object that hold pd.DataFrame of the Electricity cost (buying and selling)
    """
    Cost = "Cost ILS/Kwh"

    def __init__(self, df: pd.DataFrame):
        InputDataFrameWrapper.__init__(self, df)
