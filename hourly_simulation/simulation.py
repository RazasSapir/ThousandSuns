from typing import Tuple, Callable

from hourly_simulation.parameters import *
from hourly_simulation.predict_demand import *
from preprocess.csv_to_pd import *


# todo: add units to parameters


def __get_solar_production_profile(normalised_production: pd.DataFrame, power_solar_panels: int) -> pd.DataFrame:
    """
    :param normalised_production: normalised solar hourly production pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    :param power_solar_panels: int power of solar panels build
    :return: total production of solar panels pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    total_production = normalised_production.copy()
    total_production[SolarProduction] *= power_solar_panels
    return total_production


def __calculate_cost(electricity_usage: pd.DataFrame, battery_capacity: float, power_solar_panels: int,
                     time_span: float = 1) -> float:
    """

    :param time_span: the time of the run
    :param power_solar_panels: int power of panel Kwh
    :param battery_capacity: float capacity of batteries in Kwh
    :param electricity_usage: pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    :return: float cost of the given electricity usage
    """
    gas_usage = electricity_usage[GasUsage]
    gas_cost_per_hour = ELECTRICITY_COST.loc[electricity_usage.HourOfYear, COST]
    total_gas_cost = gas_usage.to_numpy().dot(gas_cost_per_hour.to_numpy())
    total_solar_opex = power_solar_panels * SOLAR_OPEX
    total_solar_capex = power_solar_panels * SOLAR_CAPEX / time_span
    total_battery_opex = battery_capacity * BATTERY_OPEX
    total_battery_capex = battery_capacity * BATTERY_CAPEX / time_span
    return total_gas_cost + total_solar_opex + total_solar_capex + total_battery_opex + total_battery_capex


def __calculate_pollution(electricity_usage: pd.DataFrame):
    """
    Calculate the total pollution created by the gas in the given year.
    :param electricity_usage: pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    :return: float pollution in units? # todo: define the wanted units
    """
    return 0


def simulate_use(demand: pd.DataFrame, normalised_production: pd.DataFrame, power_solar_panels: int,
                 battery_storage: float, strategy: Callable, simulated_year: int) -> \
        Tuple[
            float, float]:
    """
    simulate the usages based of demand. number of solar panels and number of panels.
    :param demand: pd.DataFrame(columns=['HourOfYear', '$(Year)'])
    :param normalised_production: pd.DataFrame(columns=['HourOfYear', 'SolarProduction']) between 0 and 1
    :param simulated_year: year to simulate
    :param power_solar_panels: int power of solar panels Kwh
    :param battery_storage: float size of battery
    :param strategy: function responsible for handling the cost
    :return: (total_cost, total_pollution)
    """
    future_demand = predict_demand_in_year(demand, simulated_year)
    total_panel_production: pd.DataFrame = __get_solar_production_profile(normalised_production, power_solar_panels)
    electricity_use: pd.DataFrame = strategy(future_demand, total_panel_production, battery_storage)
    return __calculate_cost(electricity_use, battery_storage, power_solar_panels), __calculate_pollution(
        electricity_use)
