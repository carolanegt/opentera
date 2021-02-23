from sqlalchemy import and_, tuple_, or_, literal
from sqlalchemy.orm import aliased

from services.RoomReservation.libroomreservation.db.models.RoomReservationReservation import RoomReservationReservation
from datetime import datetime


class DBManagerReservationAccess:

    def query_reservation_by_id(self, reservation_id: int):
        reservation = RoomReservationReservation.get_reservation_by_id(reservation_id)
        return reservation

    def query_reservation_by_room(self, room_id, start_date, end_date):
        start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
        end_date = end_date.replace(hour=23, minute=59, second=59)

        reservations = RoomReservationReservation.query.filter(
            RoomReservationReservation.reservation_start_datetime.between(start_date, end_date),
            RoomReservationReservation.id_room == room_id).all()

        if reservations:
            return reservations
        return []

    def query_overlaps(self, id_room, start_time, end_time, id_reservation=0):

        reservations = RoomReservationReservation.query.filter(
            and_(RoomReservationReservation.id_reservation != id_reservation,
                 or_(RoomReservationReservation.reservation_start_datetime.between(start_time, end_time),
                     RoomReservationReservation.reservation_end_datetime.between(start_time, end_time),
                     literal(start_time).between(RoomReservationReservation.reservation_start_datetime,
                                                 RoomReservationReservation.reservation_end_datetime),
                     literal(end_time).between(RoomReservationReservation.reservation_start_datetime,
                                               RoomReservationReservation.reservation_end_datetime))),
            RoomReservationReservation.id_room == id_room).all()

        if reservations:
            return reservations
        return []
