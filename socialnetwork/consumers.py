import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        current_id = self.scope['user'].id
        friend_user_id = self.scope['url_route']['kwargs']['id']
        if int(current_id) > int(friend_user_id):
            self.room_name = f'{current_id}-{friend_user_id}'
        else:
            self.room_name = f'{friend_user_id}-{current_id}'

        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        print(json_data)
        message = json_data['message']
        username = json_data['username']
        sent_to = json_data['friend']

        await self.save_message(username, self.room_group_name, message, sent_to)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def save_message(self, username, chat_name, message, sent_to):
        username = User.objects.get(username=username)
        Chat.objects.create(
            message_owner=username, chat_message=message, chat_name=chat_name, sent_to=sent_to)
