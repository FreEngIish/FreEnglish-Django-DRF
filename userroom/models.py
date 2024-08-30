import uuid

from django.contrib.auth.models import User
from django.db import models


# Model for default rooms
class DefaultRoom(models.Model):
    # Choices for room status
    ROOM_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Closed', 'Closed'),
    ]

    # Choices for language proficiency levels
    LANGUAGE_LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Native', 'Native'),
    ]

    # Fields for default rooms
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for the room
    room_name = models.CharField(max_length=100)  # Name of the room
    native_language = models.CharField(max_length=10)  # Primary language used in the room
    language_level = models.CharField(max_length=12, choices=LANGUAGE_LEVEL_CHOICES, default='Beginner')
    participant_limit = models.IntegerField(default=10)  # Maximum number of participants allowed
    current_participants = models.IntegerField(default=0)  # Current number of participants in the room
    creation_date = models.DateTimeField(auto_now_add=True)  # Timestamp of when the room was created
    last_updated_date = models.DateTimeField(auto_now=True)  # Timestamp of the last update to the room
    status = models.CharField(max_length=10, choices=ROOM_STATUS_CHOICES, default='Active')  # Current status ofthe room

    def __str__(self):
        return self.room_name  # String representation of the room

# Model for user-created rooms
class UserRoom(models.Model):
    # Choices for room status
    ROOM_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Closed', 'Closed'),
    ]

    # Choices for language proficiency levels
    LANGUAGE_LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Native', 'Native'),
    ]

    # Fields for user-created rooms
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for the room
    room_name = models.CharField(max_length=100)  # Name of the room
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # User who created the room
    native_language = models.CharField(max_length=10)  # Primary language used in the room
    language_level = models.CharField(max_length=12, choices=LANGUAGE_LEVEL_CHOICES, default='Beginner')
    participant_limit = models.IntegerField(default=10)  # Maximum number of participants allowed
    current_participants = models.IntegerField(default=0)  # Current number of participants in the room
    creation_date = models.DateTimeField(auto_now_add=True)  # Timestamp of when the room was created
    last_updated_date = models.DateTimeField(auto_now=True)  # Timestamp of the last update to the room
    status = models.CharField(max_length=10, choices=ROOM_STATUS_CHOICES, default='Active')  # Current status ofthe room

    def __str__(self):
        return self.room_name  # String representation of the room

# Model for room members (both default and user-created rooms)
class RoomMembers(models.Model):
    room = models.ForeignKey(UserRoom, on_delete=models.CASCADE)  # Room to which the user belongs
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User participating in the room

    class Meta:
        unique_together = ('room', 'user')  # Ensures that each combination of room and user is unique

# Model for messages in rooms
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for message
    room = models.ForeignKey(UserRoom, on_delete=models.CASCADE)  # Room to which the message belongs
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who sent the message
    message_text = models.TextField()  # Content of the message
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of when the message was sent

    def __str__(self):
        return f'Message from {self.user.username} in {self.room.room_name}'  # String representation of the message
