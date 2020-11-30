from services.RoomReservation.libroomreservation.db.models.RoomReservationReservation import RoomReservationReservation
import datetime
import dateutil

class DBManagerReservationAccess:

    def query_reservation_by_id(self, reservation_id: int):
        reservation = RoomReservationReservation.get_reservation_by_id(reservation_id)
        return reservation

    def query_reservation_by_room(self, room_id, start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
        end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

        reservations = RoomReservationReservation.query.filter(
            RoomReservationReservation.reservation_start_datetime.between(start_date, end_date),
            RoomReservationReservation.id_room == room_id).all()

        if reservations:
            return reservations
        return []

    def query_by_room_and_time(self, reservation):
        start_time = dateutil.parser.parse(reservation['reservation_start_datetime'])
        end_time = dateutil.parser.parse(reservation['reservation_end_datetime'])

        reservations = RoomReservationReservation.query.filter(
            RoomReservationReservation.reservation_start_datetime.between(start_time, end_time),
            RoomReservationReservation.id_room == reservation['id_room']).all()

        if reservations:
            return reservations
        return None
