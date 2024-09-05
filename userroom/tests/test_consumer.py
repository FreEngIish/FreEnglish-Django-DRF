import pytest
from channels.db import database_sync_to_async

from userroom.models import UserRoom
from userroom.tests.utils_test import create_test_oauth_token, setup_communicator


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_create_room():
    from accounts.models import User

    user = await database_sync_to_async(User.objects.create_user)(
        email='testuser@example.com', password='password123', username='testuser', auth0_sub='auth0|test_unique_user1'
    )
    token = create_test_oauth_token(
        user_id=user.id,
        email=user.email,
        username=user.username,
        auth0_sub=user.auth0_sub,
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
