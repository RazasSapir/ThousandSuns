import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Iterator

from df_objects.df_objects import SimulationResults

GAS_USAGE = 'GasUsage'
SOLAR_USAGE = 'SolarUsage'
STORED_USAGE = 'StoredUsage'
SOLAR_STORED = 'SolarStored'
SOLAR_LOST = 'SolarLost'

STORED_STATE = 'StoredState'
USAGE_SUM = 'UsageSum'

yearly_stats_labels = [GAS_USAGE, SOLAR_USAGE, STORED_USAGE,
                       SOLAR_STORED, SOLAR_LOST]

names = {
    GAS_USAGE: 'Gas Based Electricity Consumption',
    SOLAR_USAGE: 'Solar Energy Consumption',
    STORED_USAGE: 'Stored Solar Energy Consumption',
    SOLAR_STORED: 'Stored Solar Energy',
    SOLAR_LOST: 'Lost Solar Energy',
    STORED_STATE: 'Batteries Charge',
    USAGE_SUM: 'Total Energy Consumption'
}

colors = {
    GAS_USAGE: '#999999',
    SOLAR_USAGE: '#00FF00',
    STORED_USAGE: '#00bcd4',
    SOLAR_STORED: '#FFC300',
    SOLAR_LOST: '#2f2f2f',
    STORED_STATE: '#bc00d4',
    USAGE_SUM: '#b33b3b'
}

OPACITY = 0.85
HOVERINFO = 'x+y'
LINES = 'lines'
WIDTH = 0.5
THICK_WIDTH = 3.5
STACKGROUP_ONE = 'one'
STACKGROUP_TWO = 'two'
STACKGROUP_THREE = 'three'
DASH = 'dash'

HOURS_IN_DAY = 24


# todo: remove strings with constants
# todo: add battery level line
# todo: add demand line as sum of all usage values
# todo: add docstring
def yearly_graph_fig(yearly_stats: pd.DataFrame, batteries_num, batteries_cap,
                     num_hours_to_sum=1):
    x = [f"{(i//HOURS_IN_DAY) + 1} ({i%HOURS_IN_DAY + 1})"
         for i in range(len(yearly_stats.index))]

    yearly_stats = yearly_stats.groupby(yearly_stats.index // num_hours_to_sum).sum()

    usage_sum = [solar + gas + stored for (solar, gas, stored) in zip(
        yearly_stats[SOLAR_USAGE],
        yearly_stats[GAS_USAGE],
        yearly_stats[STORED_USAGE])]

    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True, row_heights=[0.4, 0.6])

    labeled_scatters = []
    for label in yearly_stats_labels:
        labeled_scatters.append(
            go.Scatter(x=x, y=yearly_stats[label], name=names[label],
                       marker_color=colors[label],
                       opacity=OPACITY, hoverinfo=HOVERINFO, mode=LINES,
                       line=dict(width=WIDTH, color=colors[label]),
                       stackgroup=STACKGROUP_ONE)
        )
        battery_state_scatter = go.Scatter(
            x=x, y=stored_state_stats(yearly_stats, batteries_num, batteries_cap),
            name=names[STORED_STATE],
            marker_color=colors[STORED_STATE],
            opacity=OPACITY,
            hoverinfo=HOVERINFO,
            mode=LINES,
            line=dict(width=WIDTH, color=colors[STORED_STATE]),
            stackgroup=STACKGROUP_TWO)

        usage_sum_scatter = go.Scatter(
            x=x, y=usage_sum,
            name=names[USAGE_SUM],
            marker_color=colors[USAGE_SUM],
            opacity=OPACITY, hoverinfo=HOVERINFO, mode=LINES,
            line=dict(width=THICK_WIDTH, color=colors[USAGE_SUM], dash=DASH)
        )

    fig.add_trace(battery_state_scatter, row=1, col=1)
    fig.add_traces(labeled_scatters + [usage_sum_scatter], rows=2, cols=1)
    fig.update_xaxes(matches='x')
    fig.update_xaxes(title_text="Day(hour)", row=2, col=1)
    fig.update_yaxes(title_text="percentage %", row=1, col=1)
    fig.update_yaxes(title_text="kWh", row=2, col=1)

    fig.update_layout(barmode='stack', title='Day Usage')
    return fig


def normalize_battery(num, batteries_num, batteries_cap):
        return (100*num)/(batteries_num*batteries_cap)


def stored_state_stats(yearly_stats, batteries_num, batteries_cap):
    stored_state = [yearly_stats['SolarStored'][0] -
                    yearly_stats['StoredUsage'][0]]
    for i in range(1, len(yearly_stats.index)):
        difference = yearly_stats['SolarStored'][i] - \
                     yearly_stats['StoredUsage'][i]
        difference = normalize_battery(difference,
                                       batteries_num,
                                       batteries_cap)
        stored_state.append(stored_state[i - 1] + difference)

    return stored_state


def yearly_graph(yearly_stats: pd.DataFrame, batteries_num,
                 batteries_cap, num_hours_to_sum=1):
    yearly_graph_fig(yearly_stats, batteries_num,
                     batteries_cap, num_hours_to_sum).show()


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
    fig.update_xaxes(title_text="number of batteries", row=1, col=1)
    fig.update_yaxes(title_text="Max solar panel power [kw]", row=1, col=1)
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
