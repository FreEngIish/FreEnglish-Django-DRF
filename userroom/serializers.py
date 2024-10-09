from rest_framework import serializers

from accounts.models import User

from .models import UserRoom


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class UserRoomSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.id')
    room_id = serializers.UUIDField(read_only=True)
    current_participants = UserSerializer(many=True)

    class Meta:
        model = UserRoom
        fields = ['room_id', 'room_name', 'native_language', 'language_level', 'participant_limit',
                  'current_participants', 'status', 'creator', 'description']
        read_only_fields = ['room_id', 'current_participants', 'status', 'creator']
