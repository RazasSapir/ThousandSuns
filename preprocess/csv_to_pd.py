import pandas as pd


def get_demand(demand_path: str) -> pd.DataFrame:
    """
    Open csv as DataFrame and preprocess the data
    :param demand_path: relative path to total yearly demand
    :return: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    """
    pass


def get_production(single_solar_production_path: str) -> pd.DataFrame:
    """
    Open csv as DataFrame and preprocess the data
    :param single_solar_production_path: relative path to single solar panel path
    :return: pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    pass
