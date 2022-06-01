from typing import Tuple

from df_objects.df_objects import DemandDf
from hourly_simulation.parameters import Params


def predict_demand_in_year(hourly_demand: DemandDf, params: Params, simulated_year: int) -> Tuple[DemandDf,int]:
    """
    Predict the growth in demand in a given year with exponential growth with GROWTH_PER_YEAR

    :param params: namedtuple Params: simulation params
    :param hourly_demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$[Year]'])
    :param simulated_year: int year of the wanted output
    :return: DemandDf of new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    and the year of demand
    """
    expected_demand = DemandDf(hourly_demand.df.copy())
    year_of_demand = int(expected_demand.Demand)
    expected_demand.df[expected_demand.Demand] *= params.GROWTH_PER_YEAR ** (simulated_year -
                                                                             year_of_demand)
    expected_demand.df = expected_demand.df.rename(columns={expected_demand.Demand: DemandDf.Demand})
    expected_demand.Demand = DemandDf.Demand
    return expected_demand, year_of_demand
