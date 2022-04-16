import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State

from hourly_simulation import strategies
from hourly_simulation.simulation import *
from output_graphs.hourly_graph_creator import *

app = Dash(external_stylesheets=[dbc.themes.JOURNAL])

app.layout = html.Div([
    html.H1("Yearly Simulation"),
    html.Div([
        html.Table([
            html.Tr(
                [html.Td("Number of Batteries: "), html.Td(dcc.Input(id='number_batteries', value='3', type='text'))]),
            html.Tr([html.Td("Solar panel max KW: "),
                     html.Td(dcc.Input(id='solar_panel_power_kw', value='6000', type='text'))]),
            html.Tr([html.Td("Use Strategy: "), html.Td(dcc.Dropdown(
                ["Greedy Use Strategy"],
                'Use Strategy',
                id='use_strategy'
            ))]),
            html.Tr([html.Td("Base: "), html.Td(dcc.Dropdown(
                ["חצור"],
                'Base',
                id='base_to_research'
            ))]),
            html.Tr([html.Button(id='run_simulation_button', children='Run Simulation', n_clicks=0)]),
        ]),
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
    State(component_id='solar_panel_power_kw', component_property='value')
)
def run_simulation(n_clicks, num_batteries_val, solar_panel_power_kw_val):
    solar_panel_power_kw = float(solar_panel_power_kw_val)
    num_batteries = float(num_batteries_val)
    demand = DemandDf(pd.read_csv(r'../data/consumption_hatzor.csv', index_col=0))
    future_demand = predict_demand_in_year(demand, 2020)
    total_panel_production = ProductionDf(NORMALISED_SOLAR_PRODUCTION.df.copy())
    total_panel_production.df[total_panel_production.SolarProduction] *= solar_panel_power_kw
    electricity_use: ElectricityUseDf = strategies.better_use_strategy(future_demand, total_panel_production,
                                                                       BATTERY_CAPACITY * num_batteries,
                                                                       CHARGE_POWER * num_batteries)
    return yearly_graph_fig(electricity_use.df, num_hours_to_sum=1)


def main():
    app.run_server(debug=True, host="0.0.0.0")


if __name__ == '__main__':
    main()
