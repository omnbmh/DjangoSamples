# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger("django")

from django.db import models
from commonlib import common_calc


# Create your models here.

class KlineHistory(models.Model):
    '''
    kline数据历史 用于分析
    '''
    id = models.CharField(max_length=100, verbose_name='ID', primary_key=True)
    symbol = models.CharField(max_length=100, verbose_name='交易币种')  # usdtbtc
    period = models.CharField(max_length=100, verbose_name='周期')
    col_amount = models.CharField(max_length=100, verbose_name='成交量', default='0')
    col_count = models.CharField(max_length=100, verbose_name='成交笔数', default='0')
    col_open = models.CharField(max_length=100, verbose_name='开盘价', default='0')
    col_close = models.CharField(max_length=100, verbose_name='收盘价', default='0')
    col_low = models.CharField(max_length=100, verbose_name='最低价', default='0')
    col_high = models.CharField(max_length=100, verbose_name='最高价', default='0')
    col_vol = models.CharField(max_length=100, verbose_name='成交额', default='0')
    col_updown_vol = models.CharField(max_length=100, verbose_name='涨跌额', default='0')
    col_updown_rate = models.CharField(max_length=100, verbose_name='涨跌幅', default='0')
    # data_key = models.CharField(max_length=100, verbose_name='数据key')
    # data_value = models.CharField(max_length=100, verbose_name='数据')
    created_at = models.CharField(max_length=100, verbose_name='数据产生时间 非入库时间')  # timestamp 转成 yyyy-mm-dd-hh-mm-ss

    class Meta:
        abstract = True

    @classmethod
    def create(cls):
        kh = cls()
        return kh


class KlineHistoryBTCUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_btc_usdt'


class KlineHistoryETHUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_eth_usdt'


class KlineHistoryHTUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_ht_usdt'


class KlineHistoryEOSUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_eos_usdt'


class KlineHistoryBCHUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_bch_usdt'


class KlineHistoryXRPUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_xrp_usdt'


class KlineHistoryETCUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_etc_usdt'


class KlineHistoryIOSTUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_iost_usdt'


class KlineHistoryLTCUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_ltc_usdt'


class KlineHistoryELFUSDT(KlineHistory):
    class Meta:
        db_table = 'kline_history_elf_usdt'


KLINE_HISTORY_SHARFING_MAP = {
    'btcusdt': KlineHistoryBTCUSDT,
    'ethusdt': KlineHistoryETHUSDT,
    'eosusdt': KlineHistoryEOSUSDT,
    'ltcusdt': KlineHistoryLTCUSDT,
    'bchusdt': KlineHistoryBCHUSDT,
    'elfusdt': KlineHistoryELFUSDT,
    'iostusdt': KlineHistoryIOSTUSDT,
    'etcusdt': KlineHistoryETCUSDT,
    'xrpusdt': KlineHistoryXRPUSDT,
    'htusdt': KlineHistoryHTUSDT,
}


def save_db_kline_history(symbol, period, row_data):
    if symbol not in KLINE_HISTORY_SHARFING_MAP:
        logger.warn('ERROR !!! not support ' + symbol + ' kline history save !!!')
        return

    id = period + str(row_data['id'])
    created_at = common_calc.ts2datetime_fmt(row_data['id'], '%Y%m%d%H%M%S')

    return_rate = common_calc.return_rate(row_data)

    logger.info(u" 币种 %s 时间 %s 开 %s 收 %s 利率 %s 成交量 %s" % (
        symbol, created_at, str(row_data['close']), str(row_data['open']), str(return_rate),
        str(row_data['amount'])))

    khobject = KLINE_HISTORY_SHARFING_MAP[symbol]
    cache_kh_list = khobject.objects.filter(id=id)
    if cache_kh_list and len(cache_kh_list) > 0:
        kh = cache_kh_list[0]

    else:
        kh = khobject.create()
        kh.id = id
        kh.symbol = symbol
        kh.period = period
        kh.created_at = created_at

    kh.col_amount = row_data['amount']
    kh.col_count = row_data['count']
    kh.col_open = row_data['open']
    kh.col_close = row_data['close']
    kh.col_low = row_data['low']
    kh.col_high = row_data['high']
    kh.col_vol = row_data['vol']
    kh.col_updown_rate = return_rate
    kh.col_updown_vol = float(row_data['close']) - float(row_data['open'])
    kh.save()

# def save_db_kline_history(trade_name, period, key, value, created_at):
#     if trade_name not in KLINE_HISTORY_SHARFING_MAP:
#         logger.info('ERROR !!! unsupport ' + trade_name + ' kline history save !!!')
#         return
#
#     khobject = KLINE_HISTORY_SHARFING_MAP[trade_name]
#     cache_kh_list = khobject.objects.filter(trade_name=trade_name, period=period, data_key=key,
#                                             created_at=created_at)
#     if cache_kh_list and len(cache_kh_list) > 0:
#         kh = cache_kh_list[0]
#         kh.data_value = value
#         kh.created_at = created_at
#         kh.save()
#     else:
#         kh = khobject.create()
#         kh.trade_name = trade_name
#         kh.period = period
#         kh.data_key = key
#         kh.data_value = value
#         kh.created_at = created_at
#         kh.save()
#     # logger.info('cache_data_save ' + period + ' ' + trade_name + ' ' + key + ' ' + value)
