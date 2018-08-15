from django.contrib import admin
from models import KlineHistoryBTCUSDT


# Register your models here.
class KlineHistoryBTCUSDTAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'symbol', 'period', 'col_open', 'col_close', 'col_low', 'col_high', 'col_vol', 'col_updown_vol',
        'col_updown_rate',)
    # list_editable = ('state',)
    search_fields = ('created_at', 'symbol', 'period', 'col_open',)


admin.site.register(KlineHistoryBTCUSDT, KlineHistoryBTCUSDTAdmin)
