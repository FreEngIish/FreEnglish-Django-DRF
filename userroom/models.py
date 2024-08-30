import uuid

from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    ROOM_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Closed', 'Closed'),
    ]

    LANGUAGE_LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Native', 'Native'),
    ]

    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    native_language = models.CharField(max_length=10)
    language_level = models.CharField(max_length=12, choices=LANGUAGE_LEVEL_CHOICES, default='Beginner')
    participant_limit = models.IntegerField(default=10)
    current_participants = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=ROOM_STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.room_name


class RoomMembers(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('room', 'user')
