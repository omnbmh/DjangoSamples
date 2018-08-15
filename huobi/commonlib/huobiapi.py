# -*- coding: utf-8 -*-

from huobi_rest_api import HuobiService


def get_kline(symbol, period, size):
    return HuobiService.get_kline(symbol, period, size)
