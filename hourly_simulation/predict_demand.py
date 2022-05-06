from df_objects.df_objects import DemandDf
from hourly_simulation.parameters import Params


def predict_demand_in_year(hourly_demand: DemandDf, params: Params, simulated_year: int) -> DemandDf:
    """
    Predict the growth in demand in a given year
    :param params: namedtuple simulation params
    :param hourly_demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$[Year]'])
    :param simulated_year: int year of the wanted output
    :return: DemandDf of new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    """
    expected_demand = DemandDf(hourly_demand.df.copy())
    expected_demand.df[expected_demand.Demand] *= params.GROWTH_PER_YEAR ** (simulated_year - int(expected_demand.Demand))
    expected_demand.df = expected_demand.df.rename(columns={expected_demand.Demand: DemandDf.Demand})
    expected_demand.Demand = DemandDf.Demand
    return expected_demand
