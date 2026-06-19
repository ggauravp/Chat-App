from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Conversation


@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    messages = conversation.messages.order_by("timestamp")

    return render(request, "chat/chat.html", {
        "conversation": conversation,
        "conversation_id": conversation_id,
        "messages": messages,
    })