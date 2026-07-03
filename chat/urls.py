from django.urls import path
from .views import (
    chat_room,
)

urlpatterns = [
    path("<int:conversation_id>/", chat_room, name="chat-room-detail"),]