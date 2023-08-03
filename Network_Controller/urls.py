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
    path('api/real-time-food/', views.real_time_food, name='real_time_food'),
    path('api/real-time-heartbeat/', views.real_time_heartbeat, name='real_time_heartbeat'),
    path('api/real-time-hatch/', views.real_time_hatch, name='real_time_hatch'),
    path('api/real-time-live-clients/', views.real_time_live_clients, name='real_time_live_clients'),
    path('', views.index, name='index'),
]
