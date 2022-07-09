import traceback
from multiprocessing.pool import ThreadPool

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html, Input, State, Output, callback

from UI.UI_params import *
from df_objects.df_objects import DemandDf, ProductionDf, SimulationResults
from hourly_simulation.parameters import Params, get_simulation_parameters, PARAMS_PATH
from hourly_simulation.strategies import use_strategies
from output_graphs import simulation_graph
from scenario_evaluator.run_scenarios import run_scenarios

block_red = {"color": "red", 'display': 'block'}
block_green = {"color": "green", 'display': 'block'}
display_none = {'display': 'none'}
output_text = lambda s1, s2, s3, s4: [html.P("Solar Panels: {:,} Mw".format(s1 / 1000)),
                                      html.P("{:,} Batteries: Capacity: {:,} Mwh, Max Charge Power: {:,} Mw".format(
                                          s2, s3 / 1000, s4 / 1000))]
progress_bar = [0]


def get_layout():
    return html.Div([
        html.Div([
            html.H1("Find Optimum"),
            dbc.Alert(
                "Parameters Unfilled",
                dismissable=True,
                color="primary",
                id="parameters_unfilled_optimum",
                is_open=False,
            ),
            dbc.Alert(
                "Parameters Error",
                dismissable=True,
                color="primary",
                id="parameters_error_optimum",
                is_open=False,
            ),
            html.Table(style={"width": "100%"}, children=[
                html.Tr([
                    html.Td(html.Table([
                        html.Tr([
                            html.Td("Inputs:"), ]),
                        html.Tr([
                            html.Td("Demand Profile: "),
                            html.Td(dcc.Dropdown(demand_files, id='place_to_research'))]),
                        html.Tr([
                            html.Td("Production Profile: "),
                            html.Td(dcc.Dropdown(production_profile_files, id='production_profile'))]),
                        html.Tr([
                            html.Td("Year to simulate: "),
                            html.Td(dbc.Input(id='year_to_simulate', value='2020', type='number'))]),
                        html.Tr([
                            html.Td("Use Strategy: "),
                            html.Td(dcc.Dropdown(list(use_strategies.keys()), id='use_strategy'))]),
                    ])),
                    html.Td(html.Table([
                        html.Tr([
                            html.Td("Batteries Range:"), ]),
                        html.Tr([
                            html.Td("From:"),
                            html.Td(dbc.Input(id='number_batteries_min_range', value='3', type='number'))]),
                        html.Tr([
                            html.Td("To:"),
                            html.Td(dbc.Input(id='number_batteries_max_range', value='4', type='number'))]),
                        html.Tr([
                            html.Td("Points:"),
                            html.Td(dbc.Input(id='number_batteries_num_range', value='10', type='number')),
                        ])])),
                    html.Td(html.Table([
                        html.Tr([
                            html.Td("Solar panel max MW Range:"), ]),
                        html.Tr([
                            html.Td("From:"),
                            html.Td(dbc.Input(id='solar_panel_power_mw_min_range', value='6', type='number'))]),
                        html.Tr([
                            html.Td("To:"),
                            html.Td(dbc.Input(id='solar_panel_power_mw_max_range', value='8', type='number'))]),
                        html.Tr([
                            html.Td("Points:"),
                            html.Td(dbc.Input(id='solar_panel_power_mw_num_range', value='10', type='number')),
                        ]),
                    ])),
                ])
            ]),
            dbc.Button(id='run_simulation_button', children='Run Simulation', n_clicks=0),
        ]),
        html.Br(),
        dcc.Interval(id='clock', interval=500, n_intervals=0, max_intervals=-1),
        dbc.Progress(value=0, id="progress_bar"),
        dcc.Graph(id='optimal_graph'),
        html.H6("", id="reached_limits", style={"color": "red"}),
        html.H3("", id="best_combination"),
    ])


@callback(
    [Output("progress_bar", "value"),
     Output("progress_bar", "label")],
    [Input("clock", "n_intervals")])
def progress_bar_update(n):
    global progress_bar
    progress = int(progress_bar[-1] * 100)
    return (progress, f"{progress} %" if progress >= 5 else "",)


@callback(
    Output(component_id='optimal_graph', component_property='figure'),
    Output(component_id='best_combination', component_property="children"),
    Output(component_id='reached_limits', component_property="children"),
    Output(component_id='reached_limits', component_property="style"),
    Output(component_id='parameters_unfilled_optimum', component_property="is_open"),
    Output(component_id='parameters_error_optimum', component_property="is_open"),
    Input(component_id='run_simulation_button', component_property="n_clicks"),
    State(component_id='number_batteries_min_range', component_property='value'),
    State(component_id='number_batteries_max_range', component_property='value'),
    State(component_id='number_batteries_num_range', component_property='value'),
    State(component_id='solar_panel_power_mw_min_range', component_property='value'),
    State(component_id='solar_panel_power_mw_max_range', component_property='value'),
    State(component_id='solar_panel_power_mw_num_range', component_property='value'),
    State(component_id='year_to_simulate', component_property='value'),
    State(component_id='use_strategy', component_property='value'),
    State(component_id='place_to_research', component_property='value'),
    State(component_id='production_profile', component_property='value'),

)
def run_optimal_simulation(n_clicks, n_batteries_min, n_batteries_max, n_batteries_num, pv_power_min, pv_power_max,
                           pv_power_num, simulated_year, chosen_strategy, place_to_research, production_profile):
    global progress_bar
    progress_bar = [0]
    if n_clicks == 0:
        return {}, "", "", {}, False, False
    try:
        if float(pv_power_min) < 0 or float(pv_power_max) < 0 or int(pv_power_num) < 0 or \
                float(n_batteries_min) < 0 or float(n_batteries_max) < 0 or int(n_batteries_num) < 0:
            return {}, "", "", {}, True, False
        solar_panel_power_it_mw = np.linspace(float(pv_power_min), float(pv_power_max), int(pv_power_num))
        solar_panel_power_it_kw = np.linspace(float(pv_power_min) * 1000, float(pv_power_max) * 1000, int(pv_power_num))
        num_batteries_it = np.linspace(float(n_batteries_min), float(n_batteries_max), int(n_batteries_num))
        simulated_year = int(simulated_year)
        if not place_to_research or not chosen_strategy or not production_profile or simulated_year < 0:
            return {}, "", "", {}, True, False
        demand = DemandDf(pd.read_csv(os.path.join(SIMULATION_DEMAND_INPUT_PATH, place_to_research), index_col=0))
        normalised_production = ProductionDf(
            pd.read_csv(os.path.join(SIMULATION_PRODUCTION_PROFILE_PATH, production_profile), index_col=0))
        normalised_production.df[normalised_production.SolarProduction] /= normalised_production.df[
            normalised_production.SolarProduction].max()
        wanted_simulation_params = Params(**get_simulation_parameters(PARAMS_PATH))
    except Exception as e:
        logging.error(traceback.format_exc())
        return {}, "", "", {}, False, True

    arguments = {'demand': demand,
                 'single_panel_production': normalised_production,
                 'simulated_year': simulated_year,
                 'solar_panel_power_it_kw': solar_panel_power_it_kw,
                 'num_batteries_it': num_batteries_it,
                 'strategy': use_strategies[chosen_strategy],
                 'params': wanted_simulation_params,
                 'progress_bar': progress_bar}

    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(run_scenarios, tuple(arguments.values()))  # tuple of args for foo
    simulation_results, best_combination, in_bounds = async_result.get()
    return simulation_graph(simulation_results=simulation_results,
                            solar_panel_power_it=solar_panel_power_it_mw,
                            num_batteries_it=num_batteries_it), \
           output_text(round(best_combination[SimulationResults.PowerSolar]),
                       round(best_combination[SimulationResults.NumBatteries], 2),
                       round(best_combination[SimulationResults.NumBatteries] *
                             wanted_simulation_params.BATTERY_CAPACITY),
                       round(best_combination[SimulationResults.NumBatteries] *
                             wanted_simulation_params.CHARGE_POWER)), \
           in_bounds[1], block_red if in_bounds[0] else block_green, False, False
