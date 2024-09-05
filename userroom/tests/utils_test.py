from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from channels.testing import WebsocketCommunicator
from jose import jwt

from freenglish import settings
from userroom.consumers.room_comsumer import RoomConsumer


def create_test_oauth_token(user_id, **kwargs):
    payload = {
        'sub': user_id,
        'email': kwargs.get('email'),
        'nickname': kwargs.get('nickname', ''),
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'aud': settings.SOCIAL_AUTH_AUTH0_KEY,
        'iss': f'https://{settings.AUTH0_DOMAIN}/',
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


async def setup_communicator(user, token):
    with patch.object(RoomConsumer, 'get_user_from_token', return_value=user):
        communicator = WebsocketCommunicator(RoomConsumer.as_asgi(), f'/ws/rooms/?token={token}')
        connected, _ = await communicator.connect()
        assert connected
        return communicator
