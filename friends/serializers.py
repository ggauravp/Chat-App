from rest_framework import serializers
from .models import FriendRequest, Friendship
from accounts.models import User


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FriendRequest
        fields = "__all__"
        read_only_fields = ["sender", "status", "created_at"]