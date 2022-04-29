import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from df_objects.df_objects import *
from typing import Iterator

labels = ['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost']
colors = {
    'GasUsage': '#999999',
    'SolarUsage': '#00FF00',
    'StoredUsage': '#00bcd4',
    'SolarStored': '#FFC300',
    'SolarLost': '#2f2f2f'
}


# todo: remove strings with constants
# todo: add battery level line
# todo: add demand line as sum of all usage values
# todo: add docstring
def yearly_graph_fig(yearly_stats: pd.DataFrame, num_hours_to_sum=1):
    x = [i for i in range(len(yearly_stats.index) + 1)]
    yearly_stats = yearly_stats.groupby(yearly_stats.index // num_hours_to_sum).sum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['GasUsage'], name='GasUsage', marker_color=colors['GasUsage'],
                             opacity=0.85, hoverinfo='x+y', mode='lines',
                             line=dict(width=0.5, color=colors['GasUsage']),
                             stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['SolarUsage'], name='SolarUsage', marker_color=colors['SolarUsage'],
                             opacity=0.85, hoverinfo='x+y', mode='lines',
                             line=dict(width=0.5, color=colors['SolarUsage']),
                             stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['StoredUsage'], name='StoredUsage', marker_color=colors['StoredUsage'],
                             opacity=0.85, hoverinfo='x+y', mode='lines',
                             line=dict(width=0.5, color=colors['StoredUsage']),
                             stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['SolarStored'], name='SolarStored', marker_color=colors['SolarStored'],
                             opacity=0.85, hoverinfo='x+y', mode='lines',
                             line=dict(width=0.5, color=colors['SolarStored']),
                             stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['SolarLost'], name='SolarLost', marker_color=colors['SolarLost'],
                             opacity=0.85, hoverinfo='x+y', mode='lines',
                             line=dict(width=0.5, color=colors['SolarLost']),
                             stackgroup='one'))
    fig.update_layout(barmode='stack'
                      , title='Day Usage'
                      , xaxis_title='Day In Year'
                      , yaxis_title='Usage (kWh)')
    return fig


def yearly_graph(yearly_stats: pd.DataFrame, num_hours_to_sum=1):
    yearly_graph_fig(yearly_stats, num_hours_to_sum).show()


def daily_graph(daily_stats: pd.DataFrame):
    x = [i for i in range(1, 25)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=daily_stats['GasUsage'], name='GasUsage', marker_color=colors['GasUsage'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['SolarUsage'], name='SolarUsage', marker_color=colors['SolarUsage'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['StoredUsage'], name='StoredUsage', marker_color=colors['StoredUsage'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['SolarStored'], name='SolarStored', marker_color=colors['SolarStored'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['SolarLost'], name='SolarLost', marker_color=colors['SolarLost'],
                         opacity=0.85))
    fig.update_layout(barmode='stack'
                      , title='Daily Usage'
                      , xaxis_title='Hour in Day'
                      , yaxis_title='Usage (kWh)')
    fig.show()


def simulation_graph(simulation_results: SimulationResults, solar_panel_power_it: Iterator, num_batteries_it: Iterator):
    """
    Graphics of the whole simulation 3d graph + 2d contour of number of batteries and power of solar panels to scenario cost
    :param simulation_results: SimulationResults of pd.DataFrame ['PowerSolar', 'NumBatteries', 'Cost']
    :param solar_panel_power_it: iterator for different solar panels
    :param num_batteries_it: iterator for different battery sizes
    :return: plotly figure :)
    """

    z = simulation_results.df[simulation_results.Cost].to_numpy().reshape(len(list(solar_panel_power_it)),
                                                                          len(list(num_batteries_it)))

    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'scatter'}, {'type': 'scene'}]])

    fig.add_traces(data=[
        go.Contour(z=z, x=num_batteries_it, y=solar_panel_power_it, colorscale='Electric', showscale=False),
        go.Surface(x=num_batteries_it, y=solar_panel_power_it, z=z, opacity=.8, colorscale='Electric',
                   contours=dict(z=dict(show=True)))],
        rows=[1, 1], cols=[1, 2])
    fig.update_xaxes(title_text="N batteries", row=1, col=1)
    fig.update_yaxes(title_text="Max solar panel power kw", row=1, col=1)
    return fig


if __name__ == '__main__':
    data = pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    df_len = (365 * 24)
    data['GasUsage'] = np.random.normal(20, 3, df_len)
    data['SolarUsage'] = np.random.normal(18, 4, df_len)
    data['StoredUsage'] = np.random.normal(5, 1, df_len)
    data['SolarStored'] = np.random.normal(5, 1, df_len)
    data['SolarLost'] = np.random.normal(3, 1, df_len)
    yearly_graph(data)
