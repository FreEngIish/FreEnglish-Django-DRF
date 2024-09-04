import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from userroom.consumers.room_commands import RoomCommands


logger = logging.getLogger('freenglish')

class RoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.commands = RoomCommands(self)

    async def connect(self):
        if self.scope['user'].is_authenticated:
            await self.accept()
        else:
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
                    await self.commands.handle_create_room(data)

                else:
                    await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unknown message type'}))

            except json.JSONDecodeError:
                logger.error('Invalid JSON received: %s', text_data)
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
            except Exception as e:
                logger.error('Error processing message: %s', str(e))
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'An unexpected error occurred'}))
