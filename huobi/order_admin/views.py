# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader

from orders.models import OrderRelation
import time
from django.db.models import Q
import logging
import huobi
import orders

logger = logging.getLogger("django")


# Create your views here.


def index(request):
    context = {}
    context['list'] = []
    context['total_income'] = 0
    # 24小时之内的数据
    # order_rela_list = OrderRelation.objects.filter(
    #    buy_order__created_at__gt=((int(time.time()) - 24 * 3600) * 1000)).order_by('-id')

    # 进行中的订单
    order_rela_list = OrderRelation.objects.filter(Q(state='A') | Q(state='P')).order_by('-id')

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

    q_count = len(order_rela_list) if order_rela_list else 0
    context['queue'] = str(q_count) + '/' + str(huobi.global_settings.ORDER_MAX)
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


def fmt_timstamp(ss):
    if isinstance(ss, (int, float)):
        return time.strftime(u'%Y-%m-%d %H:%M:%S', time.localtime(ss))
    return ss


# @login_required
def manage_account(request):
    """
    账户币种管理
    :param request:
    :return:
    """
    context = {}
    context["list"] = []

    # 获取当前账户详情
    rlt_json = orders.HuobiService.get_balance()
    if rlt_json[u'status'] == 'ok':
        balanceList = rlt_json[u'data'][u'list']
        for ban in balanceList:
            if ban[u'balance'].startswith('0.00000000'):
                continue
            if ban[u'type'] == 'frozen':
                continue

            logger.info(u'币种 %s 类型 %s 现量 %s' % (ban[u'currency'], ban[u'type'], ban[u'balance']))
            coin_name = ban[u'currency'] + 'usdt'

    else:
        logger.error(u"获取账户详情失败")

    template = loader.get_template('account.html')
    return HttpResponse(template.render(context, request))


@login_required
def manage_monitor(request):
    context = {}
    context["list"] = []
    template = loader.get_template('monitor.html')
    return HttpResponse(template.render(context, request))
