# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import time
from models import CacheData, Order, Symbol, Setting
import huobi.global_settings
import logging
import numpy as np

logger = logging.getLogger("django")


def refresh_setting():
    setting_list = Setting.objects.filter()
    if setting_list and len(setting_list) > 0:
        for setting in setting_list:
            if setting.setting_key == 'INCOME_MINI':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.INCOME_MINI))
                huobi.global_settings.INCOME_MINI = float(setting.setting_value)
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.INCOME_MINI))
            if setting.setting_key == 'INCOME_INCR_MAX':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.INCOME_INCR_MAX))
                huobi.global_settings.INCOME_INCR_MAX = float(setting.setting_value)
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.INCOME_INCR_MAX))
            if setting.setting_key == 'INCOME_DECR_MAX':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.INCOME_DECR_MAX))
                huobi.global_settings.INCOME_DECR_MAX = float(setting.setting_value)
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.INCOME_DECR_MAX))
            if setting.setting_key == 'ORDER_MAX':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.ORDER_MAX))
                huobi.global_settings.ORDER_MAX = int(setting.setting_value)
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.ORDER_MAX))
            if setting.setting_key == 'SELL_ORDER_MAX_WAIT_TIME':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.SELL_ORDER_MAX_WAIT_TIME))
                huobi.global_settings.SELL_ORDER_MAX_WAIT_TIME = int(setting.setting_value)
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.SELL_ORDER_MAX_WAIT_TIME))
            if setting.setting_key == 'BUY_ORDER_MAX_WAIT_TIME':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.BUY_ORDER_MAX_WAIT_TIME))
                huobi.global_settings.BUY_ORDER_MAX_WAIT_TIME = int(setting.setting_value)
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.BUY_ORDER_MAX_WAIT_TIME))
            if setting.setting_key == 'USDT_COUNT':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.USDT_COUNT))
                huobi.global_settings.USDT_COUNT = int(setting.setting_value)
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.USDT_COUNT))
            if setting.setting_key == 'ACCESS_KEY':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.ACCESS_KEY))
                huobi.global_settings.ACCESS_KEY = setting.setting_value
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.ACCESS_KEY))
            if setting.setting_key == 'SECRET_KEY':
                logger.info(u"配置刷新前 " + str(huobi.global_settings.SECRET_KEY))
                huobi.global_settings.SECRET_KEY = setting.setting_value
                logger.info(u'刷新全局配置 %s 值 %s' % (setting.setting_key, setting.setting_value))
                logger.info(u"配置刷新后 " + str(huobi.global_settings.SECRET_KEY))


def buy_match(trade_name, q_count):
    '''
    策略描述
    1. 半小时内不购买同币种
    2. 大于 ORDER_MAX 不下单
    3.

    '''

    can_buy = True
    buy_price = None
    buy_count = None
    logger.info(u'当前队列容量 %d/%d' % (q_count, huobi.global_settings.ORDER_MAX))
    if q_count >= huobi.global_settings.ORDER_MAX:
        can_buy = False
        logger.info(u'处理队列已满 %d/%d' % (q_count, huobi.global_settings.ORDER_MAX))

    buy_order_list = Order.objects.filter(symbol=trade_name, type='buy-limit').order_by('-created_at')
    if can_buy and buy_order_list and len(buy_order_list) > 0:
        logger.info(u'查询到上次订单 订单号 ' + buy_order_list[0].id)
        time_diff = int(time.time()) - int(buy_order_list[0].created_at) / 1000
        logger.info(u'币种 %s 距离上次购买 时间差为 %d 上次购买时间是 %s ' % (trade_name, time_diff, buy_order_list[0].created_at))
        if time_diff < 1800:
            logger.info(u'币种 %s 距离上次购买小于半小时 不购买' % (trade_name))
            can_buy = False

    # 获取精度
    symbol = Symbol.objects.get(trade_name=trade_name)
    # 获取缓存数据
    cur_price = None
    min1_avg = None
    min5_avg = None
    min15_avg = None
    min15_trend = None
    min15_avg_high_low = None
    min15_std = None
    min30_avg = None
    min60_avg = None
    day1_avg = None

    cache_data_list = CacheData.objects.filter(trade_name=trade_name)
    if can_buy and cache_data_list and len(cache_data_list) > 0:
        # 准备缓存数据
        for cd in cache_data_list:
            try:
                if cd.period == '1min':
                    if cd.data_key == 'realtime':
                        cur_price = float(cd.data_value)
                    if cd.data_key == 'avg':
                        min1_avg = float(cd.data_value)
                if cd.period == '5min':
                    if cd.data_key == 'avg':
                        min5_avg = float(cd.data_value)
                if cd.period == '15min':
                    if cd.data_key == 'avg':
                        min15_avg = float(cd.data_value)
                    if cd.data_key == 'avg_high_low':
                        min15_avg_high_low = float(cd.data_value)
                    if cd.data_key == 'std':
                        min15_std = float(cd.data_value)
                    if cd.data_key == 'trend':
                        min15_trend = cd.data_value
                if cd.period == '30min':
                    if cd.data_key == 'avg':
                        min30_avg = float(cd.data_value)
                if cd.period == '60min':
                    if cd.data_key == 'avg':
                        min60_avg = float(cd.data_value)
                if cd.period == '1day':
                    if cd.data_key == 'avg':
                        day1_avg = float(cd.data_value)
            except Exception as e:
                logger.error(e)
                logger.error(u"缓存数据未完成 跳过 " + trade_name)
                return False, round(0.0, int(symbol.price_precision)), 0.0
        # 判断是否购买 趋势判断
        # if can_buy and min15_trend:
        #     logger.info(u"%s 15min趋势 参考值 %s" % (trade_name, min15_trend))
        #     tmp_trend = min15_trend.split(',')
        #     for w in range(1):
        #         if float(tmp_trend[w]) < 0.001:
        #             can_buy = True
        #             break
        #         else:
        #             can_buy = False
        if cur_price and can_buy and cur_price > day1_avg:
            logger.info(u"%s 大于1day均价 不购买 基准值 %f 比对值 %f" % (trade_name, cur_price, day1_avg))
            can_buy = False
        if cur_price and can_buy and cur_price > min30_avg:
            logger.info(u"%s 大于30min均价 不购买 基准值 %f 比对值 %f" % (trade_name, cur_price, min30_avg))
            can_buy = False
        if cur_price and can_buy and cur_price > min60_avg:
            logger.info(u"%s 大于60min均价 不购买 基准值 %f 比对值 %f" % (trade_name, cur_price, min60_avg))
            can_buy = False
        if cur_price and can_buy and cur_price > min15_avg:
            logger.info(u"%s 大于15min均价 不购买 基准值 %f 比对值 %f" % (trade_name, cur_price, min15_avg))
            can_buy = False
        if cur_price and can_buy and cur_price > min15_avg_high_low:
            logger.info(u"%s 大于15min(avg_high_low) 不购买 基准值 %f 比对值 %f" % (trade_name, cur_price, min15_avg_high_low))
            can_buy = False
        if cur_price and can_buy and cur_price > min5_avg and False:
            logger.info(u"%s 大于5min均价 不购买 基准值 %f 比对值 %f" % (trade_name, cur_price, min5_avg))
            can_buy = False
        if cur_price and can_buy and cur_price > min1_avg and False:
            logger.info(u"%s 大于1min均价 不购买 基准值 %f 比对值 %f" % (trade_name, cur_price, min1_avg))
            can_buy = False

    if can_buy:
        buy_price = cur_price
        # 购买数量
        buy_count = round(huobi.global_settings.USDT_COUNT / cur_price, int(symbol.amount_precision))

    return can_buy, buy_price, buy_count


def sell_match(buy_order, trade_name):
    '''
    策略描述
    1. 卖单大于2小时 以最低收益 挂单
    2. 卖单大于1小时 最低收益 + 0.001 挂单
    3.

    '''

    can_sell = True
    sell_price = None

    # 获取精度
    symbol = Symbol.objects.get(trade_name=trade_name)

    # 获取缓存数据
    cur_price = None
    min1_avg = None
    min1_trend = None
    min5_avg = None
    min15_avg = None
    min15_avg_high_low = None
    min15_std = None
    min15_trend = None
    min30_avg = None
    min60_avg = None
    day1_avg = None

    cache_data_list = CacheData.objects.filter(trade_name=trade_name)
    if cache_data_list and len(cache_data_list) > 0:
        # 准备缓存数据
        for cd in cache_data_list:
            try:
                if cd.period == '1min':
                    if cd.data_key == 'realtime':
                        cur_price = float(cd.data_value)
                    if cd.data_key == 'avg':
                        min1_avg = float(cd.data_value)
                    if cd.data_key == 'trend':
                        min1_trend = cd.data_value
                if cd.period == '5min':
                    if cd.data_key == 'avg':
                        min5_avg = float(cd.data_value)
                if cd.period == '15min':
                    if cd.data_key == 'avg':
                        min15_avg = float(cd.data_value)
                    if cd.data_key == 'avg_high_low':
                        min15_avg_high_low = float(cd.data_value)
                    if cd.data_key == 'std':
                        min15_std = float(cd.data_value)
                    if cd.data_key == 'trend':
                        min15_trend = cd.data_value
                if cd.period == '30min':
                    if cd.data_key == 'avg':
                        min30_avg = float(cd.data_value)
                if cd.period == '60min':
                    if cd.data_key == 'avg':
                        min60_avg = float(cd.data_value)
                if cd.period == '1day':
                    if cd.data_key == 'avg':
                        day1_avg = float(cd.data_value)
            except Exception as e:
                logger.error(e)
                logger.error(u"缓存数据未完成 跳过 " + trade_name)
                return False, round(0.0, int(symbol.price_precision)), 0.0

    # 策略开始判断
    count_price = float(buy_order.price) * (
            1 + huobi.global_settings.INCOME_MINI + huobi.global_settings.INCOME_INCR_MAX)
    sell_price = cur_price if cur_price > count_price else count_price

    # 止盈利 见好就收
    up_irr = 1 + huobi.global_settings.INCOME_MINI + huobi.global_settings.INCOME_INCR_MAX
    if not can_sell and cur_price and cur_price > float(buy_order.price) * up_irr:
        can_sell = True
        count_price = float(buy_order.price) * up_irr
        sell_price = cur_price if cur_price > count_price else count_price
        logger.info(
            u'盈利了 利率 %f 当前价格 %f 计算价格 %f' % (up_irr, cur_price, count_price))

        # 马上就不盈利了
    ben_irr = 1 + huobi.global_settings.INCOME_MINI + 0.001
    if not can_sell and cur_price and cur_price > float(buy_order.price) * ben_irr:
        can_sell = True
        count_price = float(buy_order.price) * ben_irr
        sell_price = cur_price if cur_price > count_price else count_price
        logger.info(
            u'保本 利率 %f 当前价格 %f 计算价格 %f' % (ben_irr, cur_price, count_price))

    # else:
    #     # 买单时间
    #     timediff = int(time.time()) - int(buy_order.finished_at) / 1000
    #     if timediff < huobi.global_settings.SELL_ORDER_MAX_WAIT_TIME:
    #         can_sell = False

    # 止损失 可能瀑布了
    # if not can_sell and cur_price and cur_price < float(buy_order.price) * (1 - huobi.global_settings.INCOME_DECR_MAX):
    #     can_sell = True
    #     count_price = float(buy_order.price) * (1 - huobi.global_settings.INCOME_DECR_MAX)
    #     sell_price = cur_price if cur_price > count_price else count_price
    #     logger.info(
    #         u'强制止跌 利率 %f 当前价格 %f 计算价格 %f' % (huobi.global_settings.INCOME_DECR_MAX, cur_price, count_price))

    # 还没到订单等待时间
    # if not can_sell and sell_timediff < huobi.global_settings.SELL_ORDER_MAX_WAIT_TIME:
    #     can_sell = False

    # 每1分钟 每15分钟 都在 上升 不卖
    if coin_trend('1min', min1_trend): # or coin_trend('15min', min15_trend):
        can_sell = False
        sell_price = cur_price

    # 校验 卖单价格
    if can_sell:
        if sell_price < (float(buy_order.price) * (1 - huobi.global_settings.INCOME_DECR_MAX)):
            logger.info(u" 价格计算错误 " + trade_name + u" 买 " + str(buy_order.price) + u" 卖 " + str(sell_price))
            count_price = float(buy_order.price) * (
                    1 + huobi.global_settings.INCOME_MINI + huobi.global_settings.INCOME_INCR_MAX)
            sell_price = cur_price if cur_price > count_price else count_price
    else:
        sell_price = cur_price

    sell_count = round(float(buy_order.amount) - float(buy_order.field_fees), int(symbol.amount_precision))
    logger.info(u'执行卖单策略 结果 %s 价格 %f 数量 %f' % (str(can_sell), round(sell_price, int(symbol.price_precision)),
                                               sell_count))
    return can_sell, round(sell_price, int(symbol.price_precision)), sell_count


def resell_match(buy_order, sell_order, trade_name):
    '''
    重新挂卖单

    误区 不能拿时间来判断涨跌  要使用当前币价为主导

    通过尝试 还做不到止跌

    卖单挂单时间太长 导致交易队列占满 需要重新挂卖单
    1. 卖单大于最大等待时间 考虑重新下单 每大于一次 下调 0.001
    1.1 举例 最大收益是 0.01 10个最大等待后 收益降为 0.0
    2. 买单挂单大于2个小时 每大于1小时 下调 0.002
    '''

    can_sell = False
    sell_price = None

    # 买单时间
    timediff = int(time.time()) - int(buy_order.finished_at) / 1000
    # 获取精度
    symbol = Symbol.objects.get(trade_name=trade_name)

    # 获取缓存数据
    cur_price = None
    min1_avg = None
    min5_avg = None
    min15_avg = None
    min15_avg_high_low = None
    min15_std = None
    min30_avg = None
    min60_avg = None
    day1_avg = None

    cache_data_list = CacheData.objects.filter(trade_name=trade_name)
    if cache_data_list and len(cache_data_list) > 0:
        # 准备缓存数据
        for cd in cache_data_list:
            try:
                if cd.period == '1min':
                    if cd.data_key == 'realtime':
                        cur_price = float(cd.data_value)
                    if cd.data_key == 'avg':
                        min1_avg = float(cd.data_value)
                if cd.period == '5min':
                    if cd.data_key == 'avg':
                        min5_avg = float(cd.data_value)
                if cd.period == '15min':
                    if cd.data_key == 'avg':
                        min15_avg = float(cd.data_value)
                    if cd.data_key == 'avg_high_low':
                        min15_avg_high_low = float(cd.data_value)
                    if cd.data_key == 'std':
                        min15_std = float(cd.data_value)
                if cd.period == '30min':
                    if cd.data_key == 'avg':
                        min30_avg = float(cd.data_value)
                if cd.period == '60min':
                    if cd.data_key == 'avg':
                        min60_avg = float(cd.data_value)
                if cd.period == '1day':
                    if cd.data_key == 'avg':
                        day1_avg = float(cd.data_value)
            except Exception as e:
                logger.error(e)
                logger.error(u"缓存数据未完成 跳过 " + trade_name)
                return False, round(0.0, int(symbol.price_precision)), 0.0

    if sell_order:
        # 有卖单的情况
        # 要按 买单的完成时间
        # timediff = int(time.time()) - int(buy_order.finished_at) / 1000
        # # 几个卖单超时时间
        # h = timediff / huobi.global_settings.SELL_ORDER_MAX_WAIT_TIME
        # sell_timediff = int(time.time()) - int(sell_order.created_at) / 1000
        # logger.info(sell_order.symbol + u' 买单 ' + buy_order.id + u' 已完成时长 ' + str(
        #     timediff) + u' 秒' + u' 卖单 ' + sell_order.id + u' 已进行时长 ' + str(sell_timediff) + u' 秒')

        # 超时卖单 调整策略
        # if not can_sell and sell_timediff > huobi.global_settings.SELL_ORDER_MAX_WAIT_TIME:
        #     if h > 0:  # 严重超时
        #         can_sell = True
        #         count_price = float(sell_order.price) * (
        #                 1 + huobi.global_settings.INCOME_MINI + huobi.global_settings.INCOME_INCR_MAX - 0.001 * h)
        #         sell_price = cur_price if cur_price > count_price else count_price
        #         logger.info(u'买单拖延时间太长 当前价格 %f 计算价格 %f' % (cur_price, count_price))

        # 买单超过两个小时 卖单还卖不出去 以0.002速度递减
        # if not can_sell and timediff > 2 * 3600:
        #     can_sell = True
        #     count_price = float(sell_order.price) * (
        #             1 + huobi.global_settings.INCOME_MINI + huobi.global_settings.INCOME_INCR_MAX - 0.002 * h)
        #     sell_price = cur_price if cur_price > count_price else count_price
        #     logger.info(u'挂单超过2小时 快速降低利率 止跌利率 %f 当前价格 %f 计算价格 %f' % (
        #         huobi.global_settings.INCOME_MINI + huobi.global_settings.INCOME_INCR_MAX - 0.002 * h, cur_price,
        #         count_price))

        # if can_sell:
        #     if (float(sell_order.price) >= sell_price * (1 - 0.0005)) and (float(sell_order.price) <= sell_price * (
        #             1 + 0.0005)):
        #         # 目前是为了防止2个小时以上的单子重复撤销挂单
        #         logger.info(u'当前卖单价格 %s 与 计算预卖价格 %f 误差在0.0005之内不卖' % (sell_order.price, sell_price))
        #         can_sell = False
        # else:
        #     # 防止None
        #     sell_price = cur_price
        can_sell, sell_price = sell_match(buy_order, trade_name)
    else:
        can_sell, sell_price = sell_match(buy_order, trade_name)
    sell_count = round(float(buy_order.amount) - float(buy_order.field_fees), int(symbol.amount_precision))
    logger.info(u'执行卖单策略 结果 %s 价格 %f 数量 %f' % (str(can_sell), round(sell_price, int(symbol.price_precision)),
                                               sell_count))
    return can_sell, round(sell_price, int(symbol.price_precision)), sell_count


def coin_trend(period, trend):
    '''
    简单判断 最新的4次是正的 则是在涨
    :param trend:
    :return:
    '''
    up = False
    logger.info(u"趋势策略 分析参考值 %s" % trend)
    tmp_trend = trend.split(',')

    tmp_arr = []
    for m in tmp_trend:
        tmp_arr.append(float(m))

    fu_count = 0

    for w in range(3):
        # 最新的数据小于0 开始在降了
        if w == 0 and tmp_arr[len(tmp_trend) - 1 - w] < 0.001:
            up = False
            break
        if tmp_arr[len(tmp_trend) - 1 - w] < 0:
            fu_count = fu_count + 1
        if tmp_arr[len(tmp_trend) - 1 - w] < 0 - 0.001:
            up = False
            break
        else:
            up = True

    # if not up and np.sum(tmp_arr) > 0:
    #     up = True
    if up and fu_count > 2:
        logger.info(u"趋势策略 包含多个负值 " + period + " 趋势上涨趋势 " + str(up))
        up = False

    logger.info(u"趋势策略 " + period + " 趋势上涨趋势 " + str(up))
    return up
