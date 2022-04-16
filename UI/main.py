import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output

from hourly_simulation import strategies
from hourly_simulation.simulation import *
from output_graphs.hourly_graph_creator import *

app = Dash(external_stylesheets=[dbc.themes.JOURNAL])

app.layout = html.Div([
    html.H1("Yearly Simulation"),
    html.Div([
        html.Table([
            html.Tr(["Number of Batteries: ", html.Td(dcc.Input(id='number_batteries', value='3', type='text'))]),
            html.Tr(["Solar panel max KW: ", html.Td(dcc.Input(id='solar_panel_power_kw', value='6000', type='text'))]),
        ]),
    ]),
    html.Br(),
    dcc.Loading(
        id="loading",
        type="default",
        children=[dcc.Graph(id='yearly_graph'), html.H4("?", id="cost_scenario")]
    ),
], style={"padding": "1rem"})


@app.callback(
    Output('yearly_graph', 'figure'),
    Output('cost_scenario', 'children'),
    Input(component_id='number_batteries', component_property='value'),
    Input(component_id='solar_panel_power_kw', component_property='value')
)
def update_output_div(num_batteries_val, solar_panel_power_kw_val):
    solar_panel_power_kw = float(solar_panel_power_kw_val)
    num_batteries = float(num_batteries_val)
    demand = DemandDf(pd.read_csv(r'../data/consumption_hatzor.csv', index_col=0))
    future_demand = predict_demand_in_year(demand, 2020)
    total_panel_production = ProductionDf(NORMALISED_SOLAR_PRODUCTION.df.copy())
    total_panel_production.df[total_panel_production.SolarProduction] *= solar_panel_power_kw
    electricity_use: ElectricityUseDf = strategies.better_use_strategy(future_demand, total_panel_production,
                                                                       BATTERY_CAPACITY * num_batteries,
                                                                       CHARGE_POWER * num_batteries)
    return yearly_graph_fig(electricity_use.df, num_hours_to_sum=1), \
           "Approximated Cost: {:,} ILS".format(calculate_cost(electricity_use,
                                                               BATTERY_CAPACITY * num_batteries,
                                                               solar_panel_power_kw, time_span=25) // 10000 * 10000)


def main():
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
