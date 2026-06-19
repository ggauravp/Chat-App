from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Conversation
from django.contrib.auth.models import User

@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    messages = conversation.messages.order_by("timestamp")

    return render(request, "chat/chat.html", {
        "conversation": conversation,
        "conversation_id": conversation_id,
        "messages": messages,
    })



def user_list(request):
    users = User.objects.exclude(id=request.user.id)

    return render(
        request,
        "chat/user_list.html",
        {"users": users}
    )


def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    conversation = (
        Conversation.objects
        .filter(participants=request.user)
        .filter(participants=other_user)
        .first()
    )

    if not conversation:
        conversation = Conversation.objects.create()

        conversation.participants.add(
            request.user,
            other_user
        )

    return redirect(
        "chat-room",
        conversation_id=conversation.id
    )