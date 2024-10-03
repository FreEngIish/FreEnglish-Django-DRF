from asgiref.sync import async_to_sync
from celery import shared_task
import logging
from userroom.services.room_service import RoomService

logger = logging.getLogger('freenglish')


@shared_task
def deactivate_room_if_empty(room_id):
    room_service = RoomService()

    logger.info(f"A task to deactivate the room has been started {room_id}")

    room = async_to_sync(room_service.get_room)(room_id)

    if room:
        participant_count = async_to_sync(room_service.count_participants)(room)
        if participant_count == 0:
            async_to_sync(room_service.update_room_status)(room, 'Inactive')
            logger.info(f"Room {room.room_name} deactivated.")
        else:
            logger.info(f"Room {room.room_name} is still active. Participants have returned.")
    else:
        logger.warning(f"Room with ID {room_id} not found.")
