import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self): # This runs when user opens websocket
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"] # This gets conversation_id from url
        self.room_group_name = f"chat_{self.conversation_id}" # This Create Group name

        await self.channel_layer.group_add(  # Adds a WebSocket connection into a group
            self.room_group_name,  # first parameter group name
            self.channel_name      # second parameter channel name which is automatically created by channels, it represents unique id for this specific websocket connection
        )

        await self.accept() # Now WebSocket is officially open.

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        user = self.scope["user"]

        if not user.is_authenticated:
            return

        saved_message = await self.save_message(
            self.conversation_id,
            user,
            message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_message.content,
                "sender_id": saved_message.sender.id,
                "sender_username": saved_message.sender.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "sender_username": event["sender_username"],
        }))

    @database_sync_to_async
    def save_message(self, conversation_id, user, content):
        conversation = Conversation.objects.get(id=conversation_id)

        return Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )