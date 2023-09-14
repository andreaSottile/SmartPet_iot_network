"""
URL configuration for Network_Controller project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('network/', views.network_start, name='network'),
    path('client-nodes/', views.client_list, name='clients'),
    path('config_page/<str:node_id>/<str:node_type>/', views.config_page, name='config'),
    path('clientapp/food/refill/start/<str:node_id>/', views.food_refill_start, name='food_start_refill'),
    path('clientapp/food/refill/stop/<str:node_id>/', views.food_refill_stop, name='food_stop_refilling'),
    path('clientapp/hatch/actuator/open/<str:node_id>/', views.hatch_open, name='hatch_open'),
    path('clientapp/hatch/actuator/close/<str:node_id>/', views.hatch_close, name='hatch_close'),
    path('clientapp/hatch/permission/allow/<str:node_id>/', views.hatch_allow_open, name='hatch_unlock'),
    path('clientapp/hatch/permission/deny/<str:node_id>/', views.hatch_forbid_open, name='hatch_lock'),
    path('clientapp/heartbeat/set/min/<str:node_id>/<int:value>/', views.heartbeat_min, name='heartbeat_set_min'),
    path('clientapp/heartbeat/set/max/<str:node_id>/<int:value>/', views.heartbeat_max, name='heartbeat_set_max'),
    path('clientapp/food/set/min/<str:node_id>/<int:value>/', views.threshold_min, name='food_set_min'),
    path('clientapp/food/set/max/<str:node_id>/<int:value>/', views.threshold_max, name='food_set_max'),
    path('api/real-time-food/', views.real_time_food, name='real_time_food'),
    path('api/real-time-heartbeat/', views.real_time_heartbeat, name='real_time_heartbeat'),
    path('api/real-time-hatch/', views.real_time_hatch, name='real_time_hatch'),
    path('api/real-time-live-clients/', views.real_time_live_clients, name='real_time_live_clients'),
    path('', views.index, name='index'),
]
