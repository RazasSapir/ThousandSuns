import logging

from hourly_simulation.parameters import *


def test_simulation(electricity_use: ElectricityUseDf, demand: DemandDf, production: ProductionDf,
                    num_batteries: float,
                    epsilon=0.05) -> None:
    """
    Running all the sanity checks
    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    :param demand: pd.Series the demand in each hour
    :param production: pd.Series the production in each hour
    :param battery_capacity: the maximum capacity of the battery
    :param epsilon: small number to account for computational errors
    :return:
    """
    test_non_negative(electricity_use)
    test_demand_is_reached(demand.df[demand.Demand], electricity_use, epsilon)
    test_production_is_used(production.df[production.SolarProduction], electricity_use, epsilon)
    test_all_stored_is_used(electricity_use, num_batteries * BATTERY_CAPACITY)
    test_battery_capacity_is_not_passed(electricity_use, num_batteries * BATTERY_CAPACITY, epsilon)
    logging.info("Passed all tests")


def test_non_negative(electricity_use: ElectricityUseDf) -> None:
    """
    Makes sure all the number are non-negative
    :param electricity_use: pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    :return: None
    """
    assert not (electricity_use.df < 0).values.any()
    logging.info("Passed test_non_negative")


def test_demand_is_reached(demand: pd.Series, electricity_use: ElectricityUseDf, epsilon: float = 0.005) -> None:
    """
    Makes sure the demand is reached each hour
    :param demand: pd.Series the demand in each hour
    :param electricity_use: ElectricityUseDf the electricity usage in each hour
    :param epsilon: small number to account for computational errors
    :return: None
    """
    should_be_demand = electricity_use.df[electricity_use.SolarUsage] + electricity_use.df[electricity_use.GasUsage] + \
                       electricity_use.df[electricity_use.StoredUsage]
    assert (should_be_demand - demand < epsilon).values.any()
    logging.info("Passed test_demand_is_reached")


def test_production_is_used(production: pd.Series, electricity_use: ElectricityUseDf, epsilon: float = 0.005) -> None:
    """
    Makes sure all the production is accounted for
    :param production: pd.Series the production in each hour
    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage, SolarStored, SolarLost])
    :param epsilon: small number to account for computational errors
    :return: None
    """
    should_be_production = electricity_use.df[electricity_use.SolarUsage] + \
                           electricity_use.df[electricity_use.SolarStored] + \
                           electricity_use.df[electricity_use.SolarLost]
    assert (should_be_production - production < epsilon).values.any()
    logging.info("passed test_production_is_used")


def test_all_stored_is_used(electricity_use: ElectricityUseDf, battery_capacity: float) -> None:
    """
    Makes sure all the stored energy is used
    :param electricity_use: ElectricityUseDf pd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage,
    SolarStored, SolarLost])
    :param battery_capacity: the maximum capacity of the battery
    :return: None
    """
    assert abs(electricity_use.df[electricity_use.SolarStored].sum() -
               electricity_use.df[electricity_use.StoredUsage].sum()) <= battery_capacity
    logging.info("passed test_all_stored_is_used")


def test_battery_capacity_is_not_passed(electricity_use: ElectricityUseDf, battery_capacity: float,
                                        epsilon=0.05) -> None:
    """
    Makes sure the battery capacity is not passed
    :param electricity_use: ElectricityUseDfpd.DataFrame(columns=[HourOfYear, GasUsage, SolarUsage, StoredUsage,
    SolarStored, SolarLost])
    :param battery_capacity: the maximum capacity of the battery
    :param epsilon: small number to account for computational errors
    :return: None
    """
    simulate_battery = 0
    for row in electricity_use.df.itertuples():
        simulate_battery += row.SolarStored - row.StoredUsage
        assert -epsilon <= simulate_battery <= battery_capacity + epsilon
    logging.info("passed test_battery_capacity_is_not_passed")
