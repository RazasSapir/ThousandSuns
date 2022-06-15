import copy
from typing import Callable

import numpy_financial as npf

from df_objects import ProductionDf
from df_objects.df_objects import ElectricityUseDf, DemandDf
from hourly_simulation.parameters import Params, ELECTRICITY_COST, ELECTRICITY_SELLING_INCOME
from hourly_simulation.predict_demand import predict_demand_in_year


def get_solar_production_profile(normalised_production: ProductionDf, solar_panel_power_kw: float,
                                 params: Params) -> ProductionDf:
    """
    Get Solar Production Profile as pd.DataFrame.

    :param normalised_production: ProductionDf normalised solar hourly production pd.DataFrame(columns=['HourOfYear',
        'SolarProduction'])
    :param solar_panel_power_kw: float max power of solar panels built [KW]
    :param params: namedtuple simulation params
    :return: ProductionDf total production of solar panels pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    total_production = copy.deepcopy(normalised_production)
    average_effective_size = (1 + (1 - params.PV_DEGRADATION) ** params.FACILITY_LIFE_SPAN) / 2
    total_production.df[
        total_production.SolarProduction] *= average_effective_size * solar_panel_power_kw  # production in Kw
    return total_production


def calculate_cost(electricity_use: ElectricityUseDf, params: Params, battery_capacity: float,
                   solar_panel_power_kw: float,
                   return_description=False):  # -> Optional[float, Tuple[float, Tuple[Any]]]:
    """
    Calculates the cost of  electricity_use

    :param params: namedtuple simulation params
    :param solar_panel_power_kw: int power of panel Kwh
    :param battery_capacity: float capacity of batteries in Kwh
    :param electricity_use: pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored',
        'SolarLost'])
    :return: float cost of the given electricity usage
    """
    # find relevant hours
    hours_paid_in_year = ELECTRICITY_COST.df[ELECTRICITY_COST.HourOfYear] == electricity_use.df[
        electricity_use.HourOfYear]
    # extract gas buying price per hour
    gas_cost_per_hour = ELECTRICITY_COST.df.loc[hours_paid_in_year, ELECTRICITY_COST.Cost]
    # extract gas selling price cost per hour
    selling_income_per_hour = ELECTRICITY_SELLING_INCOME.df.loc[hours_paid_in_year, ELECTRICITY_COST.Cost]
    # calculate gas usage price
    gas_usage_cost = electricity_use.df[electricity_use.GasUsage].to_numpy().dot(gas_cost_per_hour.to_numpy())
    # calculate gas stored price
    gas_stored_cost = electricity_use.df[electricity_use.GasStored].to_numpy().dot(gas_cost_per_hour.to_numpy())
    total_gas_cost = gas_usage_cost + gas_stored_cost / params.BATTERY_EFFICIENCY
    # calculate solar selling income
    immediate_selling_income = electricity_use.df[electricity_use.SolarSold].to_numpy().dot(
        selling_income_per_hour.to_numpy())
    # calculate stored selling income
    battery_selling_income = electricity_use.df[electricity_use.StoredSold].to_numpy().dot(
        selling_income_per_hour.to_numpy())
    total_selling_income = immediate_selling_income + battery_selling_income
    # calculate PV opex and capex
    total_solar_opex = solar_panel_power_kw * params.PV_OPEX
    total_solar_capex = solar_panel_power_kw * params.PV_CAPEX / params.FACILITY_LIFE_SPAN
    # calculate batteries opex and capex
    total_battery_opex = battery_capacity * params.BATTERY_OPEX
    total_battery_capex = battery_capacity * params.BATTERY_CAPEX / params.FACILITY_LIFE_SPAN
    # sum opex and capex
    total_init_capex = total_battery_capex + total_solar_capex
    total_opex = total_solar_opex + total_battery_opex
    # battery_replacement_cost
    future_battery_capex = params.BATTERY_ADDED_FOR_REPLACEMENT * battery_capacity * params.BATTERY_FUTURE_CAPEX / params.FACILITY_LIFE_SPAN
    # capital expenses due to loans
    total_loan = total_init_capex * params.FACILITY_LIFE_SPAN * params.LOAN_SIZE
    capital_expenses = (-1 * npf.pmt(rate=params.LOAN_INTEREST_RATE, nper=params.LOAN_LENGTH,
                                     pv=total_loan) * params.LOAN_LENGTH - total_loan) / params.FACILITY_LIFE_SPAN
    # entrepreneur profit
    total_equity = total_init_capex * params.FACILITY_LIFE_SPAN * (1 - params.LOAN_SIZE)
    entrepreneur_profit = (-1 * npf.pmt(rate=params.ENTREPRENEUR_PROFIT, nper=params.FACILITY_LIFE_SPAN,
                                        pv=total_equity) * params.FACILITY_LIFE_SPAN - total_equity) / params.FACILITY_LIFE_SPAN
    # sum the cost
    total_cost = total_gas_cost + total_init_capex + total_opex + future_battery_capex - total_selling_income + \
                 capital_expenses + entrepreneur_profit
    if return_description:
        return total_cost, ((total_cost, total_gas_cost, total_solar_capex, total_battery_capex,
                             future_battery_capex, total_solar_opex, total_battery_opex,
                             capital_expenses, entrepreneur_profit, total_selling_income,))
    return total_cost


def get_usage_profile(demand: DemandDf, normalised_production: ProductionDf, params: Params,
                      solar_panel_power_kw: float,
                      num_batteries: float, strategy: Callable, simulated_year: int):
    """
    Simulate Usage Profile
    :param demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$(Year)'])
    :param normalised_production: ProductionDf of pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
        between 0 and 1
    :param params: namedtuple simulation params
    :param simulated_year: year to simulate
    :param solar_panel_power_kw: int power of solar panels Kwh
    :param num_batteries: float number of batteries
    :param strategy: function responsible for handling the cost
    :return: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage', 'StoredUsage',
                'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    """
    future_demand = predict_demand_in_year(hourly_demand=demand, params=params,
                                           simulated_year=simulated_year)
    total_panel_production: ProductionDf = get_solar_production_profile(normalised_production=normalised_production,
                                                                        solar_panel_power_kw=solar_panel_power_kw,
                                                                        params=params)
    electricity_use: ElectricityUseDf = strategy(future_demand, total_panel_production,
                                                 params, num_batteries, future_demand.YearOfDemand)
    return electricity_use


def simulate_use(demand: DemandDf, normalised_production: ProductionDf, params: Params, solar_panel_power_kw: float,
                 num_batteries: float, strategy: Callable, simulated_year: int) -> float:
    """
    simulate the usages based of demand. number of solar panels and number of panels.

    :param demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$(Year)'])
    :param normalised_production: ProductionDf of pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
        between 0 and 1
    :param params: namedtuple simulation params
    :param simulated_year: year to simulate
    :param solar_panel_power_kw: int power of solar panels Mw
    :param num_batteries: float number of batteries
    :param strategy: function responsible for handling the cost
    :return: float total_cost
    """
    electricity_use = get_usage_profile(demand=demand, normalised_production=normalised_production,
                                        solar_panel_power_kw=solar_panel_power_kw,
                                        num_batteries=num_batteries, strategy=strategy, params=params,
                                        simulated_year=simulated_year)
    return calculate_cost(electricity_use=electricity_use,
                          params=params,
                          battery_capacity=params.BATTERY_CAPACITY * num_batteries,
                          solar_panel_power_kw=solar_panel_power_kw)
