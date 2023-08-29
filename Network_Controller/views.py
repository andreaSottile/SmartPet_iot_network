from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Network_Controller.models import *
from iot.network_manager import boot
from iot.pubsubconfig import *
from iot.utils import command_sender


def index(request):
    context = {"status": "not-started"}
    return render(request, "index.html", context)

def food_refill_start(containerID):
    pairObject = Pair.objects.filter(nodeIdCOAP=containerID).first()
    if pairObject is not None:
        pairSensor = pairObject.nodeIdMQTT
        command_sender(COMMAND_REFILL_START_FOOD, pairSensor)
    else:
        print("Non trovato nodo paired")
def food_refill_stop(containerID):
    pairObject = Pair.objects.filter(nodeIdCOAP=containerID).first()
    if pairObject is not None:
        pairSensor = pairObject.nodeIdMQTT
        command_sender(COMMAND_REFILL_STOP_FOOD, pairSensor)
    else:
        print("Non trovato nodo paired")
def hatch_open(hatchID):
    pairObject = Pair.objects.filter(nodeIdCOAP=hatchID).first()
    if pairObject is not None:
        pairSensor = pairObject.nodeIdMQTT
        command_sender(COMMAND_CLOSE_HATCH, pairSensor)
    else:
        print("Non trovato nodo paired")
def hatch_close(hatchID):
    pairObject = Pair.objects.filter(nodeIdCOAP=hatchID).first()
    if pairObject is not None:
        pairSensor = pairObject.nodeIdMQTT
        command_sender(COMMAND_CLOSE_HATCH, pairSensor)
    else:
        print("Non trovato nodo paired")
def hatch_allow_open(hatchID):
    hatch = HatchConfig.objects.get(hatchId = hatchID)
    hatch.allowOpen = True;
    hatch.save()

def hatch_forbid_open(hatchID):
    hatch = HatchConfig.objects.get(hatchId = hatchID)
    hatch.allowOpen = False;
    hatch.save()
def threshold_max(containerID, lvl):
    food = FoodConfig.objects.get(containerID = containerID)
    food.lvlThresholdStop = lvl;
    food.save()
def threshold_min(containerID, lvl):
    food = FoodConfig.objects.get(containerID = containerID)
    food.lvlThresholdStart = lvl;
    food.save()

def heartbeat_max(petID, lvl):
    heartbeat = HeartBeatConfig.objects.get(petID = petID)
    heartbeat.high_Threshold = lvl;
    heartbeat.save()
def heartbeat_min(petID, lvl):
    heartbeat = HeartBeatConfig.objects.get(petID = petID)
    heartbeat.low_Threshold = lvl;
    heartbeat.save()

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

def client_list(request):
    context = {"data": real_time_live_clients(request)}
    return render(request, "client_list.html", context)


def config_page(request, node_id, node_type, is_actuator):
    context = {
        'client': LiveClient.objects.get(node_id=node_id),
        'node_id': node_id,
        'node_type': node_type,
        'is_actuator': is_actuator,
    }
    return render(request, "config.html", context)