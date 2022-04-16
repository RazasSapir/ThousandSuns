from hourly_simulation.strategies import *
# todo: add units

# FILE_PATHS
DEMAND_FILE_PATH = ""
PANEL_PRODUCTION_PATH = ""

# prediction
GROWTH_PER_YEAR = 1.028

# Batteries
BATTERY_CAPACITY = 4000  # Kwh
CHARGE_POWER = 1000  # Kw

# BATTERY_EFFICIENCY = 0.89  # %
# BATTERY_DEPTH = 0.8  # %
BATTERY_OPEX = 15.6  # ILS / kW / year
BATTERY_CAPEX = 1004  # ILS per Kw

# Electricity
ELECTRICITY_COST_PATH = 'data/electricity_cost.csv'
ELECTRICITY_COST = CostElectricityDf(pd.read_csv(ELECTRICITY_COST_PATH))  # ILS per Kw

# Solar Panels
NATIONAL_SOLAR_PRODUCTION_PATH = 'data/national_solar_production.csv'
NATIONAL_SOLAR_PRODUCTION = ProductionDf(pd.read_csv(NATIONAL_SOLAR_PRODUCTION_PATH, index_col=0))
NORMALISED_SOLAR_PRODUCTION = ProductionDf(NATIONAL_SOLAR_PRODUCTION.df.copy())
NORMALISED_SOLAR_PRODUCTION.df[NORMALISED_SOLAR_PRODUCTION.SolarProduction] /= \
    NATIONAL_SOLAR_PRODUCTION.df[NATIONAL_SOLAR_PRODUCTION.SolarProduction].max()

SOLAR_OPEX = 70.4  # ILS / kW / year
SOLAR_CAPEX = 3300  # ILS per Kw

# future constants
MAXIMUM_SELLING_KWH = 1
BATTERY_LIFETIME = 0
SOLAR_LIFETIME = 0

# UI params
demand_files = {"Hatzor": r'../data/consumption_hatzor.csv'}
use_strategies = {"Greedy Demand": greedy_use_strategy}
