from rest_framework import serializers
from .models import UserRoom


class UserRoomSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.id')
    room_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = UserRoom
        fields = ['room_id', 'room_name', 'native_language', 'language_level', 'participant_limit',
                  'current_participants', 'status', 'creator']
        read_only_fields = ['room_id', 'current_participants', 'status', 'creator']
