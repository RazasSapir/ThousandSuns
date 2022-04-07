import numpy as np
import pandas as pd


def yearly_graph():
    pass


def daily_graph():
    pass


if __name__ == '__main__':
    data = pd.DataFrame(columns=['GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored', 'SolarLost'])
    data['GasUsage'] = np.random.normal(20, 3, 24)
    data['SolarUsage'] = np.random.normal(18, 4, 24)
    data['StoredUsage'] = np.random.normal(5, 1, 24)
    data['SolarStored'] = np.random.normal(5, 1, 24)
    data['SolarLost'] = np.random.normal(3, 1, 24)
    daily_graph(data)
