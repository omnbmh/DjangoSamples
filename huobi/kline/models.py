# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import logging
import json

reload(sys)
sys.setdefaultencoding('utf-8')
logger = logging.getLogger("django")

from django.db import models

# Create your models here.
import time
import datetime
from orders.models import Symbol
from orders import HuobiService, common_calc


class KlineHistory(models.Model):
    '''
    kline数据历史 用于分析
    '''
    trade_name = models.CharField(max_length=100, verbose_name='交易币种')
    period = models.CharField(max_length=100, verbose_name='周期')
    data_key = models.CharField(max_length=100, verbose_name='数据key')
    data_value = models.CharField(max_length=100, verbose_name='数据')
    created_at = models.CharField(max_length=100, verbose_name='数据产生时间 非入库时间')


def save_kline_history(period, size):
    symbol_list = Symbol.objects.filter(quote_currency='usdt')
    for symbol in symbol_list:
        rlt_json = HuobiService.get_kline(symbol.trade_name, period, size)
        if rlt_json[u'status'] == 'ok':
            for i in range(len(rlt_json[u'data'])):
                offset = i
                row_data = rlt_json[u'data'][offset]
                if '1day' == period:
                    return_rate = common_calc.return_rate(row_data)
                    created_at = common_calc.add_days(datetime.datetime.now(), 0 - i)
                    logger.info(u" 币种 %s 时间 %s 开 %s 收 %s 利率 %s" % (
                        symbol.trade_name, created_at, str(row_data['close']), str(row_data['open']), str(return_rate)))
                    save_db_kline_history(symbol.trade_name, period, 'return_rate', return_rate, created_at)
            logger.info(u'缓存数据 %s %s %s 完成' % (symbol.trade_name, period, created_at))
    logger.info(u'缓存数据 %s %d 完成' % (period, size))
    time.sleep(5)


def save_db_kline_history(trade_name, period, key, value, created_at):
    cache_data_list = KlineHistory.objects.filter(trade_name=trade_name, period=period, data_key=key,
                                                  created_at=created_at)
    if cache_data_list and len(cache_data_list) > 0:
        kh = cache_data_list[0]
        kh.data_value = value
        kh.created_at = created_at
        kh.save()
    else:
        kh = KlineHistory(trade_name=trade_name, period=period, data_key=key, data_value=value, created_at=created_at)
        kh.save()
    # logger.info('cache_data_save ' + period + ' ' + trade_name + ' ' + key + ' ' + value)
