from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import FriendRequest, Friendship
from django.contrib.auth.models import User
from .serializers import FriendRequestSerializer
from chat.models import Conversation
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model 
from django.contrib.auth.decorators import login_required

User = get_user_model()

#  USER LIST PAGE
def user_list(request):
    users = User.objects.exclude(id=request.user.id)

    return render(
        request,
        "friends/user_list.html",
        {"users": users}
    )

@login_required
def chat_list(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by("-created_at")

    return render(request, "friends/chat_list.html", {
        "conversations": conversations,
        "current_user" : request.user
    })

#  START CHAT (CREATE OR GET CONVERSATION)
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # try to find existing conversation between 2 users
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    # if not found → create new conversation
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect("chat-room-detail", conversation_id=conversation.id)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    receiver_id = request.data.get("receiver_id")

    try:
        receiver = User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if receiver == request.user:
        return Response({"error": "You cannot add yourself"}, status=400)

    FriendRequest.objects.get_or_create(
        sender=request.user,
        receiver=receiver
    )

    return Response({"message": "Friend request sent"})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_friend_request(request, request_id):
    try:
        fr = FriendRequest.objects.get(
            id=request_id,
            receiver=request.user
        )
    except FriendRequest.DoesNotExist:
        return Response(
            {"error": "Request not found"},
            status=404
        )

    fr.status = "accepted"
    fr.save()

    Friendship.objects.get_or_create(
        user1=fr.sender,
        user2=fr.receiver
    )

    existing = Conversation.objects.filter(
        participants=fr.sender
    ).filter(
        participants=fr.receiver
    ).first()

    if not existing:
        conversation = Conversation.objects.create()
        conversation.participants.add(
            fr.sender,
            fr.receiver
        )

    return Response(
        {"message": "Friend request accepted"}
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_friend_request(request, request_id):
    try:
        fr = FriendRequest.objects.get(id=request_id, receiver=request.user)
    except FriendRequest.DoesNotExist:
        return Response({"error": "Request not found"}, status=404)

    fr.status = "rejected"
    fr.save()

    return Response({"message": "Friend request rejected"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_friends(request):
    friendships = Friendship.objects.filter(
        models.Q(user1=request.user) | models.Q(user2=request.user)
    )

    friends = []

    for f in friendships:
        if f.user1 == request.user:
            friends.append(f.user2.username)
        else:
            friends.append(f.user1.username)

    return Response({"friends": friends})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pending_requests(request):
    requests = FriendRequest.objects.filter(
        receiver=request.user,
        status="pending"
    )

    serializer = FriendRequestSerializer(requests, many=True)
    return Response(serializer.data)