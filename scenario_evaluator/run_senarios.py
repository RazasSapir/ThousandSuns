from typing import Iterator, Tuple

import pandas as pd

from hourly_simulation.parameters import *
from hourly_simulation.simulation import simulate_use
from hourly_simulation import strategies
from tqdm import tqdm


def run_scenarios(demand: DemandDf, single_panel_production: ProductionDf, simulated_year: int,
                  solar_panel_power_it: Iterator, num_batteries_it: Iterator, params: Params) -> \
        Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run the simulation of various solar panel and battery combinations
    :param demand:
    :param single_panel_production:
    :param simulated_year: int year to simulate
    :param solar_panel_power_it: iterator for different solar panels
    :param num_batteries_it: iterator for different battery sizes
    :return: Tuple of the best combination of (number of solar panels, size of battery)
    """
    simulation_results = {'PowerSolar': [], 'BatteryCapacity': [], 'Cost': []}
    for power_solar_panels in tqdm(solar_panel_power_it):
        for num_batteries in num_batteries_it:
            simulation_results['PowerSolar'].append(power_solar_panels)
            simulation_results['BatteryCapacity'].append(num_batteries)
            simulation_results['Cost'].append(
                simulate_use(demand=demand, normalised_production=single_panel_production, params=params,
                             power_solar_panels=power_solar_panels, num_batteries=num_batteries,
                             strategy=strategies.greedy_use_strategy, simulated_year=simulated_year, time_span=25))
    df_results = pd.DataFrame.from_dict(simulation_results)
    return df_results, df_results.loc[df_results['Cost'].idxmin()]
