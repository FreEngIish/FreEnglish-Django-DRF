import uuid

from django.conf import settings
from django.db import models


class DefaultRoom(models.Model):
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
    native_language = models.CharField(max_length=10)
    language_level = models.CharField(max_length=12, choices=LANGUAGE_LEVEL_CHOICES, default='Beginner')
    participant_limit = models.IntegerField(default=10)
    current_participants = models.ManyToManyField('accounts.User', related_name='user_rooms', blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=ROOM_STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.room_name


class UserRoom(models.Model):
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
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_rooms', on_delete=models.CASCADE)
    native_language = models.CharField(max_length=10)
    language_level = models.CharField(max_length=12, choices=LANGUAGE_LEVEL_CHOICES, default='Beginner')
    participant_limit = models.IntegerField(default=10)
    current_participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='participant_rooms',
                                                  blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=ROOM_STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.room_name


class RoomMembers(models.Model):
    room = models.ForeignKey(UserRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('room', 'user')

    def __str__(self):
        return f'{self.user.email} in {self.room.room_name}'

class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(UserRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.user.username} in {self.room.room_name}'
