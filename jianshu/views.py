import uuid
import json

from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from sp import celery_app as app

from .serializers import TaskSerializer
from .spider import get_info
from .tasks import increase_views_task


class PostDetailAPIView(APIView):

    def get(self, request, pk, format=None):
        try:
            data = get_info(pk)
        except Exception as e:
            return Response(data={'detail': '解析失败，请检查文章是否存在。'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data=data)


class TaskDetailAndDestroyAPIView(APIView):

    def get(self, request, pk, format=None):
        result = AsyncResult(id=pk)
        return Response(data={'status': result.status, 'info': result.info})

    def delete(self, request, pk, format=None):
        app.control.terminate(pk)
        post_num = cache.get(pk)
        cache.delete(pk)
        cache.delete(post_num)
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(pk, {
            "type": "progress.message",
            "content": json.dumps({
                'status': 'CANCEL', 'progress': 0
            })
        })
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCreateAPIView(APIView):

    serializer_class = TaskSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        post_num = serializer.data.get('post_num')
        task_id = cache.get(post_num)
        if task_id:
            return Response(data={'task_id': task_id})
        task_id = str(uuid.uuid4())
        cache.set(post_num, task_id)
        cache.set(task_id, post_num)
        result = increase_views_task.apply_async((serializer.data,), task_id=task_id)
        return Response(data={'task_id': result.id}, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        return self.serializer_class
