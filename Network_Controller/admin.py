from django.contrib import admin
from Network_Controller.models import *

admin.site.register_sensor(Food, )
admin.site.register_sensor(Heartbeat, )
admin.site.register_sensor(Hatch, )
admin.site.register_sensor(HeartBeatConfig, )
admin.site.register_sensor(HatchConfig, )
admin.site.register_sensor(FoodConfig, )
admin.site.register_sensor(LiveClients, )
