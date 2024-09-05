import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from jose import JWTError

from userroom.consumers.room_commands import RoomCommands
from userroom.services.user_service import UserService


logger = logging.getLogger('freenglish')


class RoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.commands = RoomCommands(self)
        self.user_service = UserService()

    async def connect(self):
        try:
            token = self.scope['query_string'].decode('utf8').split('=')[1]
            self.user = await self.user_service.get_user_from_token(token)
            if self.user:
                await self.accept()
            else:
                await self.close(code=4001)  # Custom close code for unauthorized access
        except (JWTError, IndexError, ValueError) as e:
            logger.error(f'WebSocket connection error: {str(e)}')
            await self.close()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data is not None:
            pass
        if text_data is not None:
            try:
                text_data_json = json.loads(text_data)
                message_type = text_data_json.get('type')
                data = text_data_json.get('data', {})

                if message_type == 'createRoom':
                    await self.commands.handle_create_room(data, user=self.user)

                else:
                    await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unknown message type'}))

            except json.JSONDecodeError:
                logger.error('Invalid JSON received: %s', text_data)
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
            except Exception as e:
                logger.error('Error processing message: %s', str(e))
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'An unexpected error occurred'}))
