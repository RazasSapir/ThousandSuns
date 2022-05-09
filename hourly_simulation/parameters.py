from collections import namedtuple

import pandas as pd

from df_objects.df_objects import CostElectricityDf, ProductionDf

# prediction
__GROWTH_PER_YEAR = 1.028

# Batteries
__BATTERY_CAPACITY = 4000  # Kwh
__CHARGE_POWER = 2000  # Kw

# BATTERY_DEPTH = 0.8  # %
__BATTERY_EFFICIENCY = 0.87  # %
__BATTERY_OPEX = 15.6  # ILS / kW / year
__BATTERY_CAPEX = 1000  # ILS / Kwh

# Electricity
ELECTRICITY_COST_PATH = 'data/electricity_cost.csv'
ELECTRICITY_SELLING_INCOME_PATH = 'data/electricity_sell_income.csv'
ELECTRICITY_COST = CostElectricityDf(pd.read_csv(ELECTRICITY_COST_PATH))  # ILS per Kw
ELECTRICITY_SELLING_INCOME = CostElectricityDf(pd.read_csv(ELECTRICITY_SELLING_INCOME_PATH))  # ILS per Kw

# Solar Panels
NATIONAL_SOLAR_PRODUCTION_PATH = 'data/national_solar_production.csv'
NATIONAL_SOLAR_PRODUCTION = ProductionDf(pd.read_csv(NATIONAL_SOLAR_PRODUCTION_PATH, index_col=0))
NORMALISED_SOLAR_PRODUCTION = ProductionDf(NATIONAL_SOLAR_PRODUCTION.df.copy())
NORMALISED_SOLAR_PRODUCTION.df[NORMALISED_SOLAR_PRODUCTION.SolarProduction] /= \
    NATIONAL_SOLAR_PRODUCTION.df[NATIONAL_SOLAR_PRODUCTION.SolarProduction].max()

__SOLAR_OPEX = 70  # ILS / kW / year
__SOLAR_CAPEX = 2600  # ILS / Kw

# future constants
__MAXIMUM_SELLING_KWH = 1
__BATTERY_LIFETIME = 0
__SOLAR_LIFETIME = 0

__simulation_params_dict = {
    "GROWTH_PER_YEAR": __GROWTH_PER_YEAR,
    "BATTERY_CAPACITY": __BATTERY_CAPACITY,
    "CHARGE_POWER": __CHARGE_POWER,
    "BATTERY_OPEX": __BATTERY_OPEX,
    "BATTERY_CAPEX": __BATTERY_CAPEX,
    "SOLAR_OPEX": __SOLAR_OPEX,
    "SOLAR_CAPEX": __SOLAR_CAPEX,
    "BATTERY_EFFICIENCY": __BATTERY_EFFICIENCY
}


Params = namedtuple('Params', __simulation_params_dict)
simulation_params = Params(**__simulation_params_dict)

