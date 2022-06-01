import csv
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, State, Output, callback
from dash.exceptions import PreventUpdate

from hourly_simulation.parameters import get_simulation_parameters, PARAMS_PATH


def get_layout():
    return html.Div([
        html.H1("Simulation Parameters"),
        html.Table([
            html.Tr([
                html.Td(k),
                html.Td(dbc.Input(id=k, value=v[0], type='number')),
                html.Td(v[1])]) for k, v in
            get_simulation_parameters(PARAMS_PATH, with_units=True).items()
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
    if n_clicks == 0:
        raise PreventUpdate()
    try:
        params_with_units_kwh = get_simulation_parameters(PARAMS_PATH, with_units=True)
        new_params_no_units = {param["props"]["children"][0]["props"]["children"]:
                                   param["props"]["children"][1]["props"]["children"]["props"]["value"]
                               for param in params_table}
        for key in params_with_units_kwh.keys():
            params_with_units_kwh[key] = (new_params_no_units[key], params_with_units_kwh[key][1])
        with open(PARAMS_PATH, 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for k, v in params_with_units_kwh.items():
                writer.writerow([k, v[0], v[1]])
        return "Last Successful save: " + str(datetime.now().strftime("%H:%M:%S"))
    except Exception as e:
        return "Error while Saving " + str(e)
