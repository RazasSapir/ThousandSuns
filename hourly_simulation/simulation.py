# todo: add units to parameters
from typing import Callable

from df_objects import ProductionDf
from df_objects.df_objects import ElectricityUseDf, DemandDf
from hourly_simulation.parameters import Params, ELECTRICITY_COST, ELECTRICITY_SELLING_INCOME
from hourly_simulation.predict_demand import predict_demand_in_year


def __get_solar_production_profile(normalised_production: ProductionDf, power_solar_panels: float) -> ProductionDf:
    """
    :param normalised_production: ProductionDf normalised solar hourly production pd.DataFrame(columns=['HourOfYear',
    'SolarProduction'])
    :param power_solar_panels: int power of solar panels build
    :return: ProductionDf total production of solar panels pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    total_production = ProductionDf(normalised_production.df.copy())
    total_production.df[total_production.SolarProduction] *= power_solar_panels
    return total_production


def calculate_cost(electricity_use: ElectricityUseDf, params: Params, battery_capacity: float,
                   power_solar_panels: float, time_span: float = 1) -> float:
    """
    :param params: namedtuple simulation params
    :param time_span: the time of the run
    :param power_solar_panels: int power of panel Kwh
    :param battery_capacity: float capacity of batteries in Kwh
    :param electricity_use: pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored'
    , 'SolarLost'])
    :return: float cost of the given electricity usage
    """
    hours_paid_in_year = ELECTRICITY_COST.df[ELECTRICITY_COST.HourOfYear] == electricity_use.df[
        electricity_use.HourOfYear]
    gas_cost_per_hour = ELECTRICITY_COST.df.loc[hours_paid_in_year, ELECTRICITY_COST.Cost]
    selling_income_per_hour = ELECTRICITY_SELLING_INCOME.df.loc[hours_paid_in_year, ELECTRICITY_COST.Cost]
    total_gas_cost = electricity_use.df[electricity_use.GasUsage].to_numpy().dot(gas_cost_per_hour.to_numpy())
    immediate_selling_income = electricity_use.df[electricity_use.SolarSold].to_numpy().dot(
        selling_income_per_hour.to_numpy())
    battery_selling_income = electricity_use.df[electricity_use.StoredSold].to_numpy().dot(
        selling_income_per_hour.to_numpy())
    total_selling_income = immediate_selling_income + battery_selling_income
    total_solar_opex = power_solar_panels * params.PV_OPEX
    total_solar_capex = power_solar_panels * params.PV_CAPEX / time_span
    total_battery_opex = battery_capacity * params.BATTERY_OPEX
    total_battery_capex = battery_capacity * params.BATTERY_CAPEX / time_span
    return total_gas_cost + total_solar_opex + total_solar_capex + total_battery_opex + total_battery_capex - total_selling_income


def calculate_cost_with_selling(electricity_use: ElectricityUseDf, params: Params, battery_capacity: float,
                                power_solar_panels: float, time_span: float = 1) -> float:
    pass


def __calculate_pollution(electricity_use: ElectricityUseDf):
    """
    Calculate the total pollution created by the gas in the given year.
    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage',
    'SolarStored', 'SolarLost'])
    :return: float pollution in units? # todo: define the wanted units
    """
    raise NotImplementedError()


def get_usage_profile(demand: DemandDf, normalised_production: ProductionDf, params: Params, power_solar_panels: float,
                      num_batteries: float, strategy: Callable, simulated_year: int):
    """
    Simulate Usage Profile
    :param params:
    :param demand:
    :param normalised_production:
    :param power_solar_panels:
    :param num_batteries:
    :param strategy:
    :param simulated_year:
    :return:
    """
    future_demand: DemandDf = predict_demand_in_year(hourly_demand=demand, params=params, simulated_year=simulated_year)
    total_panel_production: ProductionDf = __get_solar_production_profile(normalised_production=normalised_production,
                                                                          power_solar_panels=power_solar_panels)
    electricity_use: ElectricityUseDf = strategy(future_demand, total_panel_production,
                                                 params, num_batteries)
    return electricity_use


def simulate_use(demand: DemandDf, normalised_production: ProductionDf, params: Params, power_solar_panels: float,
                 num_batteries: float, strategy: Callable, simulated_year: int, time_span: int = 1) -> float:
    """
    simulate the usages based of demand. number of solar panels and number of panels.
    :param params: namedtuple simulation params
    :param time_span: time of which the system is expected to work
    :param demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$(Year)'])
    :param normalised_production: ProductionDf of pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    between 0 and 1
    :param simulated_year: year to simulate
    :param power_solar_panels: int power of solar panels Kwh
    :param num_batteries: float number of batteries
    :param strategy: function responsible for handling the cost
    :return: (total_cost, total_pollution)
    """
    electricity_use = get_usage_profile(demand=demand, normalised_production=normalised_production,
                                        power_solar_panels=power_solar_panels,
                                        num_batteries=num_batteries, strategy=strategy, params=params,
                                        simulated_year=simulated_year)
    return calculate_cost(electricity_use=electricity_use,
                          params=params,
                          battery_capacity=params.BATTERY_CAPACITY * num_batteries,
                          power_solar_panels=power_solar_panels,
                          time_span=time_span)
