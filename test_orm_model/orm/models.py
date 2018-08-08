# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


# Create your models here.
class ShardingTable(models.Model):
    username = models.CharField(max_length=255)

    class Meta:
        abstract = True


class ShardingTableOne(ShardingTable):
    class Meta:
        db_table = 'sharding_talbe_one'  # 默认会使用ClassName Lower


class ShardingTableTwo(ShardingTable):
    class Meta:
        db_table = 'sharding_talbe_two'  # 默认会使用ClassName Lower
