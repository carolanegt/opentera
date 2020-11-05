from services.RoomReservation.libroomreservation.db.models.RoomReservationRoom import RoomReservationRoom
import datetime
import calendar


class DBManagerRoomAccess:

    def query_room_by_id(self, room_id: int):
        room = RoomReservationRoom.get_room_by_id(room_id)
        return room

    def query_rooms_for_site(self, site_id: int):
        rooms = RoomReservationRoom.query.filter_by(id_site=site_id)

        return rooms.all()
