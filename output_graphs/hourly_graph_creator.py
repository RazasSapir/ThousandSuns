import copy
from typing import Iterator

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from df_objects.df_objects import SimulationResults, DemandDf
from hourly_simulation.parameters import Params, get_simulation_parameters, PARAMS_PATH
from hourly_simulation.shift_day_in_year import shift_day_of_year

GAS_USAGE = 'GasUsage'
SOLAR_USAGE = 'SolarUsage'
STORED_USAGE = 'StoredUsage'
USAGE_SUM = 'UsageSum'

SOLAR_SOLD = 'SolarSold'
STORED_SOLD = 'StoredSold'

STORED_CONSUMERS = [STORED_USAGE,
                    STORED_SOLD]

SOLAR_STORED = 'SolarStored'
GAS_STORED = 'GasStored'
STORED_STATE = 'StoredState'

ENERGY_COLLECTORS = [SOLAR_STORED, GAS_STORED]

SOLAR_LOST = 'SolarLost'

USAGE_PRODUCTION_LABELS = [GAS_USAGE, SOLAR_USAGE, STORED_USAGE,
                           SOLAR_STORED, SOLAR_LOST]

BUY_SELL_LABELS = [STORED_SOLD, SOLAR_SOLD, GAS_STORED]

NAMES = {
    GAS_USAGE: 'Gas Based Electricity Consumption',
    SOLAR_USAGE: 'Solar Energy Consumption',
    STORED_USAGE: 'Stored Solar Energy Consumption',
    SOLAR_STORED: 'Stored Solar Energy',
    SOLAR_LOST: 'Lost Solar Energy',
    STORED_STATE: 'Batteries Charge',
    USAGE_SUM: 'Total Energy Consumption',
    SOLAR_SOLD: "Solar Energy Sold",
    GAS_STORED: "Gas Energy Bought and Stored",
    STORED_SOLD: "Stored Energy Sold"
}

COLORS = {
    GAS_USAGE: '#909090',
    GAS_STORED: '#909090',

    SOLAR_USAGE: '#FFE000',
    SOLAR_STORED: '#FFE000',
    SOLAR_SOLD: '#50FF00',
    SOLAR_LOST: '#000000',

    STORED_USAGE: '#ADD8E6',
    STORED_STATE: '#ADD8E6',
    STORED_SOLD: '#00B838',

    USAGE_SUM: '#FF2020',
}

FILL_PATTERN = {
    GAS_USAGE: '',
    GAS_STORED: '/',


    SOLAR_USAGE: '',
    SOLAR_STORED: '/',
    SOLAR_SOLD: '',
    SOLAR_LOST: '/',

    STORED_USAGE: '',
    STORED_STATE: '/',
    STORED_SOLD: '/',
}

HIDE_BATTERY_EFFICIENCY_LOSS = True
OPACITY = 1
HOVERINFO = 'x+y'
LINES = 'lines'
WIDTH = 0.5
THICK_WIDTH = 2.5
STACKGROUP_ONE = 'one'
STACKGROUP_TWO = 'two'
STACKGROUP_THREE = 'three'
DASH = 'solid'

BATTERY_PLOT_POSITION = (1, 1)
BUY_SELL_PLOT_POSITION = (2, 1)
USAGE_PRODUCTION_PLOT_POSITION = (3, 1)

HOURS_IN_DAY = 24


# todo: add docstring and docstring
def yearly_graph_fig(yearly_stats: pd.DataFrame,
                     batteries_effecitive_cap, demand: DemandDf, demand_year,
                     num_hours_to_sum=1):
    yearly_stats = copy.deepcopy(yearly_stats)
    x = []
    for i in range(len(yearly_stats.index)):
        x.append(f"{(i // HOURS_IN_DAY) + 1} ({i % HOURS_IN_DAY + 1})")
        x.append(f"{(i // HOURS_IN_DAY) + 1} ({i % HOURS_IN_DAY + 1})")

    wanted_simulation_params = Params(**get_simulation_parameters(PARAMS_PATH))
    batter_eff = wanted_simulation_params.BATTERY_EFFICIENCY
    if HIDE_BATTERY_EFFICIENCY_LOSS:
        yearly_stats[SOLAR_LOST] -= yearly_stats[SOLAR_STORED] / batter_eff * (1 - batter_eff)

    yearly_stats = yearly_stats.groupby(
        yearly_stats.index // num_hours_to_sum).sum()

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True, row_heights=[0.2, 0.3, 0.5],
                        vertical_spacing=0.01)

    usage_production_scatters = []
    for label in USAGE_PRODUCTION_LABELS:
        usage_production_scatters.append(
            go.Scatter(x=x, y=double_stat(yearly_stats[label]), name=NAMES[label],
                       fillcolor=COLORS[label],
                       fillpattern={'shape': FILL_PATTERN[label],
                                    'fgcolor': "#FFFFFF"},
                       opacity=OPACITY, hoverinfo=HOVERINFO,
                       mode=LINES,
                       line=dict(width=0, color=COLORS[label]),
                       stackgroup=STACKGROUP_ONE)
        )

    buy_sell_scatters = []
    for label in BUY_SELL_LABELS:
        buy_sell_scatters.append(
            go.Scatter(x=x, y=double_stat(yearly_stats[label]), name=NAMES[label],
                       fillcolor=COLORS[label],
                       fillpattern={'shape': FILL_PATTERN[label],
                                    'fgcolor': "#FFFFFF"},
                       opacity=OPACITY, hoverinfo=HOVERINFO, mode=LINES,
                       line=dict(width=0, color=COLORS[label]),
                       stackgroup=STACKGROUP_ONE
                       )
        )

    battery_state_scatter = go.Scatter(
        x=x,
        y=double_stat(stored_state_stats(yearly_stats, batteries_effecitive_cap)),
        name=NAMES[STORED_STATE],
        fillcolor=COLORS[STORED_STATE],
        fillpattern={'shape': FILL_PATTERN[STORED_STATE], 'fgcolor': "#FFFFFF"},
        hoverinfo=HOVERINFO,
        mode=LINES,
        line=dict(width=WIDTH, color=COLORS[STORED_STATE]),
        stackgroup=STACKGROUP_ONE
    )

    usage_sum_scatter = go.Scatter(
        x=x, y=double_stat(shift_day_of_year(demand.df[demand.Demand], demand_year)),
        name=NAMES[USAGE_SUM],
        marker_color=COLORS[USAGE_SUM],
        opacity=OPACITY,
        hoverinfo=HOVERINFO,
        mode=LINES,
        line=dict(width=THICK_WIDTH, color=COLORS[USAGE_SUM], dash=DASH)
    )
    fig.add_traces(usage_production_scatters + [usage_sum_scatter],
                   rows=USAGE_PRODUCTION_PLOT_POSITION[0],
                   cols=USAGE_PRODUCTION_PLOT_POSITION[1])

    fig.add_traces(buy_sell_scatters,
                   rows=BUY_SELL_PLOT_POSITION[0],
                   cols=BUY_SELL_PLOT_POSITION[1]
                   )

    fig.add_trace(battery_state_scatter,
                  row=BATTERY_PLOT_POSITION[0],
                  col=BATTERY_PLOT_POSITION[1]
                  )

    fig.update_xaxes(matches='x')
    # fig.update_xaxes(title_text="Day(hour)")
    fig.update_yaxes(title_text="percentage %",
                     row=BATTERY_PLOT_POSITION[0],
                     col=BATTERY_PLOT_POSITION[1]
                     )
    fig.update_yaxes(title_text="kWh",
                     row=BUY_SELL_PLOT_POSITION[0],
                     col=BUY_SELL_PLOT_POSITION[1]
                     )
    fig.update_yaxes(title_text="kWh",
                     row=USAGE_PRODUCTION_PLOT_POSITION[0],
                     col=USAGE_PRODUCTION_PLOT_POSITION[1]
                     )

    fig.update_layout(barmode='stack', title='Daily Electricity Management',
                      height=670)
    return fig


def stored_state_stats(yearly_stats, batteries_effective_cap):
    if batteries_effective_cap == 0:
        return [0] * len(yearly_stats.index)
    stored_state = [
        normalize_battery(get_collection(0, yearly_stats) - get_consumption(0, yearly_stats), batteries_effective_cap)]
    for i in range(1, len(yearly_stats.index)):
        difference = get_collection(i, yearly_stats) - get_consumption(i, yearly_stats)
        difference = normalize_battery(difference,
                                       batteries_effective_cap)
        stored_state.append(stored_state[-1] + difference)

    return stored_state


def get_consumption(index, yearly_stats):
    consumption = 0
    for consumer in STORED_CONSUMERS:
        consumption += yearly_stats[consumer][index]
    return consumption


def get_collection(index, yearly_stats):
    collection = 0
    for collector in ENERGY_COLLECTORS:
        collection += yearly_stats[collector][index]
    return collection


def normalize_battery(num, batteries_effective_cap):
    return (100 * num) / batteries_effective_cap


def double_stat(stat):
    doubled_stat = []
    for i in range(len(stat) - 1):
        doubled_stat.append(stat[i])
        doubled_stat.append(stat[i+1])
    return doubled_stat


def yearly_graph(yearly_stats: pd.DataFrame, batteries_num, batteries_cap,
                 demand: DemandDf, demand_year, num_hours_to_sum=1):
    yearly_graph_fig(yearly_stats, batteries_cap, demand,
                     demand_year, num_hours_to_sum).show()


def daily_graph(daily_stats: pd.DataFrame):
    x = [i for i in range(1, 25)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=daily_stats['GasUsage'], name='GasUsage',
                         marker_color=COLORS['GasUsage'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['SolarUsage'], name='SolarUsage',
                         marker_color=COLORS['SolarUsage'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['StoredUsage'], name='StoredUsage',
                         marker_color=COLORS['StoredUsage'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['SolarStored'], name='SolarStored',
                         marker_color=COLORS['SolarStored'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['SolarLost'], name='SolarLost',
                         marker_color=COLORS['SolarLost'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['SolarSold'], name='SolarSold',
                         marker_color=COLORS['SolarSold'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['GasStored'], name='GasStored',
                         marker_color=COLORS['GasStored'],
                         opacity=0.85))
    fig.add_trace(go.Bar(x=x, y=daily_stats['StoredSold'], name='StoredSold',
                         marker_color=COLORS['StoredSold'],
                         opacity=0.85))
    fig.update_layout(barmode='stack'
                      , title='Daily Usage'
                      , xaxis_title='Hour in Day'
                      , yaxis_title='Usage (mWh)')
    fig.show()


def simulation_graph(simulation_results: SimulationResults,
                     solar_panel_power_it: Iterator,
                     num_batteries_it: Iterator):
    """
    Graphics of the whole simulation 3d graph + 2d contour of number of batteries and power of solar panels to scenario cost
    :param simulation_results: SimulationResults of pd.DataFrame ['PowerSolar', 'NumBatteries', 'Cost']
    :param solar_panel_power_it: iterator for different solar panels
    :param num_batteries_it: iterator for different battery sizes
    :return: plotly figure :)
    """

    z = simulation_results.df[simulation_results.Cost].to_numpy().reshape(
        len(list(solar_panel_power_it)),
        len(list(num_batteries_it)))

    fig = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'scatter'}, {'type': 'scene'}]])

    fig.add_traces(data=[
        go.Contour(z=z, x=num_batteries_it, y=solar_panel_power_it,
                   colorscale='Electric', showscale=False),
        go.Surface(x=num_batteries_it, y=solar_panel_power_it, z=z, opacity=.8,
                   colorscale='Electric',
                   contours=dict(z=dict(show=True)))],
        rows=[1, 1], cols=[1, 2])
    fig.update_layout(scene=dict(
        xaxis_title='number of batteries',
        yaxis_title='Max solar panel [mw]',
        zaxis_title='Cost [ILS]'))
    fig.update_xaxes(title_text="number of batteries", row=1, col=1)
    fig.update_yaxes(title_text="Max solar panel power [mw]", row=1, col=1)
    return fig
