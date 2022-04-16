from typing import Callable

from hourly_simulation.parameters import *
from hourly_simulation.predict_demand import *


# todo: add units to parameters


def __get_solar_production_profile(normalised_production: ProductionDf, power_solar_panels: int) -> ProductionDf:
    """
    :param normalised_production: ProductionDf normalised solar hourly production pd.DataFrame(columns=['HourOfYear',
    'SolarProduction'])
    :param power_solar_panels: int power of solar panels build
    :return: ProductionDf total production of solar panels pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    total_production = ProductionDf(normalised_production.df.copy())
    total_production.df[total_production.SolarProduction] *= power_solar_panels
    return total_production


def calculate_cost(electricity_usage: ElectricityUseDf, battery_capacity: float, power_solar_panels: int,
                   time_span: float = 1) -> float:
    """

    :param time_span: the time of the run
    :param power_solar_panels: int power of panel Kwh
    :param battery_capacity: float capacity of batteries in Kwh
    :param electricity_usage: pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    :return: float cost of the given electricity usage
    """
    hours_paid_in_year = ELECTRICITY_COST.df[ELECTRICITY_COST.HourOfYear] == electricity_usage.df[
        electricity_usage.HourOfYear]
    gas_cost_per_hour = ELECTRICITY_COST.df.loc[hours_paid_in_year, ELECTRICITY_COST.Cost]
    total_gas_cost = electricity_usage.df[electricity_usage.GasUsage].to_numpy().dot(gas_cost_per_hour.to_numpy())
    total_solar_opex = power_solar_panels * SOLAR_OPEX
    total_solar_capex = power_solar_panels * SOLAR_CAPEX / time_span
    total_battery_opex = battery_capacity * BATTERY_OPEX
    total_battery_capex = battery_capacity * BATTERY_CAPEX / time_span
    return total_gas_cost + total_solar_opex + total_solar_capex + total_battery_opex + total_battery_capex


def __calculate_pollution(electricity_usage: ElectricityUseDf):
    """
    Calculate the total pollution created by the gas in the given year.
    :param electricity_usage: ElectricityUseDf pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage',
    'SolarStored', 'SolarLost'])
    :return: float pollution in units? # todo: define the wanted units
    """
    return 0


def simulate_use(demand: DemandDf, normalised_production: ProductionDf, power_solar_panels: int,
                 num_batteries: float, strategy: Callable, simulated_year: int, time_span: int = 1) -> float:
    """
    simulate the usages based of demand. number of solar panels and number of panels.
    :param demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$(Year)'])
    :param normalised_production: ProductionDf of pd.DataFrame(columns=['HourOfYear', 'SolarProduction']) between 0 and 1
    :param simulated_year: year to simulate
    :param power_solar_panels: int power of solar panels Kwh
    :param num_batteries: float number of batteries
    :param strategy: function responsible for handling the cost
    :return: (total_cost, total_pollution)
    """
    future_demand: DemandDf = predict_demand_in_year(demand, simulated_year)
    total_panel_production: ProductionDf = __get_solar_production_profile(normalised_production, power_solar_panels)
    electricity_use: ElectricityUseDf = strategy(future_demand, total_panel_production,
                                                 BATTERY_CAPACITY * num_batteries, CHARGE_POWER * num_batteries)
    return calculate_cost(electricity_use, BATTERY_CAPACITY * num_batteries, power_solar_panels, time_span)
