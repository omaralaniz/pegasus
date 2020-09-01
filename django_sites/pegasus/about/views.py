from django.shortcuts import render

def index(request):
    return render(request, 'about/index.html')


def brenna(request):
    return render(request, 'about/brenna.html')


def fatma(request):
    return render(request, 'about/fatma.html')


def wafi(request):
    return render(request, 'about/wafi.html')


def zachary(request):
    return render(request, 'about/zachary.html')


def adan(request):
    return render(request, 'about/adan.html')


def quan(request):
    return render(request, 'about/quan.html')


def omar(request):
    return render(request, 'about/omar.html')
