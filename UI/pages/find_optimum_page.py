import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, State, Output, callback
from dash.exceptions import PreventUpdate

from UI.UI_params import *
from df_objects.df_objects import DemandDf, ProductionDf, SimulationResults
from hourly_simulation.parameters import NORMALISED_SOLAR_PRODUCTION, Params, get_simaltion_paramaters, PARAMS_PATH
from output_graphs import simulation_graph
from scenario_evaluator.run_senarios import run_scenarios

show_error = {"color": "red", 'display': 'block'}
dont_show_error = {'display': 'none'}
output_text = lambda s1, s2: [html.P("Solar Panels: {:,}".format(s1)), html.P("Number Batteries: {:,}".format(s2))]


def get_layout():
    return html.Div([
        html.Div([
            html.H1("Find Optimum"),
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
                    html.Td("Batteries Range (start, stop, num):"),
                    html.Td(dbc.Input(id='number_batteries_range', value='3,4,10', type='text')),
                ]),
                html.Tr([
                    html.Td("Solar panel max KW Range (start, stop, num):"),
                    html.Td(dbc.Input(id='solar_panel_power_kw_range', value='6000,8000,10', type='text'))]),
                html.Tr([
                    html.Td(dbc.Button(id='run_simulation_button', children='Run Simulation', n_clicks=0))]),
            ]),
            html.H2("Input Error", id="input_error", style=dont_show_error)
        ]),
        html.Br(),
        dcc.Loading(
            id="loading",
            type="default",
            children=[dcc.Graph(id='optimal_graph')]
        ),
        html.H6("", id="reached_limits", style={"color": "red"}),
        html.H3("", id="best_combination"),
    ])


@callback(
    Output('optimal_graph', 'figure'),
    Output('input_error', component_property='style'),
    Output('best_combination', component_property="children"),
    Output('reached_limits', component_property="children"),
    Input(component_id='run_simulation_button', component_property="n_clicks"),
    State(component_id='number_batteries_range', component_property='value'),
    State(component_id='solar_panel_power_kw_range', component_property='value'),
    State(component_id='year_to_simulate', component_property='value'),
    State(component_id='use_strategy', component_property='value'),
    State(component_id='place_to_research', component_property='value'),
)
def run_optimal_simulation(n_clicks, num_batteries_range, solar_panel_power_kw_range, simulated_year, chosen_strategy,
                           place_to_research):
    try:
        solar_panel_power_kw_range = [float(num.strip()) for num in str(solar_panel_power_kw_range).split(',')]
        solar_panel_power_it = np.linspace(solar_panel_power_kw_range[0], solar_panel_power_kw_range[1],
                                           int(solar_panel_power_kw_range[2]))
        num_batteries_range = [float(num.strip()) for num in str(num_batteries_range).split(',')]
        num_batteries_it = np.linspace(num_batteries_range[0], num_batteries_range[1], int(num_batteries_range[2]))
        simulated_year = int(simulated_year)
        if not place_to_research or not chosen_strategy:
            raise PreventUpdate
        demand = DemandDf(pd.read_csv(os.path.join(SIMULATION_DEMAND_INPUT_PATH, place_to_research), index_col=0))
        normalised_panel_production = ProductionDf(NORMALISED_SOLAR_PRODUCTION.df.copy())
        wanted_simulation_params = Params(**get_simaltion_paramaters(PARAMS_PATH))
    except (ValueError, IndexError) as e:
        return go.Figure(), show_error, "", ""
    simulation_results, best_combination, in_bounds = run_scenarios(demand=demand,
                                                                    single_panel_production=normalised_panel_production,
                                                                    simulated_year=simulated_year,
                                                                    solar_panel_power_it=solar_panel_power_it,
                                                                    num_batteries_it=num_batteries_it,
                                                                    strategy=use_strategies[chosen_strategy],
                                                                    params=wanted_simulation_params)

    return simulation_graph(simulation_results=simulation_results,
                            solar_panel_power_it=solar_panel_power_it,
                            num_batteries_it=num_batteries_it), \
           dont_show_error, \
           output_text(round(best_combination[SimulationResults.PowerSolar]),
                       round(best_combination[SimulationResults.NumBatteries])), \
           in_bounds
