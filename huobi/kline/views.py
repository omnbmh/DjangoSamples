# -*- coding: utf-8 -*-
from django.template import loader

from django.http import HttpResponse
from orders.models import Symbol
from models import KlineHistory, save_db_kline_history

from huobi import global_settings
from commonlib import common_calc
from commonlib import huobiapi
import datetime
import logging
import json
import models

logger = logging.getLogger("django")


# Create your views here.

def kline_ref(request):
    context = {}
    template = loader.get_template('ref.html')
    return HttpResponse(template.render(context, request))


def kline_hb10(request):
    context = {}
    template = loader.get_template('hb10.html')
    return HttpResponse(template.render(context, request))


def kline_data(request):
    '''
    data = {
        labels: ["January", "February", "March", "April", "May", "June", "July"],
        datasets: [
            {
                label: "My First dataset",
                fillColor: "rgba(220,220,220,0.5)",
                strokeColor: "rgba(220,220,220,0.8)",
                highlightFill: "rgba(220,220,220,0.75)",
                highlightStroke: "rgba(220,220,220,1)",
                data: [65, 59, 80, 81, 56, 55, 40]
            },
            {
                label: "My Second dataset",
                fillColor: "rgba(151,187,205,0.5)",
                strokeColor: "rgba(151,187,205,0.8)",
                highlightFill: "rgba(151,187,205,0.75)",
                highlightStroke: "rgba(151,187,205,1)",
                data: [28, 48, 40, 19, 86, 27, 90]
            }
        ]
    };
    '''

    period = request.GET['p']
    print(period)
    # 获取交易币种
    data = {"labels": [], "datasets": []}
    # 添加labels
    if period == '1day':
        for i in range(30):
            created_at = common_calc.add_days(datetime.datetime.now(), i + 1 - 30)
            data['labels'].append(created_at)

    if period == '60min':
        for i in range(24):
            created_at = common_calc.add_hours(datetime.datetime.now(), i + 1 - 24)
            data['labels'].append(created_at)

    # symbol_list = Symbol.objects.filter(quote_currency='usdt', symbol_partition='main')
    symbol_list = Symbol.objects.filter(quote_currency='usdt')
    for symbol in symbol_list:
        ds = {}
        ds['data'] = []
        ds['label'] = symbol.trade_name
        # ds['backgroundColor'] = 'rgba(0,0,0,0.0)'
        # ds['fill'] = 'false'
        ds['borderWidth'] = '1'
        for cedat in data['labels']:
            try:
                kh = KlineHistory.objects.get(trade_name=symbol.trade_name, period=period, data_key='return_rate',
                                              created_at=cedat)
                ds['data'].append(float(kh.data_value))
            except Exception as e:
                logger.error(e)
                ds['data'].append(0)
        data['datasets'].append(ds)

    # 添加一个均价
    # ds = {}
    # ds['data'] = []
    # ds['label'] = 'avg'
    # ds['borderColor'] = 'rgba(255,0,0,1)'
    # ds['fill'] = 'false'
    # ds['borderWidth'] = '2'
    # for cedat in data['datasets']:
    #     try:
    #         ds['data'].append(round(orders.common_calc.var(cedat['data']), 4))
    #     except Exception as e:
    #         logger.error(e)
    #         ds['data'].append(0)
    # data['datasets'].append(ds)

    return HttpResponse(json.dumps(data), content_type="application/json")


def kline_amount_data(request):
    '''
    data = {
        labels: ["January", "February", "March", "April", "May", "June", "July"],
        datasets: [
            {
                label: "My First dataset",
                fillColor: "rgba(220,220,220,0.5)",
                strokeColor: "rgba(220,220,220,0.8)",
                highlightFill: "rgba(220,220,220,0.75)",
                highlightStroke: "rgba(220,220,220,1)",
                data: [65, 59, 80, 81, 56, 55, 40]
            },
            {
                label: "My Second dataset",
                fillColor: "rgba(151,187,205,0.5)",
                strokeColor: "rgba(151,187,205,0.8)",
                highlightFill: "rgba(151,187,205,0.75)",
                highlightStroke: "rgba(151,187,205,1)",
                data: [28, 48, 40, 19, 86, 27, 90]
            }
        ]
    };
    '''

    period = request.GET['p']
    print(period)
    # 获取交易币种
    data = {"labels": [], "datasets": []}
    # 添加labels
    if period == '1day':
        for i in range(30):
            created_at = common_calc.add_days(datetime.datetime.now(), i + 1 - 30)
            data['labels'].append(created_at)

    if period == '60min':
        for i in range(24):
            created_at = common_calc.add_hours(datetime.datetime.now(), i + 1 - 24)
            data['labels'].append(created_at)

    # symbol_list = Symbol.objects.filter(quote_currency='usdt', symbol_partition='main')
    symbol_list = Symbol.objects.filter(quote_currency='usdt')
    for symbol in symbol_list:
        ds = {}
        ds['data'] = []
        ds['label'] = symbol.trade_name
        # ds['backgroundColor'] = 'rgba(0,0,0,0.0)'
        ds['stack'] = 's0'
        ds['borderWidth'] = '1'
        for cedat in data['labels']:
            try:
                kh = KlineHistory.objects.get(trade_name=symbol.trade_name, period=period, data_key='amount',
                                              created_at=cedat)
                ds['data'].append(float(kh.data_value))
            except Exception as e:
                logger.error(e)
                ds['data'].append(0)
        data['datasets'].append(ds)

    return HttpResponse(json.dumps(data), content_type="application/json")


def kline_hb10_data(request):
    period = '1day'
    # 获取交易币种
    data = {"labels": [], "datasets": []}
    # 添加labels
    if period == '1day':
        for i in range(14):
            created_at = common_calc.add_days_fmt(datetime.datetime.now(), i + 1 - 14, "%Y%m%d")
            data['labels'].append(created_at)

    if period == '60min':
        for i in range(24):
            created_at = common_calc.add_hours(datetime.datetime.now(), i + 1 - 24)
            data['labels'].append(created_at)

    # symbol_list = Symbol.objects.filter(quote_currency='usdt', symbol_partition='main')
    symbol_list = Symbol.objects.filter(quote_currency='usdt')
    for symbol in symbol_list:
        if symbol.trade_name in global_settings.HB_10:
            ds = {}
            ds['data'] = []
            ds['label'] = symbol.trade_name
            # ds['backgroundColor'] = 'rgba(0,0,0,0.0)'
            # ds['fill'] = 'false'
            ds['borderWidth'] = '1'
            for cedat in data['labels']:
                try:
                    khobject = models.KLINE_HISTORY_SHARFING_MAP[symbol.trade_name]
                    kh = khobject.objects.get(symbol=symbol.trade_name, period=period,
                                              created_at=cedat + "000000")
                    ds['data'].append(float(kh.col_updown_rate))
                except Exception as e:
                    logger.error(e)
                    ds['data'].append(0)
            data['datasets'].append(ds)

    return HttpResponse(json.dumps(data), content_type="application/json")


#
# API 接口
#


def kline_history_init(request):
    """
    初始化所有币种的历史kline信息
    :param request:
    :param period:
    :return:
    """
    # 获取需要初始化的币种信息
    # 查询出 所有支持交易的USDT区币种
    symbol_list = Symbol.objects.filter(quote_currency='usdt')
    # symbol_list = Symbol.objects.filter(quote_currency='usdt', base_currency='btc')
    if symbol_list:
        for symbol in symbol_list:
            # logger.info(type(symbol))
            if symbol.trade_name not in global_settings.HB_10:
                logger.info(u'not hb10 coin don\'t cache. ' + symbol.trade_name)
                continue
            for period in global_settings.KLINE_PERIOD_ARRAY:
                logger.info(u'start cache kline data symbol. ' + symbol.trade_name + u' per. ' + period)
                __kline_history_init_symbol(symbol.trade_name, period, global_settings.KLINE_MAX_SIZE)
                logger.info(u'end cache kline data symbol. ' + symbol.trade_name + u' per. ' + period)

    return_rlt = {u'status': 'ok'}
    return HttpResponse(json.dumps(return_rlt), content_type="application/json")


def kline_history_all_symbol():
    # 获取需要初始化的币种信息
    # 查询出 所有支持交易的USDT区币种
    symbol_list = Symbol.objects.filter(quote_currency='usdt')
    # symbol_list = Symbol.objects.filter(quote_currency='usdt', base_currency='btc')
    if symbol_list:
        for symbol in symbol_list:
            # logger.info(type(symbol))
            if symbol.trade_name not in global_settings.HB_10:
                logger.info(u'not hb10 coin don\'t cache. ' + symbol.trade_name)
                continue
            if symbol.trade_name not in models.KLINE_HISTORY_SHARFING_MAP:
                logger.info(u'not support coin don\'t cache. ' + symbol.trade_name)
                continue
            for period in global_settings.KLINE_PERIOD_ARRAY:
                size = 1
                if period == '1min' or period == '5min' or period == '15min':
                    size = 30
                logger.info(
                    u'start cache kline data symbol. ' + symbol.trade_name + u' per. ' + period + u' size. ' + str(
                        size))
                __kline_history_init_symbol(symbol.trade_name, period, size)
                logger.info(u'end cache kline data symbol. ' + symbol.trade_name + u' per. ' + period)


def __kline_history_init_symbol(symbol, period, size):
    """
    初始化历史币种kline信息
    """
    rlt_json = huobiapi.get_kline(symbol, period, size)
    # logger.info(rlt_json)
    if rlt_json[u'status'] == 'ok':
        for i in range(len(rlt_json[u'data'])):
            offset = i
            row_data = rlt_json[u'data'][offset]
            save_db_kline_history(symbol, period, row_data)
        logger.info(u'缓存数据 %s %s 成功' % (symbol, period))
    else:
        logger.info(u'缓存数据 %s %d 失败 接口调用失败' % (period, size))
