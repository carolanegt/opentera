from services.RoomReservation.libbureauactif.db.models.RoomReservationRoom import RoomReservationRoom
import datetime
import calendar


class DBManagerRoomReservationAccess:

    def query_room_by_id(self, room_id: int):
        room = RoomReservationRoom.get_room_by_id(room_id)
        return room
