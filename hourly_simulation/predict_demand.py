import numpy as np
import pandas as pd
from parameters import *


def predict_demand(hourly_demand: pd.DataFrame, year_wanted: int, last_year_checked: int) -> pd.DataFrame:
    """
    Predict the growth in demand in a given year
    :param hourly_demand: pd.DataFrame(columns=['HourOfYear', 'Demand'])
    :param year_wanted: int year of the wanted output
    :param last_year_checked: the last year that the consumption checked
    :return: new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    """

    temp = hourly_demand.copy()
    temp['Demand'] = temp['Demand'].multiply(np.float_power(GROWTH_PER_YEAR, year_wanted - last_year_checked))
    return temp

