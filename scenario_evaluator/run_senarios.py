from typing import Iterator, Tuple

from hourly_simulation import strategies
from hourly_simulation.parameters import *
from hourly_simulation.simulation import simulate_use
from preprocess.csv_to_pd import *


def run_scenarios(simulated_year: int, solar_panel_power_it: Iterator, battery_size_it: Iterator) -> Tuple[float, float]:
    """
    Run the simulation of various solar panel and battery combinations
    :param simulated_year: int year to simulate
    :param solar_panel_it: iterator for different solar panels
    :param battery_size_it: iterator for different battery sizes
    :return: Tuple of the best combination of (number of solar panels, size of battery)
    """
    demand: pd.DataFrame = get_demand(DEMAND_FILE_PATH)
    single_panel_production: pd.DataFrame = get_production(PANEL_PRODUCTION_PATH)
    simulation_results = {}
    for power_solar_panels in solar_panel_power_it:
        for battery_storage in battery_size_it:
            simulation_results[(power_solar_panels, battery_storage)] = simulate_use(demand, single_panel_production,
                                                                                   power_solar_panels,
                                                                                   battery_storage,
                                                                                   strategies.greedy_use_strategy,
                                                                                   simulated_year)
    df_results = pd.DataFrame(simulation_results)
    return df_results.idxmin().name
