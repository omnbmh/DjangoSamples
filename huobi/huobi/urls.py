"""huobi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

import orders.views
import order_admin.views
import kline.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # login page
    # url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^$', order_admin.views.index),
    url(r'^manage/account$', order_admin.views.manage_account),
    url(r'^manage/monitor.html', order_admin.views.manage_monitor),

    url(r'^thread/kline/start', orders.views.start_t_kline_history),

    url(r'^order/init/symbol', orders.views.init_db_symbol),
    url(r'^order/init/order', orders.views.init_db_order),
    url(r'^order/refresh_settings', orders.views.refresh_settings),

    url(r'^kline/ref', kline.views.kline_ref),
    url(r'^kline/hb10', kline.views.kline_hb10),
    url(r'^kline/data.json', kline.views.kline_data),
    url(r'^kline/amount_data.json', kline.views.kline_amount_data),
    url(r'^kline/kline_hb10_data.json', kline.views.kline_hb10_data),
    url(r'^kline/init', kline.views.kline_history_init),

    url(r'^trade/start_work', orders.views.start_work),
    # 4 test
    # url(r'^test', orders.views.test),
]
