import json
import logging

from channels.db import database_sync_to_async
from django.core.cache import cache

from userroom.services.room_service import RoomService


logger = logging.getLogger('freenglish')

class RoomCommands:
    def __init__(self, consumer):
        self.consumer = consumer
        self.room_service = RoomService()

    async def handle_join_room(self, room_id, user):
        try:
            cache_key = f'user_room_{user.id}'
            cached_room_id = cache.get(cache_key)

            if cached_room_id:
                if cached_room_id != room_id:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'error',
                        'message': f'You are already in another room with ID {cached_room_id}. You can only join one room at a time.'  # noqa: E501
                    }))
                    return
                else:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'info',
                        'message': f'You are already in the room "{room_id}".'
                    }))
                    return

            user_room = None

            if not cached_room_id:
                user_room = await self.room_service.get_user_room(user)

            if user_room:
                cache.set(cache_key, user_room.room_id, timeout=3600)
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'You are already in another room with ID {user_room.room_id}. You can only join one room at a time.'  # noqa: E501
                }))
                return

            room = await self.room_service.get_room(room_id)
            if room:
                current_count = await self.room_service.count_participants(room)
                if current_count < room.participant_limit:
                    added = await self.room_service.add_participant(room, user)
                    if added:
                        self.consumer.room_id = room_id
                        cache.set(cache_key, room_id, timeout=3600)
                        await self.consumer.send(text_data=json.dumps({
                            'type': 'success',
                            'message': f'You have successfully joined the room "{room.room_name}".'
                        }))
                        logger.info(f'Participant {user.email} added to RoomMembers for room {room.room_name}')
                    else:
                        await self.consumer.send(text_data=json.dumps({
                            'type': 'info',
                            'message': f'You are already a participant in the room "{room.room_name}".'
                        }))
                        logger.warning(f'Participant {user.email} already in RoomMembers for room {room.room_name}')
                else:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Room is full.'
                    }))
            else:
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Room does not exist.'
                }))
        except Exception as e:
            logger.error(f'An error occurred while joining the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not join room.'
            }))

    async def handle_leave_room(self, room_id, user):
        try:
            room = await self.room_service.get_room(room_id)
            if room:
                removed = await self.room_service.remove_participant(room, user)
                if removed:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'success',
                        'message': f'You have left the room "{room.room_name}".'
                    }))
                    logger.info(f'Participant {user.email} removed from RoomMembers for room {room.room_name}')

                    cache_key = f'user_room_{user.id}'
                    cache.delete(cache_key)
                else:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'info',
                        'message': f'You were not a participant in the room "{room.room_name}".'
                    }))
                    logger.warning(f'Participant {user.email} not found in RoomMembers for room {room.room_name}')
            else:
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Room does not exist.'
                }))
        except Exception as e:
            logger.error(f'An error occurred while leaving the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not leave room.'
            }))

    async def handle_edit_room(self, room_id, user, data):
        try:
            room = await self.room_service.get_room(room_id)
            if room:
                creator = await database_sync_to_async(lambda: room.creator)()
                if creator.id == user.id:
                    room_name = data.get('room_name')
                    native_language = data.get('native_language')
                    language_level = data.get('language_level')
                    participant_limit = data.get('participant_limit')

                    await self.room_service.update_room(
                        room,
                        room_name=room_name,
                        native_language=native_language,
                        language_level=language_level,
                        participant_limit=participant_limit
                    )

                    await self.consumer.send(text_data=json.dumps({
                        'type': 'success',
                        'message': 'Room updated successfully.'
                    }))
                    logger.info(f'Room {room.room_name} updated by {user.email}')
                else:
                    await self.consumer.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'You do not have permission to edit this room.'
                    }))
            else:
                await self.consumer.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Room does not exist.'
                }))
        except Exception as e:
            logger.error(f'An error occurred while editing the room: {e}', exc_info=True)
            await self.consumer.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Could not edit room.'
            }))
