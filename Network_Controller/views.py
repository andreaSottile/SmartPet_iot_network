from django.db.models import OuterRef, Subquery, Max
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Network_Controller.models import *
from iot.mqttnode import command_sender
from iot.network_manager import boot
from iot.pubsubconfig import *



def index(request):
    context = {"status": "not-started"}
    return render(request, "index.html", context)

def food_refill_start(containerID):
    command_sender(containerID, COMMAND_REFILL_START_FOOD, containerID + + " filling")
def food_refill_stop(containerID):

def hatch_open(hatchID):

def hatch_close(hatchID):

def hatch_config_setPermission(hatchID):

def food_config_setMax(containerID):

def food_config_setMin(containerID):


@csrf_exempt
def network_start(request):
    boot(request)
    context = {"status": "started"}
    return render(request, "network.html", context)


def real_time_food(request):
    data = Food.objects.order_by('-time')[:100].values('time', 'lvl', 'containerID')
    return JsonResponse(list(data), safe=False)


def real_time_heartbeat(request):
    data = Heartbeat.objects.order_by('-time')[:100].values('time', 'frequency', 'petID')
    return JsonResponse(list(data), safe=False)


def real_time_hatch(request):
    data = Hatch.objects.order_by('-time')[:100].values('time', 'hatchId', 'direction_Trigger')
    return JsonResponse(list(data), safe=False)


def real_time_live_clients(request):
    data = LiveClient.objects.order_by('-lastInteraction')[:100].values('nodeId', 'nodeCoapName', 'nodeCoapAddress',
                                                                        'nodeType', 'isFree', 'isActuator',
                                                                        'lastInteraction')
    return JsonResponse(list(data), safe=False)
