from django.urls import path
from .views import chat_list, start_chat, user_list


from .views import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    list_friends,
    pending_requests
)

urlpatterns = [
    path("send/", send_friend_request),
    path("accept/<int:request_id>/", accept_friend_request),
    path("reject/<int:request_id>/", reject_friend_request),
    path("pending/", pending_requests),
    path("list/", user_list, name="user-list"),
    path("", chat_list, name="chat-list"),
    path("start/<int:user_id>/", start_chat, name="start-chat"),
]


