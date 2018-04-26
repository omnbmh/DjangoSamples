# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader

from orders.models import OrderRelation
import time

import logging

logger = logging.getLogger("django")


# Create your views here.


def index(request):
    context = {}
    context['list'] = []
    context['total_income'] = 0
    # 24小时之内的数据
    order_rela_list = OrderRelation.objects.filter(
        buy_order__created_at__gt=((int(time.time()) - 24 * 3600) * 1000)).order_by('-id')

    for r in order_rela_list:
        item = {"id": r.id, "symbol": r.buy_order.symbol,
                'created_at': fmt_timstamp(int(r.buy_order.created_at) / 1000),
                'finished_at': '-',
                'buy_price': float(r.buy_order.price), 'sell_price': '-', 'state': r.state, 'income_rate': '-',
                'income': '-'}

        if r.sell_order_id:
            if int(r.sell_order.finished_at) > 0:
                item['finished_at'] = fmt_timstamp(int(r.sell_order.finished_at) / 1000)
            item['sell_price'] = float(r.sell_order.price)
            item['income_rate'] = round(float(r.sell_order.price) / float(r.buy_order.price) - 1, 5)
        if r.state == 'S':
            # 收入 = 卖出成交金额 - 卖出手续费 - 买入成交金额
            income = float(r.sell_order.field_cash_amount) - float(
                r.sell_order.field_fees) - float(r.buy_order.field_cash_amount)
            item['income'] = income
            context['total_income'] = context['total_income'] + income
        context['list'].append(item)
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


def fmt_timstamp(ss):
    if isinstance(ss, (int, float)):
        return time.strftime(u'%Y-%m-%d %H:%M:%S', time.localtime(ss))
    return ss
