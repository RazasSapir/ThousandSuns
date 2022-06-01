import copy

from df_objects.df_objects import DemandDf
from hourly_simulation.parameters import Params


def predict_demand_in_year(hourly_demand: DemandDf, params: Params, simulated_year: int) -> DemandDf:
    """
    Predict the growth in demand in a given year with exponential growth with GROWTH_PER_YEAR

    :param params: namedtuple Params: simulation params
    :param hourly_demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$[Year]'])
    :param simulated_year: int year of the wanted output
    :return: DemandDf of new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    and the year of demand
    """
    expected_demand = copy.deepcopy(hourly_demand)
    expected_demand.df[expected_demand.Demand] *= params.GROWTH_PER_YEAR ** (simulated_year -
                                                                             expected_demand.YearOfDemand)
    return expected_demand
