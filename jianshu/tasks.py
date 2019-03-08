# Create your tasks here
from __future__ import absolute_import, unicode_literals

import json
import time
from decimal import Decimal

from sp import celery_app
from channels import layers
from django.core.cache import cache
from asgiref.sync import async_to_sync

from .spider import increase_views


@celery_app.task(bind=True)
def increase_views_task(self, data):
    start_time = Decimal(time.time())
    generate = increase_views(data['increase_count'], data['post_num'], data['csrf_token'], data['uuid'])
    layer = layers.get_channel_layer()
    try:
        for progress in generate:
            self.update_state(state='PROGRESS', meta={'exc': progress})
            async_to_sync(layer.group_send)(self.request.id, {
                "type": "progress.message",
                "content": json.dumps({
                    'status': 'PROGRESS', 'progress': progress
                })
            })
    except Exception as e:
        self.update_state(state='FAIL', meta={'exc': str(e)})
        async_to_sync(layer.group_send)(self.request.id, {
            "type": "progress.message",
            "content": json.dumps({
                'status': 'FAIL', 'progress': 0
            })
        })
        return 'FAIL {}'.format(e)
    else:
        cache.delete(data['post_num'])
        cache.delete(self.request.id)
        async_to_sync(layer.group_send)(self.request.id, {
            "type": "progress.message",
            "content": json.dumps({
                'status': 'FINISH', 'progress': 1
            })
        })
        async_to_sync(layer.group_send)(self.request.id, {
            "type": "progress.force_disconnect",
        })
        end_time = Decimal(time.time())
        return 'FINISH 耗时{}s'.format(end_time - start_time)
