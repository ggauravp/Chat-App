from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_requests"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_requests"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("sender", "receiver")

class Friendship(models.Model):
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendships1"
    )

    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendships2"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")