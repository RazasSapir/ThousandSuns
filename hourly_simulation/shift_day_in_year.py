import datetime
import numpy as np

def shift_day_of_year(arr, year):
    day_num = int(datetime.datetime(year, 1, 1).strftime("%w"))
    return np.roll(arr, -day_num * 24)

