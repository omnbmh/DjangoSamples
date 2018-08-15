# -*- coding: utf-8 -*-

import numpy as np
import datetime
import time

C_CLOSE = 'close'
C_OPEN = 'open'
C_HIGH = 'high'
C_LOW = 'low'


def avg_high_low(num_array):
    return round((np.max(num_array) + np.min(num_array)) / 2, 13)


def avg_close(data):
    return avg(data)


def avg(data):
    return round(np.average(data), 13)


def std_close(data):
    return std(data)


def std(data):
    return round(np.std(data), 13)


def var(data):
    return round(np.mean(data), 13)


def trend(data):
    num_arr = []
    for i in range(len(data)):
        num_arr.append(str(round((float(data[i][C_CLOSE]) - float(data[i][C_OPEN])) / float(data[i][C_OPEN]), 4)))
    return num_arr


def trend_std(data):
    num_arr = []
    for i in range(len(data)):
        num_arr.append(round((float(data[i][C_CLOSE]) - float(data[i][C_OPEN])) / float(data[i][C_OPEN]), 4))
    return round(np.std(num_arr), 13)


def return_rate(row_data):
    return round((float(row_data[C_CLOSE]) - float(row_data[C_OPEN])) / float(row_data[C_OPEN]), 4)


def add_days(dt, days):
    new_dt = dt + datetime.timedelta(days=days)
    # return  new_dt.strftime("%Y-%m-%d %H:%M:%S")
    return new_dt.strftime("%Y-%m-%d")


def add_days_fmt(dt, days, fmt):
    new_dt = dt + datetime.timedelta(days=days)
    return new_dt.strftime(fmt)


def add_hours(dt, days):
    new_dt = dt + datetime.timedelta(hours=days)
    # return  new_dt.strftime("%Y-%m-%d %H:%M:%S")
    return new_dt.strftime("%Y-%m-%d %H")


def ts2datetime(ts):
    return ts2datetime_fmt(ts, '%Y-%m-%d %H:%M:%S')


def ts2datetime_fmt(ts, fmt):
    st = time.localtime(ts)
    return time.strftime(fmt, st)
