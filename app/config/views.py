from django.http import HttpResponse
from django.shortcuts import render


def health_check(request):
    return HttpResponse('OK', status=200)


def ustukan_view(request):
    return render(request, "ustukan.html")

