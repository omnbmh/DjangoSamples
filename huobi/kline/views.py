# -*- coding: utf-8 -*-

import sys
import logging
import json

reload(sys)
sys.setdefaultencoding('utf-8')
logger = logging.getLogger("django")

from django.shortcuts import render
from django.template import loader

from django.http import HttpResponse
from orders.models import Symbol
from models import save_kline_history, KlineHistory

import datetime
import orders.common_calc


# Create your views here.

def kline_history(request, period):
    logger.info(u"开始缓存 " + period + u' kline 数据')
    if period == '1day':
        save_kline_history(period, 30)
    return_rlt = {u'status': 'ok'}
    return HttpResponse(json.dumps(return_rlt), content_type="application/json")


def kline_ref(request):
    context = {}
    template = loader.get_template('ref.html')
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
    # 获取交易币种
    data = {"labels": [], "datasets": []}
    # 添加labels
    for i in range(30):
        created_at = orders.common_calc.add_days(datetime.datetime.now(), i + 1 - 30)
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
                kh = KlineHistory.objects.get(trade_name=symbol.trade_name, period='1day', data_key='return_rate',
                                              created_at=cedat)
                ds['data'].append(float(kh.data_value))
            except Exception as e:
                logger.error(e)
                ds['data'].append(0)
        data['datasets'].append(ds)

    return HttpResponse(json.dumps(data), content_type="application/json")
