from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FriendRequest, Friendship
from accounts.models import User
from .serializers import FriendRequestSerializer

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
        fr = FriendRequest.objects.get(id=request_id, receiver=request.user)
    except FriendRequest.DoesNotExist:
        return Response({"error": "Request not found"}, status=404)

    fr.status = "accepted"
    fr.save()

    Friendship.objects.get_or_create(
        user1=fr.sender,
        user2=fr.receiver
    )

    return Response({"message": "Friend request accepted"})

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