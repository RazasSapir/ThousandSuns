import logging

import pandas as pd

from df_objects.df_objects import ElectricityUseDf, DemandDf, ProductionDf
from hourly_simulation.parameters import Params


def test_simulation(electricity_use: ElectricityUseDf, demand: DemandDf, production: ProductionDf,
                    params: Params, num_batteries: float, epsilon=0.05) -> None:
    """
    Running all the sanity checks

    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :param demand: pd.Series the demand in each hour
    :param production: pd.Series the production in each hour
    :param epsilon: small number to account for computational errors
    :return: None
    """
    test_non_negative(electricity_use, epsilon)
    test_demand_is_reached(demand.df[demand.Demand], electricity_use, epsilon)
    test_production_is_used(production.df[production.SolarProduction], electricity_use, epsilon)
    test_all_stored_is_used(electricity_use, num_batteries * params.BATTERY_CAPACITY *
                            params.BATTERY_EFFECTIVE_SIZE)
    test_battery_capacity_is_not_passed(electricity_use, num_batteries * params.BATTERY_CAPACITY *
                                        params.BATTERY_EFFECTIVE_SIZE, num_batteries * params.CHARGE_POWER, epsilon)
    test_charge_power_not_passed(electricity_use, num_batteries * params.CHARGE_POWER, epsilon)
    test_selling_limit_not_passed(electricity_use, params.MAX_SELLING_POWER, epsilon)
    logging.info("Passed all tests")


def test_non_negative(electricity_use: ElectricityUseDf, epsilon: float) -> None:
    """
    Makes sure all the number are non-negative

    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :return: None
    """
    assert not (electricity_use.df < -epsilon).values.any(), "Found Negative value: " + str(
        electricity_use.df.min().min())
    logging.info("Passed test_non_negative")


def test_demand_is_reached(demand: pd.Series, electricity_use: ElectricityUseDf, epsilon: float = 0.005) -> None:
    """
    Makes sure the demand is reached each hour

    :param demand: pd.Series the demand in each hour
    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :param epsilon: small number to account for computational errors
    :return: None
    """
    should_be_demand = electricity_use.df[electricity_use.SolarUsage] + electricity_use.df[electricity_use.GasUsage] + \
                       electricity_use.df[electricity_use.StoredUsage]
    assert (should_be_demand - demand < epsilon).values.any(), "Demand was not reached"
    logging.info("Passed test_demand_is_reached")


def test_production_is_used(production: pd.Series, electricity_use: ElectricityUseDf, epsilon: float = 0.005) -> None:
    """
    Makes sure all the production is accounted for

    :param production: pd.Series the production in each hour
    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :param epsilon: small number to account for computational errors
    :return: None
    """
    should_be_production = electricity_use.df[electricity_use.SolarUsage] + \
                           electricity_use.df[electricity_use.SolarStored] + \
                           electricity_use.df[electricity_use.SolarLost] + \
                           electricity_use.df[electricity_use.SolarSold]

    # for i in range(len(should_be_production)):
    #     if abs(should_be_production[i] - production[i]) > epsilon:
    #         # print(f"in index {i}, {should_be_production[i]} - {production[i]} > {epsilon}")
    #         print(f"in index {i}, difference = {should_be_production[i] - production[i]}, (lost + stored) * (1-battery_efficiency) = "
    #               f"{(electricity_use.df[electricity_use.SolarLost][i] + electricity_use.df[electricity_use.SolarStored][i])*0.13}")


    assert (abs(should_be_production - production) < epsilon).values.all(), "Not all production was used"
    logging.info("passed test_production_is_used")


def test_all_stored_is_used(electricity_use: ElectricityUseDf, battery_capacity: float) -> None:
    """
    Makes sure all the stored energy is used

    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :param battery_capacity: the maximum capacity of the battery
    :return: None
    """
    assert abs(electricity_use.df[electricity_use.SolarStored].sum() +
               electricity_use.df[electricity_use.GasStored].sum() -
               electricity_use.df[electricity_use.StoredUsage].sum() -
               electricity_use.df[electricity_use.StoredSold].sum()) <= battery_capacity, "Not all stored was used"
    logging.info("passed test_all_stored_is_used")


def test_battery_capacity_is_not_passed(electricity_use: ElectricityUseDf, battery_capacity: float,
                                        battery_power: float, epsilon=0.05) -> None:
    """
    Makes sure the battery capacity is not passed

    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :param battery_capacity: the maximum capacity of the battery
    :param epsilon: small number to account for computational errors
    :return: None
    """
    simulate_battery = 0
    for row in electricity_use.df.itertuples():
        simulate_battery += row.SolarStored + row.GasStored - row.StoredUsage - row.StoredSold
        assert row.SolarStored + row.GasStored <= battery_power, f"{row.SolarStored + row.GasStored} <= {battery_power}"
        assert row.StoredUsage + row.StoredSold <= battery_power, f"{row.StoredUsage + row.StoredSold} <= {battery_power}"
        assert not (
                row.SolarStored + row.GasStored > 0 and row.StoredUsage + row.StoredSold > 0), f"not ({row.SolarStored + row.GasStored} > 0 and {row.StoredUsage + row.StoredSold} > 0)"
        # todo: not sure the last should be a test, is charging the battery and using it at the same time allowed?
        assert -epsilon <= simulate_battery <= battery_capacity + epsilon, f"{-epsilon} <= {simulate_battery} <= {battery_capacity + epsilon}"
    logging.info("passed test_battery_capacity_is_not_passed")


def test_charge_power_not_passed(electricity_use: ElectricityUseDf, charge_power: float, epsilon: float) -> None:
    """
    Makes sure the charge power is not passed

    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :param charge_power: the maximum charge power of the battery
    :return:
    """
    assert (abs(electricity_use.df[electricity_use.SolarStored] +
                electricity_use.df[
                    electricity_use.GasStored]) < charge_power + epsilon).values.all(), "Charging power limit was passed"
    assert (abs(electricity_use.df[electricity_use.StoredSold] -
                electricity_use.df[
                    electricity_use.StoredUsage]) < charge_power + epsilon).values.all()
    logging.info("passed test_charge_power_not_passed")


def test_selling_limit_not_passed(electricity_use: ElectricityUseDf, selling_limit: float, epsilon: float) -> None:
    """
    Makes sure the charge power is not passed

    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'GasStored', 'SolarUsage',
        'StoredUsage', 'SolarStored', 'SolarLost', 'SolarSold' , 'StoredSold'])
    :param selling_limit: the maximum selling power of the battery
    :return:
    """
    assert (abs(electricity_use.df[electricity_use.SolarSold] +
                electricity_use.df[
                    electricity_use.StoredSold]) < selling_limit + epsilon).values.all(), "Selling power limit was passed"
    logging.info("passed test_selling_limit_not_passed")
