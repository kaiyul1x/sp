from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TaskProgressConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('connect')
        self.result_id = self.scope['url_route']['kwargs']['pk']
        await self.channel_layer.group_add(
            self.result_id,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        print('disconnect')
        # Leave room group
        await self.channel_layer.group_discard(
            self.result_id,
            self.channel_name
        )

    async def progress_message(self, event):
        await self.send_json(
            {
                'type': 'progress.message',
                'content': event['content']
            }
        )
