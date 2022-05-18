import csv
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, State, Output, callback

from hourly_simulation.parameters import simulation_params, get_simaltion_paramaters, PARAMS_PATH

params = simulation_params


def get_layout():
    return html.Div([
        html.H1("Simulation Parameters"),
        html.Table([
            html.Tr([
                html.Td(k),
                html.Td(dbc.Input(id=k, value=v, type='number'))]) for k, v in
            get_simaltion_paramaters(PARAMS_PATH).items()
        ], id="simulation_params_table"),
        dbc.Button(id='save_parameters', children='Save Parameters', n_clicks=0),
        dcc.Loading(
            id="loading",
            type="default",
            children=[html.H2("Default Parameters", id="saved_status")]
        ),
    ])


@callback(
    Output('saved_status', 'children'),
    Input(component_id='save_parameters', component_property="n_clicks"),
    State(component_id='simulation_params_table', component_property='children'),
)
def update_params(n_clicks, params_table):
    global params
    try:
        params = {param["props"]["children"][0]["props"]["children"]:
                      param["props"]["children"][1]["props"]["children"]["props"]["value"]
                  for param in params_table}
        with open(PARAMS_PATH, 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for k, v in params.items():
                writer.writerow([k] + [v])
        return "Last Successful save: " + str(datetime.now().strftime("%H:%M:%S"))
    except Exception as e:
        return "Error while Saving " + str(e)
