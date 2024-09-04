import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

from userroom.consumers.room_comsumer import RoomConsumer
from userroom.models import UserRoom


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_create_room():
    from accounts.models import User
    user = await database_sync_to_async(User.objects.create_user)(
        email='testuser@example.com',
        password='password123',
        username='testuser',
    )
    communicator = WebsocketCommunicator(RoomConsumer.as_asgi(), '/ws/room/')
    communicator.scope['user'] = user
    connected, _ = await communicator.connect()
    assert connected
    await communicator.send_json_to({
        'type': 'createRoom',
        'data': {
            'room_name': 'Test Room',
            'native_language': 'English',
            'language_level': 'Intermediate',
            'participant_limit': 10
        }
    })
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
