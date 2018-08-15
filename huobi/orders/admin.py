from django.contrib import admin

from models import OrderRelation, Symbol, Order, Setting


# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'symbol', 'type', 'state', 'created_at', 'finished_at', 'canceled_at', 'price', 'amount',
        'field_amount',
        'field_cash_amount', 'field_fees',)


class OrderRelationAdmin(admin.ModelAdmin):
    list_display = ('buy_order', 'sell_order', 'state',)


class SymbolAdmin(admin.ModelAdmin):
    list_display = ('trade_name', 'price_precision', 'amount_precision', 'symbol_partition', 'state',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderRelation, OrderRelationAdmin)
admin.site.register(Symbol, SymbolAdmin)


class SettingAdmin(admin.ModelAdmin):
    list_display = ('setting_key', 'setting_value',)


admin.site.register(Setting, SettingAdmin)