import logging
from typing import Iterator, Tuple, Callable, List

import pandas as pd
from tqdm import tqdm

from df_objects.df_objects import DemandDf, ProductionDf, SimulationResults
from hourly_simulation.parameters import Params
from hourly_simulation.predict_demand import predict_demand_in_year
from hourly_simulation.simulation import simulate_use


def check_reached_edges_of_iterator(solar_panel_power_it_kw: Iterator, num_batteries_it: Iterator,
                                    optimal_power, optimal_num_batteries) -> Tuple[bool, str]:
    """
    Checks whether the one of the optimal values reached the minimum / maximum of the iterator.

    :param solar_panel_power_it_kw: iterator for different solar panels
    :param num_batteries_it: iterator for different battery sizes
    :param optimal_power: simulated optimal solar power
    :param optimal_num_batteries: simulated optimal number of batteries
    :return: Tuple[is reached bounds?, String status of optimal combination in bounds].
    """
    results = ""
    if optimal_power == min(solar_panel_power_it_kw):
        msg = "Reached the 'from' of the Solar panel max MW Range: " + str(optimal_power / 1000)
        logging.warning(msg)
        results += msg + '\n'
    elif optimal_power == max(solar_panel_power_it_kw):
        msg = "Reached the 'to' of the Solar panel max MW Range: " + str(optimal_power / 1000)
        logging.warning(msg)
        results += msg + '\n'
    if optimal_num_batteries == min(num_batteries_it):
        msg = "Reached the 'from' of the Batteries Range: " + str(optimal_num_batteries)
        logging.warning(msg)
        results += msg + '\n'
    elif optimal_num_batteries == max(num_batteries_it):
        msg = "Reached the 'to' of the Batteries Range: " + str(optimal_num_batteries)
        logging.warning(msg)
        results += msg + '\n'
    if not results:
        return False, "Optimal Combination is in range"
    return True, results


def run_scenarios(demand: DemandDf, normalised_production: ProductionDf, simulated_year: int,
                  solar_panel_power_it_kw: Iterator, num_batteries_it: Iterator, strategy: Callable, params: Params,
                  progress_bar: List[float]) -> Tuple[SimulationResults, pd.DataFrame, Tuple[bool, str]]:
    """
    Run the simulation of various solar panel and battery combinations

    :param demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$(Year)'])
    :param normalised_production: ProductionDf of pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
        between 0 and 1
    :param simulated_year: int year to simulate
    :param solar_panel_power_it_kw: iterator for different solar panels in kw
    :param num_batteries_it: iterator for different battery sizes
    :param strategy: function responsible for handling the cost
    :param params: namedtuple simulation params
    :param progress_bar: List reference used to update callee on percentage done.
    :return: Tuple of the best combination of (number of solar panels, size of battery)
    """
    simulation_results = {SimulationResults.PowerSolar: [], SimulationResults.NumBatteries: [],
                          SimulationResults.Cost: []}
    counter = 0
    total_simulations = sum(1 for _ in solar_panel_power_it_kw) * sum(
        1 for _ in num_batteries_it) * params.YEARS_TO_SIMULATE
    for solar_panel_power_kw in tqdm(solar_panel_power_it_kw):
        for num_batteries in num_batteries_it:
            total_cost = 0
            for year in range(int(params.YEARS_TO_SIMULATE)):
                total_cost += simulate_use(demand=predict_demand_in_year(demand, params, demand.YearOfDemand + year),
                                           normalised_production=normalised_production,
                                           params=params,
                                           solar_panel_power_kw=solar_panel_power_kw,
                                           num_batteries=num_batteries,
                                           strategy=strategy,
                                           simulated_year=simulated_year)
                counter += 1
                progress_bar.append(counter / total_simulations)
            simulation_results[SimulationResults.PowerSolar].append(solar_panel_power_kw)
            simulation_results[SimulationResults.NumBatteries].append(num_batteries)
            simulation_results[SimulationResults.Cost].append(total_cost)
    df_results = SimulationResults(pd.DataFrame.from_dict(simulation_results))
    optimal_scenario = df_results.df.loc[df_results.df[df_results.Cost].idxmin()]
    in_bounds = check_reached_edges_of_iterator(solar_panel_power_it_kw=solar_panel_power_it_kw,
                                                num_batteries_it=num_batteries_it,
                                                optimal_power=optimal_scenario[df_results.PowerSolar],
                                                optimal_num_batteries=optimal_scenario[df_results.NumBatteries])
    return df_results, optimal_scenario, in_bounds
