import logging

from channels.db import database_sync_to_async
from django.db.models import Count


logger = logging.getLogger('freenglish')


class RoomService:
    @database_sync_to_async
    def create_room(self, room_name, native_language, language_level, participant_limit, creator, description=''):
        from userroom.models import UserRoom

        room = UserRoom(
            room_name=room_name,
            native_language=native_language,
            language_level=language_level,
            participant_limit=participant_limit,
            creator=creator,
            description=description,
        )
        room.save()
        return room

    @database_sync_to_async
    def update_room(self, room, room_name=None, native_language=None, language_level=None, participant_limit=None, description=None):  # noqa: E501
        if room_name is not None:
            room.room_name = room_name
        if native_language is not None:
            room.native_language = native_language
        if language_level is not None:
            room.language_level = language_level
        if participant_limit is not None:
            room.participant_limit = participant_limit
        if description is not None:
            room.description = description
        room.save()
        return room

    @database_sync_to_async
    def update_room_status(self, room, status):
        room.status = status
        room.save()

    @database_sync_to_async
    def get_room(self, room_id):
        from userroom.models import UserRoom
        return UserRoom.objects.filter(room_id=room_id).first()

    @database_sync_to_async
    def add_participant(self, room, user):
        from userroom.models import RoomMembers
        if not room.current_participants.filter(id=user.id).exists():
            room.current_participants.add(user)
            RoomMembers.objects.create(room=room, user=user)
            return True
        return False

    @database_sync_to_async
    def remove_participant(self, room, user):
        from userroom.models import RoomMembers

        if room.current_participants.filter(id=user.id).exists():
            room.current_participants.remove(user)

            RoomMembers.objects.filter(room=room, user=user).delete()
            return True
        return False

    @database_sync_to_async
    def count_participants(self, room):
        return room.current_participants.count()

    async def serialize_room_data(self, room):
        from userroom.serializers import UserRoomSerializer
        return await database_sync_to_async(lambda: UserRoomSerializer(room).data)()

    @database_sync_to_async
    def serialize_rooms_data(self, rooms):
        from userroom.serializers import UserRoomSerializer

        return [UserRoomSerializer(room).data for room in rooms]

    @database_sync_to_async
    def get_user_room(self, user):
        from userroom.models import RoomMembers
        room_member = RoomMembers.objects.filter(user=user).first()
        return room_member.room if room_member else None

    @database_sync_to_async
    def get_all_rooms(self, language_level=None, min_participants=None, max_participants=None):
        from userroom.models import UserRoom

        rooms_query = UserRoom.objects.filter(status='Active')

        if language_level:
            rooms_query = rooms_query.filter(language_level=language_level)

        if min_participants is not None:
            rooms_query = rooms_query.annotate(participant_count=Count('current_participants')).filter(participant_count__gte=min_participants)  # noqa: E501

        if max_participants is not None:
            rooms_query = rooms_query.annotate(participant_count=Count('current_participants')).filter(participant_count__lte=max_participants)  # noqa: E501

        return rooms_query.order_by('-creation_date')

    @database_sync_to_async
    def count_user_rooms(self, user):
        from userroom.models import UserRoom
        return UserRoom.objects.filter(creator=user, status='Active').count()

    @database_sync_to_async
    def get_room_participants(self, room):
        return list(room.current_participants.all())
    @database_sync_to_async
    def search_rooms_by_name(self, search_query):
        from userroom.models import UserRoom
        return UserRoom.objects.filter(room_name__icontains=search_query, status='Active').order_by('-creation_date')
