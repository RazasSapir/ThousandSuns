import logging
import os.path

SIMULATION_DEMAND_INPUT_PATH = r"data/simulation_demand_input"
if os.path.isdir(SIMULATION_DEMAND_INPUT_PATH):
    demand_files = os.listdir(SIMULATION_DEMAND_INPUT_PATH)
else:
    logging.error("Could Not Found: " + os.getcwd() + "/" + SIMULATION_DEMAND_INPUT_PATH)

ASSETS_FOLDER = r"UI/assets"
if not os.path.isdir(ASSETS_FOLDER):
    ASSETS_FOLDER = r"Lib/UI/assets"

MADOR_LOGO = r"MadorLogo.png"
TALPIOT_LOGO = r"TalpiotLogo.png"

YEARLY_SIMULATION_PAGE = '/'
FIND_OPTIMUM_PAGE = '/find_optimum'
SIMULATION_PARAMS_PAGE = "/simulation_params"
