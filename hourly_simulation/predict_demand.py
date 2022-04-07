import pandas as pd


def predict_demand_in_year(hourly_demand: pd.DataFrame, year_wanted: int) -> pd.DataFrame:
    """
    Predict the growth in demand in a given year
    :param hourly_demand: pd.DataFrame(columns=['HourOfYear', '$[Year]'])
    :param year_wanted: int year of the wanted output
    :return: new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    """
    s = hourly_demand.copy()
    s[s.columns[1]] *= 1.28 ** (year_wanted - int(s.columns[1]))
    s = s.rename(columns={s.columns[1]: "Demand"})
    return s
