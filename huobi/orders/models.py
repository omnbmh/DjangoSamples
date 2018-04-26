# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import HuobiService

# Create your models here.
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Order(models.Model):
    id = models.CharField(max_length=100, verbose_name='订单ID', primary_key=True)
    account_id = models.CharField(max_length=100, verbose_name='账户ID')
    amount = models.CharField(max_length=100, verbose_name='订单数量')
    canceled_at = models.CharField(max_length=100, verbose_name='订单撤销时间')
    created_at = models.CharField(max_length=100, verbose_name='订单创建时间')
    field_amount = models.CharField(max_length=100, verbose_name='已成交数量')
    field_cash_amount = models.CharField(max_length=100, verbose_name='已成交总金额')
    field_fees = models.CharField(max_length=100, verbose_name='已成交手续费')
    finished_at = models.CharField(max_length=100, verbose_name='最后成交时间')
    price = models.CharField(max_length=100, verbose_name='订单价格')
    source = models.CharField(max_length=100, verbose_name='订单来源')
    state = models.CharField(max_length=100, verbose_name='订单状态')
    symbol = models.CharField(max_length=100, verbose_name='交易对')
    type = models.CharField(max_length=100, verbose_name='订单类型')

    def __unicode__(self):
        return self.symbol + ' - ' + self.id

    def refresh(self):
        # 查询订单信息初始化订单
        rlt_json = HuobiService.order_info(self.id)
        # print rlt_json
        if rlt_json[u'status'] == 'ok':
            self.account_id = rlt_json[u'data'][u'account-id']
            self.state = rlt_json[u'data'][u'state']
            self.canceled_at = rlt_json[u'data'][u'canceled-at']
            self.symbol = rlt_json[u'data'][u'symbol']
            self.finished_at = rlt_json[u'data'][u'finished-at']
            self.created_at = rlt_json[u'data'][u'created-at']
            self.type = rlt_json[u'data'][u'type']
            self.field_fees = rlt_json[u'data'][u'field-fees']
            self.price = rlt_json[u'data'][u'price']
            self.amount = rlt_json[u'data'][u'amount']
            self.source = rlt_json[u'data'][u'source']
            self.field_amount = rlt_json[u'data'][u'field-amount']
            self.field_cash_amount = rlt_json[u'data'][u'field-cash-amount']
            self.save()
            print(u'订单 ' + self.id + u' 刷新成功')

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单列表"


class OrderRelation(models.Model):
    '''
    状态 A 新增 P 进行中 C 撤销 S 成功
    '''
    buy_order = models.ForeignKey(Order, to_field='id', related_name='buy_order_relation', verbose_name='买单')
    sell_order = models.ForeignKey(Order, to_field='id', related_name='sell_order_relation', null=True, blank=True,
                                   verbose_name='卖单')
    state = models.CharField(max_length=10, verbose_name='状态')

    class Meta:
        verbose_name = "买卖交易关系"
        verbose_name_plural = "买卖交易关系列表"


class Symbol(models.Model):
    base_currency = models.CharField(max_length=100, verbose_name='基础币种')
    quote_currency = models.CharField(max_length=100, verbose_name='计价币种')
    price_precision = models.CharField(max_length=100, verbose_name='价格精度位数（0为个位）')
    amount_precision = models.CharField(max_length=100, verbose_name='数量精度位数（0为个位）')
    symbol_partition = models.CharField(max_length=100, verbose_name='交易区 main主区，innovation创新区，bifurcation分叉区')
    trade_name = models.CharField(max_length=100, verbose_name='交易对 ethusdt')
    state = models.CharField(max_length=10, verbose_name='是有有效 0-no 1-yes')

    class Meta:
        verbose_name = "交易币种"
        verbose_name_plural = "交易币种列表"


class CacheData(models.Model):
    '''
    缓存数据
    '''
    trade_name = models.CharField(max_length=100, verbose_name='交易币种')
    period = models.CharField(max_length=100, verbose_name='周期')
    data_key = models.CharField(max_length=100, verbose_name='数据key')
    data_value = models.CharField(max_length=100, verbose_name='数据')


class Setting(models.Model):
    '''
    配置表
    '''
    setting_key = models.CharField(max_length=100, verbose_name='配置项')
    setting_value = models.CharField(max_length=100, verbose_name='配置值')

    class Meta:
        verbose_name = "配置"
        verbose_name_plural = "配置列表"


class OrderRelationHistory(models.Model):
    '''
    买卖交易关系历史表
    '''
    buy_order = models.ForeignKey(Order, to_field='id', related_name='buy_order_relation_history', verbose_name='买单')
    sell_order = models.ForeignKey(Order, to_field='id', related_name='sell_order_relation_history',
                                   verbose_name='卖单')
    created_at = models.CharField(max_length=100, verbose_name='创建时间')
