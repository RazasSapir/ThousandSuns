import os.path

from hourly_simulation import strategies

SIMULATION_DEMAND_INPUT_PATH = r"data/simulation_demand_input"
demand_files = os.listdir(SIMULATION_DEMAND_INPUT_PATH)

use_strategies = {"Greedy Demand": strategies.greedy_use_strategy}

ASSETS_FOLDER = r"UI/assets"
MADOR_LOGO = r"MadorLogo.png"
TALPIOT_LOGO = r"TalpiotLogo.png"

YEARLY_SIMULATION_PAGE = '/'
FIND_OPTIMUM_PAGE = '/find_optimum'
SIMULATION_PARAMS_PAGE = "/simulation_params"
