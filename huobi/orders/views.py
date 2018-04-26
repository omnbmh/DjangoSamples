# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import json
import time
import threading
import logging
import math

logger = logging.getLogger("django")
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q
from models import Order, OrderRelation, Symbol, CacheData, OrderRelationHistory

import HuobiService
import common_calc
import match
import huobi.global_settings
import kline.models

FIRST_INIT_CACHE_DATA = False


# api
# 开始工作
def start_work(request):
    match.refresh_setting()
    # 初始化 未完成 订单
    init_orders()

    # 缓存数据
    ana_kline_thread = threading.Thread(target=ana_kline, name='ana_kline')
    ana_kline_thread.start()

    # 缓存数据
    kline_history_thread = threading.Thread(target=kline_history, name='kline_history')
    kline_history_thread.start()

    # 扫单
    loop_order_thread = threading.Thread(target=loop_order, name='loop_order')
    loop_order_thread.start()

    # 策略下单
    orders_buy_thread = threading.Thread(target=orders_buy, name='orders_buy')
    orders_buy_thread.start()

    return_rlt = {u'status': 'ok'}
    return HttpResponse(json.dumps(return_rlt), content_type="application/json")


def refresh_settings(request):
    match.refresh_setting()
    return_rlt = {u'status': 'ok'}
    return HttpResponse(json.dumps(return_rlt), content_type="application/json")


def init_db_symbol(request):
    # 初始化 可交易币种 和 精度
    rlt_json = HuobiService.get_symbols()
    if rlt_json[u'status'] == 'ok':
        for sml in rlt_json[u'data']:
            save_symbol(sml)
    else:
        logger.error(rlt_json)
        logger.info(u'获取 可交易币种 失败')

    return_rlt = {u'status': 'ok'}
    return HttpResponse(json.dumps(return_rlt), content_type="application/json")


def init_db_order(request):
    # 'buy-limit,buy-market,sell-limit,sell-market',
    # 初始化 历史订单
    rlt_json = HuobiService.get_balance()
    if rlt_json[u'status'] == 'ok':
        balanceList = rlt_json[u'data'][u'list']
        for ban in balanceList:
            if ban[u'balance'].startswith('0.00000000'):
                continue
            if ban[u'currency'] == 'usdt':
                # 法币不交易
                continue
            if ban[u'type'] == 'frozen':
                continue
            logger.info(u'币种 %s 类型 %s 现量 %s' % (ban[u'currency'], ban[u'type'], ban[u'balance']))
            coin_name = ban[u'currency'] + 'usdt'
            rlt_json = HuobiService.orders_list(coin_name,
                                                'pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled',
                                                start_date='2018-04-23')
            if rlt_json[u'status'] == 'ok':
                for order_ in rlt_json[u'data']:
                    save_order(order_)
                    time.sleep(1)
            else:
                logger.info(rlt_json)
                logger.info(u"加载订单失败 " + rlt_json[u'status'] + ' ' + coin_name)
    else:
        logger.info(rlt_json)
        logger.info("获取账户信息失败 " + rlt_json[u'status'])
    return_rlt = {u'status': 'ok'}
    return HttpResponse(json.dumps(return_rlt), content_type="application/json")


def save_symbol(sml):
    base_currency = sml['base-currency']
    quote_currency = sml['quote-currency']
    s_list = Symbol.objects.filter(base_currency=base_currency, quote_currency=quote_currency)
    if quote_currency == 'usdt':
        if s_list and len(s_list) > 0:
            symbol = s_list[0]
            # symbol.base_currency = sml["base-currency"],
            # symbol.quote_currency = sml["quote-currency"],
            symbol.canceled_at = sml["price-precision"]
            symbol.amount_precision = sml["amount-precision"]
            symbol.symbol_partition = sml["symbol-partition"]
            symbol.save()

        else:
            symbol = Symbol(base_currency=sml["base-currency"],
                            quote_currency=sml["quote-currency"],
                            price_precision=sml["price-precision"],
                            amount_precision=sml["amount-precision"],
                            symbol_partition=sml["symbol-partition"],
                            trade_name=sml["base-currency"] + sml["quote-currency"],
                            state='0')
            symbol.save()
        logger.info(u'初始化 交易币种 %s %s' % (base_currency, quote_currency))
    else:
        if s_list and len(s_list) > 0:
            # 更新
            symbol = s_list[0]
            symbol.delete()
            logger.info(u'初始化 删除 交易币种 %s %s' % (base_currency, quote_currency))


def save_order(rowData):
    id = rowData['id']

    order_list = Order.objects.filter(id=id)
    if order_list and len(order_list) > 0:
        order = order_list[0]
        if order.state != 'filled':
            order.refresh()
            logger.info(u'初始化数据库 更新订单 ' + order.id)
    else:
        logger.info(u'新增订单 ' + str(id))
        order = Order(account_id=rowData["account-id"],
                      amount=rowData["amount"],
                      canceled_at=rowData["canceled-at"],
                      created_at=rowData["created-at"],
                      field_amount=rowData["field-amount"],
                      field_cash_amount=rowData["field-cash-amount"],
                      field_fees=rowData["field-fees"],
                      finished_at=rowData["finished-at"],
                      id=rowData["id"],
                      price=rowData["price"],
                      source=rowData["source"],
                      state=rowData["state"],
                      symbol=rowData["symbol"],
                      type=rowData["type"])
        order.save()
        logger.info(u'初始化数据库 新增订单 ' + str(order.id))


def ana_kline():
    # 计时器
    last_time_60 = 0
    last_time_300 = 0
    last_time_900 = 0
    last_time_1800 = 0
    last_time_3600 = 0
    last_time_86400 = 0
    while True:
        if int(time.time()) - last_time_60 > 60:  # 1分钟
            save_cache_data('1min', 15)
            last_time_60 = int(time.time())
        if int(time.time()) - last_time_300 > 300:  # 5分钟
            save_cache_data('5min', 6)
            last_time_300 = int(time.time())
        if int(time.time()) - last_time_900 > 900:  # 15分钟
            save_cache_data('15min', 8)
            last_time_900 = int(time.time())
        if int(time.time()) - last_time_1800 > 1800:  # 30分钟
            save_cache_data('30min', 8)
            last_time_1800 = int(time.time())
        if int(time.time()) - last_time_3600 > 3600:  # 60分钟
            save_cache_data('60min', 8)
            last_time_3600 = int(time.time())
        if int(time.time()) - last_time_86400 > 86400:  # 1天
            save_cache_data('1day', 5)
            last_time_86400 = int(time.time())
        global FIRST_INIT_CACHE_DATA
        FIRST_INIT_CACHE_DATA = True
        time.sleep(10)


def kline_history():
    # 计时器
    last_time_60 = 0
    last_time_300 = 0
    last_time_900 = 0
    last_time_1800 = 0
    last_time_3600 = 0
    last_time_86400 = 0
    while True:
        if int(time.time()) - last_time_60 > 60:  # 1分钟
            # save_cache_data('1min', 15)
            last_time_60 = int(time.time())
        if int(time.time()) - last_time_300 > 300:  # 5分钟
            # save_cache_data('5min', 6)
            last_time_300 = int(time.time())
        if int(time.time()) - last_time_900 > 900:  # 15分钟
            # save_cache_data('15min', 8)
            last_time_900 = int(time.time())
        if int(time.time()) - last_time_1800 > 1800:  # 30分钟
            kline.models.save_kline_history('1day', 2)
            last_time_1800 = int(time.time())
        if int(time.time()) - last_time_3600 > 3600:  # 60分钟
            # save_cache_data('60min', 8)
            last_time_3600 = int(time.time())
        if int(time.time()) - last_time_86400 > 86400:  # 1天
            # save_cache_data('1day', 5)
            last_time_86400 = int(time.time())
        time.sleep(10)


def save_cache_data(period, size):
    symbol_list = Symbol.objects.filter(quote_currency='usdt')
    for symbol in symbol_list:
        rlt_json = HuobiService.get_kline(symbol.trade_name, period, size)
        if rlt_json[u'status'] == 'ok':
            if '1min' == period:
                offset = 0
                save_db_cache_data(symbol.trade_name, period, 'realtime',
                                   ('%.13f' % rlt_json[u'data'][offset][u'close']))

            avg_c = common_calc.avg_close(deal_data(rlt_json[u'data'], 'close'))
            std_c = common_calc.std_close(deal_data(rlt_json[u'data'], 'close'))
            avg_high_low_c = common_calc.avg_high_low(deal_data(rlt_json[u'data'], 'close'))
            trend_c = common_calc.trend(rlt_json[u'data'])
            trend_std_c = common_calc.trend_std(rlt_json[u'data'])
            save_db_cache_data(symbol.trade_name, period, 'avg', ('%.13f' % avg_c))
            save_db_cache_data(symbol.trade_name, period, 'std', ('%.13f' % std_c))
            save_db_cache_data(symbol.trade_name, period, 'avg_high_low', ('%.13f' % avg_high_low_c))
            save_db_cache_data(symbol.trade_name, period, 'trend', ','.join(trend_c))
            save_db_cache_data(symbol.trade_name, period, 'trend_std', ('%.13f' % trend_std_c))
            logger.info(u'缓存数据 %s %s %d 完成' % (symbol.trade_name, period, size))
    logger.info(u'缓存数据 %s %d 完成' % (period, size))
    time.sleep(5)


def save_db_cache_data(trade_name, period, key, value):
    cache_data_list = CacheData.objects.filter(trade_name=trade_name, period=period, data_key=key)
    if cache_data_list and len(cache_data_list) > 0:
        cd = cache_data_list[0]
        cd.data_value = value
        cd.save()
    else:
        cd = CacheData(trade_name=trade_name, period=period, data_key=key, data_value=value)
        cd.save()
    # logger.info('cache_data_save ' + period + ' ' + trade_name + ' ' + key + ' ' + value)


def deal_data(data, prop_name):
    num_arr = []
    for dd in data:
        num_arr.append(float(dd[prop_name]))
    return num_arr


def init_orders():
    # 获取下账户信息
    rlt_json = HuobiService.get_balance()
    if rlt_json[u'status'] == 'ok':
        logger.info('----- Account Balance Detail-----')
        for ban in rlt_json[u'data'][u'list']:
            if ban[u'balance'].startswith('0.00000000'):
                continue
            logger.info(u'币种 %s 类型 %s 现量 %s' % (ban[u'currency'], ban[u'type'], ban[u'balance']))
        logger.info('----- Account Balance End-----')
    else:
        logger.info("获取账户信息失败 " + rlt_json[u'status'])
    logger.info(u"初始化账户完成 ")
    # 获取历史订单
    order_rela_list = OrderRelation.objects.filter(Q(state='A') | Q(state='P'))
    if order_rela_list and len(order_rela_list):
        for row in order_rela_list:
            if row.sell_order_id:
                order = Order.objects.get(id=row.sell_order_id)
                order.refresh()
                if order.state == 'filled':
                    logger.info(u"卖单已完成")
                    row.state = 'S'
                    row.save()

    logger.info(u"初始化订单完成 ")


def loop_order():
    '''
    扫描订单状态
    1. 买单 未交易 超过10分钟 撤销订单
    2. 买单 部分交易 超过20分钟 撤销订单

    '''
    last_time = 0
    while True:
        if int(time.time()) - last_time > 60 and FIRST_INIT_CACHE_DATA:
            logger.info(u'开始扫单')
            # 获取进行中的交易
            order_rela_list = OrderRelation.objects.filter(Q(state='A') | Q(state='P'))
            if order_rela_list and len(order_rela_list):
                for row in order_rela_list:
                    order = Order.objects.get(id=row.buy_order_id)
                    order.refresh()
                    logger.info(u'开始扫单 买单' + row.buy_order_id)
                    symbol = Symbol.objects.get(trade_name=order.symbol)
                    # 处理买单 支持限价买 市价买
                    if order.type == 'buy-limit' or order.type == 'buy-market':
                        if order.state == 'filled':
                            '''
                            买单已成交
                            '''
                            logger.info(u" 买单成功 订单号 " + order.id)
                            sell_order = None
                            # 判断是否需要 卖单
                            if row.sell_order_id:
                                # 有卖单 处理卖单 处理已知的状态
                                sell_order = row.sell_order
                                sell_order.refresh()
                                if sell_order.state == 'filled':
                                    # 卖单成功 更新 交易关系状态 S
                                    logger.info(u" 卖单成功 交易完成 订单号 " + sell_order.id)
                                    row.state = 'S'
                                    row.save()
                                    # 交易完成
                                    continue
                                elif sell_order.state == 'canceled':
                                    logger.info(u" 卖单已撤单 订单号 " + sell_order.id)
                                    # 添加撤销历史
                                    rela_history = OrderRelationHistory(buy_order=order, sell_order=sell_order,
                                                                        created_at=str(int(time.time())))
                                    rela_history.save()
                                    # 卖单撤销 更新 交易关系状态 A 等待重新下卖单
                                    row.sell_order = None
                                    row.state = 'A'
                                    row.save()
                                    continue
                                elif sell_order.state == 'partial-filled':
                                    pass
                                    # 卖单还没有被取消掉
                                    # sell_order = row.sell_order
                                    # can_sell, sell_price, sell_cnt = match.resell_match(order, sell_order, order.symbol)
                                    # if can_sell:
                                    #     if sell_order.state == 'submitted':
                                    #         # 已经有卖单了 还让卖 考虑是否需要撤单 重新下单 买单是提交状态 才能撤单 防止部分成交
                                    #         rlt = HuobiService.cancel_order(sell_order.id)
                                    #         if rlt[u'status'] == 'ok':
                                    #             # 卖出量 小于 持有量 或者 卖出量
                                    #             balance = symbol_balance(order.symbol)
                                    #             if sell_cnt > balance or ((sell_cnt * (1 + 0.05)) > balance):
                                    #                 sell_cnt = round(balance, int(symbol.amount_precision))
                                    #                 if sell_cnt >= balance:
                                    #                     # 防止四舍五入 导致账户余额 不足无法卖单
                                    #                     sell_cnt = sell_cnt - math.pow(0.1, int(symbol.amount_precision))
                                    #                     logger.info(u"调整后 卖出量 %s 账户余额 %s " % (str(sell_cnt), str(balance)))
                                    #                 logger.info(u"重新调整卖出量 " + str(sell_cnt))
                                    #
                                    #             logger.info(u'下单 卖出价 %s 卖出量 %s' % (sell_price, sell_cnt))
                                    #             logger.info(u'策略重新挂卖单 取消成功 订单号 ' + sell_order.id)
                                    #             rlt = HuobiService.send_order(str(sell_cnt), 'api', order.symbol, 'sell-limit',
                                    #                                           str(sell_price))
                                    #             if rlt[u'status'] == 'ok':
                                    #                 sell_order = Order(id=rlt[u'data'])
                                    #                 #  保存卖订单
                                    #                 sell_order.refresh()
                                    #
                                    #                 # 更新关系
                                    #                 row.sell_order = sell_order
                                    #                 row.state = 'P'
                                    #                 row.save()
                                    #                 logger.info(u'策略重新挂卖单 挂单成功 订单号 ' + sell_order.id)
                                    #             else:
                                    #                 logger.error(rlt)
                                    #                 logger.info(u'策略重新挂卖单 挂单失败')
                                    #         else:
                                    #             logger.error(rlt)
                                    #             logger.error(u'策略重新挂卖单 取消失败 订单号  ' + sell_order.id)
                                    #     else:
                                    #         logger.info(u'不能重新下卖单 状态不符合 订单号' + sell_order.id + u' 状态 ' + sell_order.state)
                                    # else:
                                    #     logger.info(u'卖单正在进行中 订单号' + sell_order.id + u' 状态 ' + sell_order.state)
                                else:
                                    pass
                            else:
                                # 无卖单 挂卖单
                                can_sell, sell_price, sell_cnt = match.sell_match(order, order.symbol)
                                if not can_sell:
                                    logger.info(u" 卖单策略 不需要卖出 好消息 可能在猛涨 买单订单号 " + order.id)
                                    continue

                                # 卖出量 小于 持有量 或者 卖出量
                                balance = symbol_balance(order.symbol)
                                if sell_cnt > balance or ((sell_cnt * (1 + 0.5)) > balance):
                                    sell_cnt = round(balance, int(symbol.amount_precision))
                                    if sell_cnt >= balance:
                                        # 防止四舍五入 导致账户余额 不足无法卖单
                                        sell_cnt = sell_cnt - math.pow(0.1, int(symbol.amount_precision)) * 2
                                        logger.info(u"调整后 卖出量 %s 账户余额 %s " % (str(sell_cnt), str(balance)))
                                    logger.info(u"重新调整卖出量 " + str(sell_cnt))

                                logger.info(u'下单 卖出价 %s 卖出量 %s' % (sell_price, sell_cnt))
                                rlt = HuobiService.send_order(str(sell_cnt), 'api', order.symbol, 'sell-limit',
                                                              str(sell_price))
                                # rlt = HuobiService.send_order(str(sell_cnt), 'api', order.symbol, 'sell-market')
                                if rlt[u'status'] == 'ok':
                                    sell_order = Order(id=rlt[u'data'])
                                    #  保存卖订单
                                    sell_order.refresh()
                                    # 更新关系
                                    row.sell_order_id = sell_order.id
                                    row.state = 'P'
                                    row.save()
                                    logger.info(u" 卖单已提交成功 订单号 " + sell_order.id)
                                else:
                                    logger.error(rlt)
                                    logger.info(u" 卖单挂单失败 买单 订单号 " + order.id)
                        elif order.state == 'partial-filled' and order.type == 'buy-limit':
                            '''
                            买单部分成交
                            '''
                            timediff = int(time.time()) - int(order.created_at) / 1000
                            logger.info(
                                u" 买单正在进行中 部分成交 订单号 " + order.id + u' 已进行时长 ' + str(timediff) + u' 秒')
                            if timediff > 2 * huobi.global_settings.BUY_ORDER_MAX_WAIT_TIME:
                                rlt = HuobiService.cancel_order(order.id)
                                if rlt[u'status'] == 'ok':
                                    logger.info(u'买单 超时 撤消成功 ' + order.id)
                                    order.refresh()
                                    row.state = 'C'
                                    row.save()
                                else:
                                    logger.error(rlt)
                                    logger.info(u'买单 超时 撤消失败 ' + order.id)
                        else:
                            '''
                            买单未成交
                            '''
                            timediff = int(time.time()) - int(order.created_at) / 1000
                            logger.info(
                                u" 买单正在进行中 订单号 " + order.id + u' 已进行时长 ' + str(timediff) + u' 状态 ' + order.state)
                            # 买单超过10分钟 撤销订单
                            if timediff > 600:
                                if order.state == 'submitted':
                                    rlt = HuobiService.cancel_order(order.id)
                                    if rlt[u'status'] == 'ok':
                                        logger.info(u'买单 超时 撤消成功 ' + order.id)
                                        order.refresh()
                                        row.state = 'C'
                                        row.save()
                                    else:
                                        logger.error(rlt)
                                        logger.info(u'买单 超时 撤消失败 ' + order.id)
            last_time = int(time.time())
        time.sleep(10)


def orders_buy():
    '''
    1. 5分钟下一次买单
    '''
    last_time = 0
    while True:
        if int(time.time()) - last_time > 300 and FIRST_INIT_CACHE_DATA:
            # 获取可交易币种
            symbol_list = Symbol.objects.filter(state='1')
            for symbol in symbol_list:
                # 获取进行中 订单
                order_rela_list = OrderRelation.objects.filter(Q(state='A') | Q(state='P'))
                q_count = len(order_rela_list) if order_rela_list else 0
                can_buy, buy_price, buy_count = match.buy_match(symbol.trade_name, q_count)
                if can_buy:
                    # 买入
                    logger.info(u"策略通过 买入 %s 价格 %f 数量 %d" % (symbol.trade_name, buy_price, buy_count))
                    rlt_json = HuobiService.send_order(str(buy_count), 'api', symbol.trade_name, 'buy-limit',
                                                       str(buy_price))
                    if rlt_json[u'status'] == 'ok':
                        order_id = rlt_json[u'data']
                        logger.info(u" 买入 %s 挂单成功 - 订单号 %s" % (symbol.trade_name, order_id))
                        # 挂单成功 存入数据库一份
                        order = Order(id=order_id)
                        order.refresh()
                        # 关系表存一份
                        order_rela = OrderRelation(buy_order=order)
                        order_rela.state = 'A'
                        order_rela.save()
                    else:
                        logger.error(rlt_json)
                        logger.info(u" 买入 %s 挂单失败 %s " % (symbol.trade_name, rlt_json[u'status']))
                else:
                    logger.info(u"策略未通过 不能买入 %s " % symbol.trade_name)
            last_time = int(time.time())
        # 延时
        time.sleep(10)


def order_sell():
    '''
    1. 不再针对单个订单 买卖 以账户余额为准 进行买卖 方便统一处理卖单

    '''
    last_time = 0
    while True:
        if int(time.time()) - last_time > 60 and FIRST_INIT_CACHE_DATA:
            # 获取下账户币信息
            rlt_json = HuobiService.get_balance()
            if rlt_json[u'status'] == 'ok':
                for ban in rlt_json[u'data'][u'list']:
                    if ban[u'balance'].startswith('0.00000000'):
                        continue
                    if ban[u'currency'] == 'usdt':
                        continue
                    if ban[u'type'] == 'trade':
                        balance = float(ban[u'balance'])
                        logger.info(u'币种 %s 现持有量(不含冻结) %s' % (ban[u'currency'] + 'usdt', ban[u'balance']))
                        logger.info()
            else:
                logger.info("获取账户信息失败 " + rlt_json[u'status'])
        # 延时
        time.sleep(10)


def fmt_timstamp(ss):
    return time.strftime(u'%d days %H hours %M minus %S secends', time.localtime(ss))


def symbol_balance(trade_name):
    balance = 0.0
    # 获取下账户信息
    rlt_json = HuobiService.get_balance()
    if rlt_json[u'status'] == 'ok':
        for ban in rlt_json[u'data'][u'list']:
            if ban[u'balance'].startswith('0.00000000'):
                continue
            if ban[u'currency'] + 'usdt' == trade_name and ban[u'type'] == 'trade':
                balance = float(ban[u'balance'])
                break
    else:
        logger.info("获取账户信息失败 " + rlt_json[u'status'])

    logger.info(u'币种 %s 现持有量(不含冻结) %s' % (ban[u'currency'], ban[u'balance']))
    return balance
