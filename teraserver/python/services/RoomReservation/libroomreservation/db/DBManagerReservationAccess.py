from services.RoomReservation.libroomreservation.db.models.RoomReservationReservation import RoomReservationReservation
import datetime
import calendar


class DBManagerReservationAccess:

    def query_reservation_by_id(self, reservation_id: int):
        room = RoomReservationReservation.get_reservation_by_id(reservation_id)
        return room
