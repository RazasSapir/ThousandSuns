import logging
from typing import Iterator, Tuple, Callable, List

import pandas as pd
from tqdm import tqdm

from df_objects.df_objects import DemandDf, ProductionDf, SimulationResults
from hourly_simulation.parameters import Params
from hourly_simulation.simulation import simulate_use


def check_reached_edges_of_iterator(solar_panel_power_it: Iterator, num_batteries_it: Iterator,
                                    optimal_power, optimal_num_batteries) -> str:
    """
    Checks whether the one of the optimal values reached the minimum / maximum of the iterator
    :param solar_panel_power_it: iterator for different solar panels
    :param num_batteries_it: iterator for different battery sizes
    :param optimal_power: simulated optimal solar power
    :param optimal_num_batteries: simulated optimal number of batteries
    :return: None
    """
    results = ""
    if optimal_power == min(solar_panel_power_it):
        msg = "Reached the 'start edge' of the solar power range: " + str(optimal_power)
        logging.warning(msg)
        results += msg + '\n'
    elif optimal_power == max(solar_panel_power_it):
        msg = "Reached the 'stop edge' of the solar power range: " + str(optimal_power)
        logging.warning(msg)
        results += msg + '\n'
    if optimal_num_batteries == min(num_batteries_it):
        msg = "Reached the 'start edge' of the num_batteries range: " + str(optimal_num_batteries)
        logging.warning(msg)
        results += msg + '\n'
    elif optimal_num_batteries == max(num_batteries_it):
        msg = "Reached the 'stop edge' of the num_batteries range: " + str(optimal_num_batteries)
        logging.warning(msg)
        results += msg + '\n'
    if not results:
        return "Optimal Combination is in range"
    return results


def run_scenarios(demand: DemandDf, single_panel_production: ProductionDf, simulated_year: int,
                  solar_panel_power_it: Iterator, num_batteries_it: Iterator, strategy: Callable, params: Params,
                  progress_bar: List[float],
                  time_span=25) -> \
        Tuple[SimulationResults, pd.DataFrame, str]:
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
    counter = 0
    total_simulations = sum(1 for _ in solar_panel_power_it) * sum(1 for _ in num_batteries_it)
    for power_solar_panels in tqdm(solar_panel_power_it):
        for num_batteries in num_batteries_it:
            progress_bar.append(counter / total_simulations)
            simulation_results[SimulationResults.PowerSolar].append(power_solar_panels)
            simulation_results[SimulationResults.NumBatteries].append(num_batteries)
            simulation_results[SimulationResults.Cost].append(
                simulate_use(demand=demand,
                             normalised_production=single_panel_production,
                             params=params,
                             power_solar_panels=power_solar_panels,
                             num_batteries=num_batteries,
                             strategy=strategy,
                             simulated_year=simulated_year,
                             time_span=time_span))
            counter += 1
    df_results = SimulationResults(pd.DataFrame.from_dict(simulation_results))
    optimal_scenario = df_results.df.loc[df_results.df[df_results.Cost].idxmin()]
    in_bounds = check_reached_edges_of_iterator(solar_panel_power_it=solar_panel_power_it,
                                                num_batteries_it=num_batteries_it,
                                                optimal_power=optimal_scenario[df_results.PowerSolar],
                                                optimal_num_batteries=optimal_scenario[df_results.NumBatteries])
    return df_results, optimal_scenario, in_bounds
