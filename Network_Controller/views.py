from django.shortcuts import render


def index(request):
    context = {"field": "test"}
    return render(request, "index.html", context)
