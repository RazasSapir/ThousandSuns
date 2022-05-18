import os.path

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, Input, State, Output, callback
from dash.exceptions import PreventUpdate

from UI.UI_params import *
from df_objects.df_objects import DemandDf, ProductionDf
from hourly_simulation.parameters import NORMALISED_SOLAR_PRODUCTION, Params, \
    get_simulation_parameters, PARAMS_PATH
from hourly_simulation.simulation import get_usage_profile
from output_graphs import yearly_graph_fig


def get_layout():
    return html.Div([
        html.Div([
            html.H1("Annual Simulation"),
            html.Table([
                html.Tr([
                    html.Td("Place to Simulate: "),
                    html.Td(dcc.Dropdown(demand_files, id='place_to_research'))]),
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
                    html.Td("Solar panel max KW: "),
                    html.Td(dbc.Input(id='solar_panel_power_kw', value='6000', type='number'))]),
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
    ])


@callback(
    Output('yearly_graph', 'figure'),
    Input(component_id='run_simulation_button', component_property="n_clicks"),
    State(component_id='number_batteries', component_property='value'),
    State(component_id='solar_panel_power_kw', component_property='value'),
    State(component_id='year_to_simulate', component_property='value'),
    State(component_id='use_strategy', component_property='value'),
    State(component_id='place_to_research', component_property='value'),
)
def run_simulation(n_clicks, num_batteries, solar_panel_power_kw, simulated_year, chosen_strategy, place_to_research):
    solar_panel_power_kw = float(solar_panel_power_kw)
    num_batteries = float(num_batteries)
    simulated_year = int(simulated_year)
    if not place_to_research or not chosen_strategy:
        raise PreventUpdate
    demand = DemandDf(pd.read_csv(os.path.join(SIMULATION_DEMAND_INPUT_PATH, place_to_research), index_col=0))
    normalised_panel_production = ProductionDf(NORMALISED_SOLAR_PRODUCTION.df.copy())
    wanted_simulation_params = Params(**get_simulation_parameters(PARAMS_PATH))
    electricity_use = get_usage_profile(demand=demand,
                                        normalised_production=normalised_panel_production,
                                        params=wanted_simulation_params,
                                        power_solar_panels=solar_panel_power_kw,
                                        num_batteries=num_batteries,
                                        strategy=use_strategies[chosen_strategy],
                                        simulated_year=simulated_year)
    return yearly_graph_fig(electricity_use.df, num_batteries,
                            wanted_simulation_params.BATTERY_CAPACITY, demand,
                            num_hours_to_sum=1)
