from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):

    sender = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = "__all__"

# StringRelatedField() returns the string representation of a related object
# instead of its ID.
#
# Example:
# If sender is a ForeignKey to User and:
#
#     User.__str__() -> returns username
#
# then:
#
# Without StringRelatedField():
# {
#     "sender": 5
# }
#
# With StringRelatedField():
# {
#     "sender": "gaurav"
# }
#
# Internally it does:
# str(message.sender) -> User.__str__() -> "gaurav"
#
# So the JSON becomes more human-readable.
