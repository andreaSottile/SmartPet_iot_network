from django.shortcuts import render


def index(request):
    context = {"test"}
    return render(request, "index.html", context)
