import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    # Runs when JavaScript creates a WebSocket connection
    # and the URL matches the route in routing.py
    async def connect(self):

        # Get conversation_id from URL
        # Example: ws/chat/18/ -> conversation_id = 18
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]

        # Create group name for this conversation
        # Example: chat_18
        self.room_group_name = f"chat_{self.conversation_id}"

        # Add current WebSocket connection to the group
        await self.channel_layer.group_add(

            # Group name
            self.room_group_name,

            # Unique channel id automatically created by Channels
            # Represents this specific WebSocket connection
            self.channel_name
        )

        # Accept the WebSocket connection
        # Without this, connection will be rejected
        await self.accept()

    # Runs automatically when WebSocket disconnects
    async def disconnect(self, close_code):

        # Remove current connection from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Runs whenever JavaScript sends data using socket.send()
    async def receive(self, text_data):
        print("Received data:", text_data)

        # Convert incoming JSON string into Python dictionary
        data = json.loads(text_data)

        # Get event type
        event_type = data.get("type")

        if event_type == "chat":
            print("Saving message...")
            # Extract message text
            message = data.get("message")

            # Get logged-in user from WebSocket scope
            # AuthenticationMiddleware provides this
            user = self.scope["user"]

            # Prevent unauthenticated users from sending messages
            if not user.is_authenticated:
                return

            # Save message into database
            saved_message = await self.save_message(
                self.conversation_id,
                user,
                message
            )
            print("Broadcasting...")
            # Send message to everyone connected
            # to this conversation group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    # Channels uses this value to determine
                    # which method should be called
                    # "chat_message" -> chat_message()
                    "type": "chat_message",

                    # Message content
                    "message": saved_message.content,

                    # Sender's id
                    "sender_id": saved_message.sender.id,

                    # Sender's username
                    "sender_username": saved_message.sender.username,

                    "timestamp": saved_message.timestamp.strftime("%H:%M"),
                }
            )

        elif event_type == "audio_call":

            user = self.scope["user"]

            await self.channel_layer.group_send(
            
                self.room_group_name,

                {              
                    "type": "incoming_audio_call",
                    "caller": user.username,
                    "caller_id": user.id,
                }

            )

        elif event_type == "video_call":
            print("Video call request received")

            user = self.scope["user"]

            await self.channel_layer.group_send(
            
                self.room_group_name,

                {               
                    "type": "incoming_video_call",
                    "caller": user.username,
                    "caller_id": user.id,
                }

            )

        elif event_type == "call_accepted":

            user = self.scope["user"]

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "call_accepted",
                    "username": user.username,
                }
            )

        elif event_type == "call_declined":
        
            user = self.scope["user"]

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "call_declined",
                    "username": user.username,
                }
            )

        elif event_type == "call_cancelled":
            print("Call cancelled event received")
        
            user = self.scope["user"]

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "call_cancelled",
                    "username": user.username,
                }
            )

    # Called automatically because
    # group_send() had "type": "chat_message"
    async def chat_message(self, event):
        print("chat_message() called")

        # Send data back to browser through WebSocket
        await self.send(
            text_data=json.dumps({
                "type": "chat",

                # Message text
                "message": event["message"],

                # Sender id
                "sender_id": event["sender_id"],

                # Sender username
                "sender_username": event["sender_username"],

                "timestamp": event.get("timestamp"),
            })
        )

    async def incoming_audio_call(self, event):
        await self.send(text_data=json.dumps({
            "type": "incoming_audio_call",
            "caller": event["caller"],
            "caller_id": event["caller_id"],
        }))

    async def incoming_video_call(self, event):
        print("incoming_video_call() called")
        await self.send(text_data=json.dumps({
            "type": "incoming_video_call",
            "caller": event["caller"],
            "caller_id": event["caller_id"],
        }))

    # Database operations are synchronous
    # This decorator allows them to be safely used inside async code
    @database_sync_to_async
    def save_message(self, conversation_id, user, content):

        # Get conversation object
        conversation = Conversation.objects.get(
            id=conversation_id
        )

        # Create and save message in database
        return Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )

    async def call_accepted(self, event):

        await self.send(text_data=json.dumps({
            "type": "call_accepted",
            "username": event["username"],
        }))

    async def call_declined(self, event):

        await self.send(text_data=json.dumps({
            "type": "call_declined",
            "username": event["username"],
        }))

    async def call_cancelled(self, event):

        await self.send(text_data=json.dumps({
            "type": "call_cancelled",
            "username": event["username"],
        }))

