from df_objects.df_objects import *
from hourly_simulation.parameters import GROWTH_PER_YEAR


def predict_demand_in_year(hourly_demand: DemandDf, year_wanted: int) -> DemandDf:
    """
    Predict the growth in demand in a given year
    :param hourly_demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$[Year]'])
    :param year_wanted: int year of the wanted output
    :return: DemandDf of new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    """
    expected_demand = DemandDf(hourly_demand.df.copy())
    expected_demand.df[expected_demand.Demand] *= GROWTH_PER_YEAR ** (year_wanted - int(expected_demand.Demand))
    expected_demand.df = expected_demand.df.rename(columns={expected_demand.Demand: DemandDf.Demand})
    expected_demand.Demand = DemandDf.Demand
    return expected_demand
