import json
import pytest
import time
from channels.testing import WebsocketCommunicator
from userroom.consumers.room_comsumer import RoomConsumer
from userroom.models import UserRoom
from userroom.services.room_service import RoomService
from userroom.services.user_service import UserService
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from utils_test import create_test_google_token, setup_communicator


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_create_room():
    User = get_user_model()
    user = await database_sync_to_async(User.objects.create_user)(  # Creating a user
        email='testuser@example.com',
        password='password123',
        username='testuser',
        google_sub='google_unique_user1'  # Adjusted to use Google sub
    )
    
    token = create_test_google_token(  # Generating Google OAuth token
        user_id=user.id,
        email=user.email
    )
    
    communicator = await setup_communicator(user, token)
    await communicator.send_json_to(
        {
            'type': 'createRoom',
            'data': {
                'room_name': 'Test Room',
                'native_language': 'English',
                'language_level': 'Intermediate',
                'participant_limit': 10,
            },
        }
    )
    
    response = await communicator.receive_json_from()
    assert response['type'] == 'roomCreated'
    assert 'room' in response
    room = response['room']
    assert room['room_name'] == 'Test Room'
    assert room['native_language'] == 'English'
    assert room['language_level'] == 'Intermediate'
    assert room['participant_limit'] == 10

    room_exists = await database_sync_to_async(lambda: UserRoom.objects.filter(room_name='Test Room').exists())()
    assert room_exists
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_update_room():
    User = get_user_model()

    user = await database_sync_to_async(User.objects.create_user)(
        email='testuser2@example.com',
        password='password123',
        username='testuser2',
        google_sub='google_unique_user2'
    )

    token = create_test_google_token(
        user_id=user.id,
        email=user.email
    )

    communicator = await setup_communicator(user, token)

    await communicator.send_json_to(
        {
            'type': 'createRoom',
            'data': {
                'room_name': 'Initial Room',
                'native_language': 'English',
                'language_level': 'Beginner',
                'participant_limit': 5,
            },
        }
    )

    response = await communicator.receive_json_from()
    assert response['type'] == 'roomCreated'
    assert 'room' in response
    room = response['room']

    room_id = room['room_id']

    await communicator.send_json_to(
        {
            'type': 'editRoom',
            'data': {
                "room_id": room_id,
                "room_name": "Updated Room",
                "native_language": "English",
                "language_level": "Intermediate",
                "participant_limit": 7
            },
        }
    )

    response = await communicator.receive_json_from()
    assert response['type'] == 'success'
    assert response['message'] == 'Room updated successfully.'

    room_exists = await database_sync_to_async(lambda: UserRoom.objects.filter(room_name='Updated Room').exists())()
    assert room_exists

    await communicator.disconnect()
