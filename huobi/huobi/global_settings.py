# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# Settings
INCOME_MINI = 0.004  # 最小收益 千4
INCOME_INCR_MAX = 0.002  # 最大增长收益 收益率 = INCOME_MINI + INCOME_INCR_MAX
INCOME_DECR_MAX = 0.03  # 止损 利率
ORDER_MAX = 2
SELL_ORDER_MAX_WAIT_TIME = 900  # 15分钟 卖单最长等待时间 超过后调整价格
BUY_ORDER_MAX_WAIT_TIME = 600  # 10 买单最长等待时间
USDT_COUNT = 10
# 此处填写APIKEY
ACCESS_KEY = None
SECRET_KEY = None
