from django.contrib import admin
from Network_Controller.models import Trapdoor,Food,Heartbeat

admin.site.register(Food)
admin.site.register(Heartbeat)
admin.site.register(Trapdoor)