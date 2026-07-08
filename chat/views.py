import json
from django.shortcuts import render, get_object_or_404
from .models import Conversation
from django.contrib.auth import get_user_model 
from django.contrib.auth.decorators import login_required

def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    messages = conversation.messages.select_related("sender").order_by("timestamp")

    messages_json = json.dumps([
        {
            "sender_id": msg.sender.id,
            "sender_username": msg.sender.username,
            "message": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M"),
        }
        for msg in messages
    ])

    return render(request, "chat/chat.html", {
        ""
        "conversation_id": conversation_id,
        "messages_json": messages_json,
    })

User = get_user_model()

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # check if conversation already exists
    conversation = Conversation.objects.filter(participants=request.user)\
        .filter(participants=other_user).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect("chat-room", conversation.id)