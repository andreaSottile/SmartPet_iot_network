from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Network_Controller.models import *
from iot.data_manager import get_pair_object_from_actuator
from iot.network_manager import boot, command_sender
from iot.pubsubconfig import *


def index(request):
    context = {"status": "not-started"}
    return render(request, "index.html", context)


def food_refill_start(request, node_id):
    print(node_id)
    paired, pair_object = get_pair_object_from_actuator(node_id)
    if paired:
        command_sender(COMMAND_REFILL_START_FOOD, pair_object)
    else:
        print("Non trovato nodo paired")
    return HttpResponse(status=200)


def food_refill_stop(request, node_id):
    paired, pair_object = get_pair_object_from_actuator(node_id)
    if paired:
        command_sender(COMMAND_REFILL_STOP_FOOD, pair_object)
    else:
        print("Non trovato nodo paired")
    return HttpResponse(status=200)


def hatch_open(request, node_id):
    paired, pair_object = get_pair_object_from_actuator(node_id)
    if paired:
        command_sender(COMMAND_OPEN_HATCH, pair_object)
    else:
        print("Non trovato nodo paired")
    return HttpResponse(status=200)


def hatch_close(request, node_id):
    paired, pair_object = get_pair_object_from_actuator(node_id)
    if paired:
        command_sender(COMMAND_CLOSE_HATCH, pair_object)
    else:
        print("Non trovato nodo paired")
    return HttpResponse(status=200)


def hatch_allow_open(request, node_id):
    hatch, _ = HatchConfig.objects.get_or_create(hatchId=node_id)
    hatch.allowOpen = True
    hatch.save()
    return config_page(request, node_id, "hatch")


def hatch_forbid_open(request, node_id):
    hatch, _ = HatchConfig.objects.get_or_create(hatchId=node_id)
    hatch.allowOpen = False
    hatch.save()
    return config_page(request, node_id, "hatch")


def threshold_max(request, node_id, value):
    print(value)
    food, _ = FoodConfig.objects.get_or_create(containerID=node_id)
    food.lvlThresholdStop = value
    food.save()
    return HttpResponse(status=200)


def threshold_min(request, node_id, value):
    food, _ = FoodConfig.objects.get_or_create(containerID=node_id)
    food.lvlThresholdStart = value
    food.save()
    return HttpResponse(status=200)


def heartbeat_max(request, node_id, value):
    heartbeat, _ = HeartBeatConfig.objects.get_or_create(petID=node_id)
    heartbeat.high_Threshold = value
    heartbeat.save()
    return HttpResponse(status=200)


def heartbeat_min(request, node_id, value):
    heartbeat, _ = HeartBeatConfig.objects.get_or_create(petID=node_id)
    heartbeat.low_Threshold = value
    heartbeat.save()
    return HttpResponse(status=200)


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
    clients = LiveClient.objects.order_by('-lastInteraction')[:100].values('nodeId', 'nodeCoapName', 'nodeCoapAddress',
                                                                           'nodeType', 'isFree', 'isActuator',
                                                                           'lastInteraction')
    print(clients)
    context = {"data": clients}
    return render(request, "client_list.html", context)


def config_page(request, node_id, node_type):
    context = {
        'client': LiveClient.objects.get(nodeId=node_id),
        'node_id': node_id,
        'node_type': node_type
    }
    return render(request, "config.html", context)
