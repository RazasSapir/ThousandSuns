import csv
from collections import namedtuple
from typing import Dict

import pandas as pd

from df_objects.df_objects import CostElectricityDf, ProductionDf

# Non changing Params
PARAMS_PATH = "hourly_simulation/parameters.csv"


def get_simulation_parameters(csv_path, with_units=False) -> Dict:
    """
    Retrieves the parameters from csv_path as dictionary

    :param csv_path: str path of parameters.csv file
    :param with_units: boolean should return the units (third column) as well?
    :return: if with_units: dictionary(str -> float). else: dictionary(str -> (float, str))
    """
    params = {}
    with open(csv_path, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if with_units:
                params[row[0]] = (float(row[1]), row[2])
            else:
                params[row[0]] = float(row[1])
    return params


__simulation_params_dict = get_simulation_parameters(PARAMS_PATH)
Params = namedtuple('Params', __simulation_params_dict.keys())
simulation_params = Params(**__simulation_params_dict)

# Electricity

ELECTRICITY_COST_PATH = 'data/electricity_cost.csv'
ELECTRICITY_SELLING_INCOME_PATH = 'data/electricity_sell_income.csv'
ELECTRICITY_COST = CostElectricityDf(pd.read_csv(ELECTRICITY_COST_PATH))  # ILS per Kw
ELECTRICITY_SELLING_INCOME = CostElectricityDf(pd.read_csv(ELECTRICITY_SELLING_INCOME_PATH))  # ILS per Kw
SELLING_COST = CostElectricityDf(pd.read_csv(r'data/electricity_cost.csv', index_col=0))
BINARY_SELLING_COST = CostElectricityDf(pd.read_csv(r'data/electricity_cost_binary.csv', index_col=0))
BUY_COST = CostElectricityDf(SELLING_COST.df.copy())
BUY_COST.df[BUY_COST.Cost] = BUY_COST.df[BUY_COST.Cost] * simulation_params.BATTERY_EFFICIENCY

# Solar Panels
NATIONAL_SOLAR_PRODUCTION_PATH = 'data/national_solar_production.csv'
NATIONAL_SOLAR_PRODUCTION = ProductionDf(pd.read_csv(NATIONAL_SOLAR_PRODUCTION_PATH, index_col=0))
NORMALISED_SOLAR_PRODUCTION = ProductionDf(NATIONAL_SOLAR_PRODUCTION.df.copy())
NORMALISED_SOLAR_PRODUCTION.df[NORMALISED_SOLAR_PRODUCTION.SolarProduction] /= \
    NATIONAL_SOLAR_PRODUCTION.df[NATIONAL_SOLAR_PRODUCTION.SolarProduction].max()
