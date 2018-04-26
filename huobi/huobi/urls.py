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
    url(r'^$', order_admin.views.index),
    url(r'^order/init/symbol', orders.views.init_db_symbol),
    url(r'^order/init/order', orders.views.init_db_order),
    url(r'^order/refresh_settings', orders.views.refresh_settings),
    url(r'^kline/ref', kline.views.kline_ref),
    url(r'^kline/data.json', kline.views.kline_data),
    url(r'^kline/history/(?P<period>\w+)', kline.views.kline_history),

    url(r'^trade/start_work', orders.views.start_work),
]
