import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, State, Output, callback
from dash.exceptions import PreventUpdate

from UI.UI_params import *
from df_objects.df_objects import DemandDf, ProductionDf, SimulationResults
from hourly_simulation.parameters import NORMALISED_SOLAR_PRODUCTION, Params, get_simulation_parameters, PARAMS_PATH
from hourly_simulation.strategies import use_strategies
from output_graphs import simulation_graph
from scenario_evaluator.run_senarios import run_scenarios

show_error = {"color": "red", 'display': 'block'}
dont_show_error = {'display': 'none'}
output_text = lambda s1, s2: [html.P("Solar Panels: {:,}".format(s1)), html.P("Number Batteries: {:,}".format(s2))]
progress_bar = [0]


def get_layout():
    return html.Div([
        html.Div([
            html.H1("Find Optimum"),
            html.Table(style={"width": "100%"}, children=[
                html.Tr([
                    html.Td(html.Table([
                        html.Tr([
                            html.Td("Inputs:"), ]),
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
                            html.Td("Time Span [Years]: "),
                            html.Td(dbc.Input(id='time_span_input', value='25', type='number'))])
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
                            html.Td("Solar panel max KW Range:"), ]),
                        html.Tr([
                            html.Td("From:"),
                            html.Td(dbc.Input(id='solar_panel_power_kw_min_range', value='6000', type='number'))]),
                        html.Tr([
                            html.Td("To:"),
                            html.Td(dbc.Input(id='solar_panel_power_kw_max_range', value='8000', type='number'))]),
                        html.Tr([
                            html.Td("Points:"),
                            html.Td(dbc.Input(id='solar_panel_power_kw_num_range', value='10', type='number')),
                        ]),
                    ])),
                ])
            ]),
            dbc.Button(id='run_simulation_button', children='Run Simulation', n_clicks=0),
            html.H2("Input Error", id="input_error", style=dont_show_error)
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
    Output('optimal_graph', 'figure'),
    Output('input_error', component_property='style'),
    Output('best_combination', component_property="children"),
    Output('reached_limits', component_property="children"),
    Input(component_id='run_simulation_button', component_property="n_clicks"),
    State(component_id='number_batteries_min_range', component_property='value'),
    State(component_id='number_batteries_max_range', component_property='value'),
    State(component_id='number_batteries_num_range', component_property='value'),
    State(component_id='solar_panel_power_kw_min_range', component_property='value'),
    State(component_id='solar_panel_power_kw_max_range', component_property='value'),
    State(component_id='solar_panel_power_kw_num_range', component_property='value'),
    State(component_id='year_to_simulate', component_property='value'),
    State(component_id='use_strategy', component_property='value'),
    State(component_id='place_to_research', component_property='value'),
    State(component_id='time_span_input', component_property='value'),
)
def run_optimal_simulation(n_clicks, n_batteries_min, n_batteries_max, n_batteries_num, pv_power_min, pv_power_max,
                           pv_power_num, simulated_year, chosen_strategy, place_to_research, time_span_input):
    global progress_bar
    progress_bar = [0]
    if n_clicks == 0:
        raise PreventUpdate()
    try:
        solar_panel_power_it = np.linspace(float(pv_power_min), float(pv_power_max), int(pv_power_num))
        num_batteries_it = np.linspace(float(n_batteries_min), float(n_batteries_max), int(n_batteries_num))
        simulated_year = int(simulated_year)
        if not place_to_research or not chosen_strategy:
            raise PreventUpdate
        demand = DemandDf(pd.read_csv(os.path.join(SIMULATION_DEMAND_INPUT_PATH, place_to_research), index_col=0))
        normalised_panel_production = ProductionDf(NORMALISED_SOLAR_PRODUCTION.df.copy())
        wanted_simulation_params = Params(**get_simulation_parameters(PARAMS_PATH))
    except (ValueError, IndexError) as e:
        return go.Figure(), show_error, "", ""

    arguments = {'demand': demand,
                 'single_panel_production': normalised_panel_production,
                 'simulated_year': simulated_year,
                 'solar_panel_power_it': solar_panel_power_it,
                 'num_batteries_it': num_batteries_it,
                 'strategy': use_strategies[chosen_strategy],
                 'params': wanted_simulation_params,
                 'progress_bar': progress_bar,
                 'time_span': int(time_span_input)}
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_scenarios, *list(arguments.values()))
        simulation_results, best_combination, in_bounds = future.result()
    return simulation_graph(simulation_results=simulation_results,
                            solar_panel_power_it=solar_panel_power_it,
                            num_batteries_it=num_batteries_it), \
           dont_show_error, \
           output_text(round(best_combination[SimulationResults.PowerSolar]),
                       round(best_combination[SimulationResults.NumBatteries], 3)), \
           in_bounds
