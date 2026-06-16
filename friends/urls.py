from django.urls import path
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
    path("list/", list_friends),
    path("pending/", pending_requests),
]