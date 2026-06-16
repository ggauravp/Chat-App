from django.shortcuts import render

# Create your views here.

def chat_room(request, conversation_id=None):
    return render(request, "chat/chat.html", {
        "conversation_id": conversation_id
    })