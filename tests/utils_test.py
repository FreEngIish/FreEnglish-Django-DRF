from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
from channels.testing import WebsocketCommunicator
from django.conf import settings

from userroom.consumers.room_comsumer import RoomConsumer
from userroom.services.user_service import UserService


def create_test_google_token(user_id, email):
    """
    Create a mock Google OAuth token for testing purposes.
    This token contains essential fields expected by your application.
    """
    payload = {
        'sub': user_id,  # Google user ID
        'email': email,  # User's email
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
    }

    # Here, we are simulating a token generation. In reality, you might want to
    # integrate with a service or generate a JWT as per your needs.
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


async def setup_communicator(user, token):
    """
    Set up a WebSocket communicator for testing purposes with mocked user token.
    This function will mock the user retrieval from the token.
    """
    with patch.object(UserService, 'get_user_from_token', return_value=user):
        communicator = WebsocketCommunicator(RoomConsumer.as_asgi(), f'/ws/rooms/?token={token}')
        connected, _ = await communicator.connect()
        assert connected
        return communicator
