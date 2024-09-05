from rest_framework import serializers

from userroom.models import UserRoom


class UserRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoom
        fields = [
            'room_id',
            'room_name',
            'native_language',
            'language_level',
            'participant_limit',
            'current_participants',
            'status',
        ]
