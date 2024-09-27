from rest_framework import serializers
from .models import UserRoom


class UserRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoom
        fields = '__all__'
