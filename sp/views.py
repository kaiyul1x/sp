from django.shortcuts import render
from channels.layers import get_channel_layer
from django.http import HttpResponse
from asgiref.sync import async_to_sync

def index(request):
    return render(request, 'index.html')


def send(request, pk):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(pk, {
        "type": "progress.message",
        "content": "Hello there!",
    })
    return HttpResponse('success')
