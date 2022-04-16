import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

from hourly_simulation.simulation import *
from output_graphs.hourly_graph_creator import *

app = Dash(external_stylesheets=[dbc.themes.JOURNAL])

app.layout = html.Div([
    html.H1("Yearly Simulation"),
    html.Div([
        html.Table([
            html.Tr([html.Td("Place to Simulate: "), html.Td(dcc.Dropdown(
                list(demand_files.keys()),
                id='place_to_research'
            ))]),
            html.Tr([html.Td("Year to simulate: "),
                     html.Td(dbc.Input(id='year_to_simulate', value='2020', type='number'))]),
            html.Tr([html.Td("Use Strategy: "), html.Td(dcc.Dropdown(
                list(use_strategies.keys()),
                id='use_strategy'
            ))]),
            html.Tr([html.Td("Number of Batteries: "),
                     html.Td(dbc.Input(id='number_batteries', value='3', type='number'))]),
            html.Tr([html.Td("Solar panel max KW: "),
                     html.Td(dbc.Input(id='solar_panel_power_kw', value='6000', type='number'))]),
        ]),
        dbc.Button(id='run_simulation_button', children='Run Simulation', n_clicks=0)
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
)
def run_simulation(n_clicks, num_batteries, solar_panel_power_kw, simulated_year, chosen_strategy, place_to_research):
    solar_panel_power_kw = float(solar_panel_power_kw)
    num_batteries = float(num_batteries)
    simulated_year = int(simulated_year)
    if not place_to_research or not chosen_strategy:
        raise PreventUpdate
    demand = DemandDf(pd.read_csv(demand_files[place_to_research], index_col=0))
    normalised_panel_production = ProductionDf(NORMALISED_SOLAR_PRODUCTION.df.copy())
    electricity_use = get_usage_profile(demand, normalised_panel_production, solar_panel_power_kw, num_batteries,
                                        use_strategies[chosen_strategy], simulated_year)
    return yearly_graph_fig(electricity_use.df, num_hours_to_sum=1)


def main():
    app.run_server(host="0.0.0.0")
