import csv
from collections import namedtuple

import pandas as pd

from df_objects.df_objects import CostElectricityDf, ProductionDf

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

# Non changing Params
PARAMS_PATH = "hourly_simulation/parameters.csv"


def get_simulation_parameters(csv_path):
    params = {}
    with open(PARAMS_PATH, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            params[row[0]] = float(row[1])
    return params


__simulation_params_dict = get_simulation_parameters(PARAMS_PATH)
Params = namedtuple('Params', __simulation_params_dict)
simulation_params = Params(**__simulation_params_dict)
