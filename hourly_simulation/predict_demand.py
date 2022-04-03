import pandas as pd


def predict_demand(hourly_demand: pd.DataFrame, year_of_data: int, year_wanted: int) -> pd.DataFrame:
    """
    Predict the growth in demand in a given year
    :param hourly_demand: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param year_of_data: int year of the given input
    :param year_wanted: int year of the wanted output
    :return: new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    """