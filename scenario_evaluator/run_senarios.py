import logging
from typing import Iterator, Tuple

import pandas as pd

from hourly_simulation.parameters import *
from hourly_simulation.simulation import simulate_use
from hourly_simulation import strategies
from tqdm import tqdm


def check_reached_edges_of_iterator(solar_panel_power_it: Iterator, num_batteries_it: Iterator,
                                    optimal_power, optimal_num_batteries) -> None:
    """
    Checks whether the one of the optimal values reached the minimum / maximum of the iterator
    :param solar_panel_power_it: iterator for different solar panels
    :param num_batteries_it: iterator for different battery sizes
    :param optimal_power: simulated optimal solar power
    :param optimal_num_batteries: simulated optimal number of batteries
    :return: None
    """
    if optimal_power == min(solar_panel_power_it):
        logging.warning("Reached the 'start edge' of the solar power range: " + str(optimal_power))
    elif optimal_power == max(solar_panel_power_it):
        logging.warning("Reached the 'stop edge' of the solar power range: " + str(optimal_power))
    if optimal_num_batteries == min(num_batteries_it):
        logging.warning("Reached the 'start edge' of the solar power range: " + str(optimal_num_batteries))
    elif optimal_num_batteries == max(num_batteries_it):
        logging.warning("Reached the 'stop edge' of the solar power range: " + str(optimal_num_batteries))


def run_scenarios(demand: DemandDf, single_panel_production: ProductionDf, simulated_year: int,
                  solar_panel_power_it: Iterator, num_batteries_it: Iterator, params: Params) -> \
        Tuple[SimulationResults, pd.DataFrame]:
    """
    Run the simulation of various solar panel and battery combinations
    :param params:
    :param demand:
    :param single_panel_production:
    :param simulated_year: int year to simulate
    :param solar_panel_power_it: iterator for different solar panels
    :param num_batteries_it: iterator for different battery sizes
    :return: Tuple of the best combination of (number of solar panels, size of battery)
    """
    simulation_results = {SimulationResults.PowerSolar: [], SimulationResults.NumBatteries: [],
                          SimulationResults.Cost: []}
    for power_solar_panels in tqdm(solar_panel_power_it):
        for num_batteries in num_batteries_it:
            simulation_results[SimulationResults.PowerSolar].append(power_solar_panels)
            simulation_results[SimulationResults.NumBatteries].append(num_batteries)
            simulation_results[SimulationResults.Cost].append(
                simulate_use(demand=demand,
                             normalised_production=single_panel_production,
                             params=params,
                             power_solar_panels=power_solar_panels,
                             num_batteries=num_batteries,
                             strategy=strategies.greedy_use_strategy,
                             simulated_year=simulated_year,
                             time_span=25))

    df_results = SimulationResults(pd.DataFrame.from_dict(simulation_results))
    optimal_scenario = df_results.df.loc[df_results.df[df_results.Cost].idxmin()]
    check_reached_edges_of_iterator(solar_panel_power_it=solar_panel_power_it,
                                    num_batteries_it=num_batteries_it,
                                    optimal_power=optimal_scenario[df_results.PowerSolar],
                                    optimal_num_batteries=optimal_scenario[df_results.NumBatteries])
    return df_results, optimal_scenario
