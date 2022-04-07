import plotly.graph_objects as go
import pandas as pd
import numpy as np

labels = ['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost']
colors = {
    'GasUsage': '#999999',
    'SolarUsage': '#00FF00',
    'StoredUsage': '#00bcd4',
    'SolarStored': '#FFC300',
    'SolarLost': '#2f2f2f'
}


def yearly_graph(yearly_stats: pd.DataFrame):
    x = [i for i in range(len(yearly_stats.index) + 1)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['GasUsage'], name='GasUsage', marker_color=colors['GasUsage'],
                             opacity=0.85, hoverinfo='x+y', mode='lines', line=dict(width=0.5, color=colors['GasUsage']),
    stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['SolarUsage'], name='SolarUsage', marker_color=colors['SolarUsage'],
                         opacity=0.85, hoverinfo='x+y', mode='lines', line=dict(width=0.5, color=colors['SolarUsage']),
    stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['StoredUsage'], name='StoredUsage', marker_color=colors['StoredUsage'],
                         opacity=0.85, hoverinfo='x+y', mode='lines', line=dict(width=0.5, color=colors['StoredUsage']),
    stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['SolarStored'], name='SolarStored', marker_color=colors['SolarStored'],
                         opacity=0.85, hoverinfo='x+y', mode='lines', line=dict(width=0.5, color=colors['SolarStored']),
    stackgroup='one'))
    fig.add_trace(go.Scatter(x=x, y=yearly_stats['SolarLost'], name='SolarLost', marker_color=colors['SolarLost'],
                         opacity=0.85, hoverinfo='x+y', mode='lines', line=dict(width=0.5, color=colors['SolarLost']),
    stackgroup='one'))
    fig.update_layout(barmode='stack'
                      , title='Yearly Usage'
                      , xaxis_title='Day'
                      , yaxis_title='Usage (kWh)')
    fig.show()


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
                      , xaxis_title='Day'
                      , yaxis_title='Usage (kWh)')

    fig.show()


if __name__ == '__main__':
    data = pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    data['GasUsage'] = np.random.normal(20, 3, (365 // 7))
    data['SolarUsage'] = np.random.normal(18, 4, (365 // 7))
    data['StoredUsage'] = np.random.normal(5, 1, (365 // 7))
    data['SolarStored'] = np.random.normal(5, 1, (365 // 7))
    data['SolarLost'] = np.random.normal(3, 1, (365 // 7))
    yearly_graph(data)
