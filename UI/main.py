import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

from hourly_simulation.simulation import *
from output_graphs.hourly_graph_creator import *

app = Dash(external_stylesheets=[dbc.themes.JOURNAL])
is_params_hidden = True

app.layout = html.Div([
    html.H1("Yearly Simulation"),
    html.Div([
        html.Table([
            html.Tr([
                html.Td("Place to Simulate: "),
                html.Td(dcc.Dropdown(list(demand_files.keys()), id='place_to_research'))]),
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
            html.Tr([
                html.Td(dbc.Button(id='show_params_button', children='Show Simulation params', n_clicks=0,
                                   style={'background-color': '#777777',
                                          "border-color": '#777777'}))]),
        ]),
        html.Table([
            html.Tr([
                html.Td(k),
                html.Td(dbc.Input(id=k, value=v, type='number'))]) for k, v in simulation_params._asdict().items()
        ], id="simulation_params_table", style={'display': 'none'}),
    ]),
    html.Br(),
    dcc.Loading(
        id="loading",
        type="default",
        children=[dcc.Graph(id='yearly_graph')]
    ),
], style={"padding": "1rem"})


@app.callback(
    Output('yearly_graph', 'figure'),
    Input(component_id='run_simulation_button', component_property="n_clicks"),
    State(component_id='number_batteries', component_property='value'),
    State(component_id='solar_panel_power_kw', component_property='value'),
    State(component_id='year_to_simulate', component_property='value'),
    State(component_id='use_strategy', component_property='value'),
    State(component_id='place_to_research', component_property='value'),
    State(component_id='simulation_params_table', component_property='children')
)
def run_simulation(n_clicks, num_batteries, solar_panel_power_kw, simulated_year, chosen_strategy, place_to_research,
                   params_table):
    solar_panel_power_kw = float(solar_panel_power_kw)
    num_batteries = float(num_batteries)
    simulated_year = int(simulated_year)
    if not place_to_research or not chosen_strategy:
        raise PreventUpdate
    demand = DemandDf(pd.read_csv(demand_files[place_to_research], index_col=0))
    normalised_panel_production = ProductionDf(NORMALISED_SOLAR_PRODUCTION.df.copy())
    wanted_simulation_params = Params(**{param["props"]["children"][0]["props"]["children"]:
                                      param["props"]["children"][1]["props"]["children"]["props"]["value"] for param in
                                  params_table})
    electricity_use = get_usage_profile(demand=demand,
                                        normalised_production=normalised_panel_production,
                                        params=wanted_simulation_params,
                                        power_solar_panels=solar_panel_power_kw,
                                        num_batteries=num_batteries,
                                        strategy=use_strategies[chosen_strategy],
                                        simulated_year=simulated_year)
    return yearly_graph_fig(electricity_use.df, num_hours_to_sum=1)


@app.callback(
    Output(component_id='simulation_params_table', component_property='style'),
    Input(component_id='show_params_button', component_property="n_clicks"),
)
def show_params(n_clicks):
    global is_params_hidden
    is_params_hidden = not is_params_hidden
    if is_params_hidden:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


def main():
    app.run_server(host="0.0.0.0", debug=True)
