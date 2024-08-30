import uuid

from django.conf import settings  # noqa: F401
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User
from django.db import models
from django.utils import timezone


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
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # User who created the room
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # User participating in the room

    class Meta:
        unique_together = ('room', 'user')  # Ensures that each combination of room and user is unique

# Model for messages in rooms
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for message
    room = models.ForeignKey(UserRoom, on_delete=models.CASCADE)  # Room to which the message belongs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # User who sent the message
    message_text = models.TextField()  # Content of the message
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of when the message was sent

    def __str__(self):
        return f'Message from {self.user.username} in {self.room.room_name}'  # String representation of the message


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):  # noqa: F811
    email = models.EmailField(unique=True, blank=False, null=False)
    username = models.CharField(max_length=150, unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Field for save identificator user from Auth0
    auth0_sub = models.CharField(max_length=255, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
