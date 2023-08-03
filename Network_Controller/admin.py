from django.contrib import admin

from Network_Controller.models import *

admin.site.register(Food, )
admin.site.register(Heartbeat)
admin.site.register(Hatch)
admin.site.register(HeartBeatConfig)
admin.site.register(HatchConfig)
admin.site.register(FoodConfig)
admin.site.register(LiveClient)
