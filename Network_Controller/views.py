from django.shortcuts import render

from iot.network_manager import boot


def index(request):
    context = {"status": "not-started"}
    return render(request, "index.html", context)


def network_start(request):
    boot()
    context = {"status": "started"}
    return render(request, "network.html", context)
