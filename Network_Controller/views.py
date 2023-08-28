from django.db.models import OuterRef, Subquery, Max
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Network_Controller.models import *
from iot.network_manager import boot


def index(request):
    context = {"status": "not-started"}
    return render(request, "index.html", context)


@csrf_exempt
def network_start(request):
    boot(request)
    context = {"status": "started"}
    return render(request, "network.html", context)


def real_time_food(request):
    # data = Food.objects.order_by('-time')[:100].values('time', 'lvl', 'containerID')

    latest_timestamps = Food.objects.values('containerID').annotate(latest_time=Max('time')).filter(
        containerID=OuterRef('containerID')).values('latest_time')

    # Query to fetch the latest lvl value for each containerID
    latest_lvls = Food.objects.filter(time=Subquery(latest_timestamps)).order_by('containerID', '-time').distinct(
        'containerID').values('containerID', 'lvl')

    latest_lvl_dict = {}
    for item in latest_lvls:
        containerID = item['containerID']
        lvl = item['lvl']
        latest_lvl_dict[containerID] = lvl
    return JsonResponse(latest_lvl_dict, safe=False)
    # return JsonResponse(list(data), safe=False)


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
