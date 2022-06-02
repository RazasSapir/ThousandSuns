import os.path
import traceback
from datetime import datetime

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, Input, State, Output, callback

from UI.UI_params import *
from df_objects.df_objects import DemandDf, ProductionDf
from hourly_simulation.parameters import Params, get_simulation_parameters, PARAMS_PATH
from hourly_simulation.simulation import get_usage_profile, get_solar_production_profile
from hourly_simulation.strategies import use_strategies
from output_graphs import yearly_graph_fig
from tests.sanity_checks import test_simulation

last_simulation_results = None


def get_layout():
    return html.Div([
        html.Div([
            html.H1("Annual Simulation"),
            dbc.Alert(
                "Parameters Problem - Unfilled / Illegal",
                dismissable=True,
                color="primary",
                id="parameters_alert_annual",
                is_open=False,
            ),
            html.Table([
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
                html.Tr([
                    html.Td("Number of Batteries: "),
                    html.Td(dbc.Input(id='number_batteries', value='3', type='number'))]),
                html.Tr([
                    html.Td("Solar panel max MW: "),
                    html.Td(dbc.Input(id='solar_panel_power_mw', value='6', type='number'))]),
                html.Tr([
                    html.Td(dbc.Button(id='run_simulation_button', children='Run Simulation', n_clicks=0))]),
            ]),
        ]),
        html.Br(),
        dcc.Loading(
            id="loading",
            type="default",
            color="#eb6864",
            children=[dcc.Graph(id='yearly_graph')],
        ),
        html.Br(),
        html.Div(
            [
                dbc.Alert(
                    "You did not run a simulation",
                    dismissable=True,
                    color="primary",
                    id="download_csv_none_error",
                    is_open=False,
                ),
                dbc.Button("Download as CSV", id="download_results_btn",
                           style={"background-color": "gray", "border-color": "gray"}),
                dcc.Download(id="download-results-csv"),
            ]
        )
    ])


@callback(
    Output('yearly_graph', 'figure'),
    Output("parameters_alert_annual", "is_open"),
    Input(component_id='run_simulation_button', component_property="n_clicks"),
    State(component_id='number_batteries', component_property='value'),
    State(component_id='solar_panel_power_mw', component_property='value'),
    State(component_id='year_to_simulate', component_property='value'),
    State(component_id='use_strategy', component_property='value'),
    State(component_id='place_to_research', component_property='value'),
    State(component_id='production_profile', component_property='value'),
)
def run_simulation(n_clicks, num_batteries, solar_panel_power_mw, simulated_year, chosen_strategy, place_to_research,
                   production_profile):
    global last_simulation_results
    if n_clicks == 0:
        return {}, False
    try:
        solar_panel_power_kw = float(solar_panel_power_mw) * 1000
        num_batteries = float(num_batteries)
        simulated_year = int(simulated_year)
    except:
        return {}, True
    if not place_to_research or not chosen_strategy or not production_profile or solar_panel_power_kw < 0 or \
            num_batteries < 0 or simulated_year < 0:
        return {}, True
    demand = DemandDf(pd.read_csv(os.path.join(SIMULATION_DEMAND_INPUT_PATH, place_to_research), index_col=0))
    normalised_production = ProductionDf(
        pd.read_csv(os.path.join(SIMULATION_PRODUCTION_PROFILE_PATH, production_profile), index_col=0))
    normalised_production.df[normalised_production.SolarProduction] /= normalised_production.df[
        normalised_production.SolarProduction].max()
    params = Params(**get_simulation_parameters(PARAMS_PATH))
    electricity_use = get_usage_profile(demand=demand,
                                        normalised_production=normalised_production,
                                        params=params,
                                        solar_panel_power_kw=solar_panel_power_kw,
                                        num_batteries=num_batteries,
                                        strategy=use_strategies[chosen_strategy],
                                        simulated_year=simulated_year)
    try:
        test_simulation(electricity_use=electricity_use, demand=demand, production=get_solar_production_profile(
            normalised_production, solar_panel_power_kw, params), params=params, num_batteries=num_batteries)
    except AssertionError as e:
        logging.warning(traceback.format_exc())
    for_download = electricity_use.df.copy()
    for_download["Demand"] = demand.df[demand.Demand]
    for_download[normalised_production.SolarProduction] = get_solar_production_profile(
        normalised_production, solar_panel_power_kw, params)
    last_simulation_results = for_download
    return yearly_graph_fig(electricity_use.df, num_batteries,
                            params.BATTERY_CAPACITY, demand,
                            num_hours_to_sum=1,
                            demand_year=demand.YearOfDemand), False


@callback(
    Output("download-results-csv", "data"),
    Output("download_csv_none_error", "is_open"),
    Input("download_results_btn", "n_clicks"),
    prevent_initial_call=True,
)
def download_results_callback(n_clicks):
    global last_simulation_results
    if last_simulation_results is not None:
        return dcc.send_data_frame(last_simulation_results.to_csv,
                                   "simulation_results_" + str(datetime.now().strftime("%H-%M-%S")) + ".csv"), False
    else:
        return None, True
