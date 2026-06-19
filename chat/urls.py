from django.urls import path
from .views import (
    chat_room,
    user_list,
    start_chat,
)

urlpatterns = [
    path("<int:conversation_id>/", chat_room, name="chat-room"),
    path("users/", user_list, name="user-list"),
    path(
        "start-chat/<int:user_id>/",
        start_chat,
        name="start-chat"
    ),
]