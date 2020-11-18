import datetime
from datetime import timedelta

from services.RoomReservation.libroomreservation.db.Base import db, BaseModel


class RoomReservationReservation(db.Model, BaseModel):
    __tablename__ = "t_reservations"
    id_reservation = db.Column(db.Integer, db.Sequence('id_reservation_sequence'), primary_key=True, autoincrement=True)
    id_room = db.Column(db.Integer, db.ForeignKey('t_rooms'), nullable=True)
    session_uuid = db.Column(db.String(36), nullable=True, unique=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    reservation_start_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    reservation_duration = db.Column(db.Float, nullable=False, default=0)
    user_name = db.Column(db.String, nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_reservation_by_id(reservation_id: int):
        return RoomReservationReservation.query.filter_by(id_reservation=reservation_id).all()

    @staticmethod
    def create_defaults():
        base_reservation = RoomReservationReservation()
        base_reservation.session_uuid = 'e5a7e3ef-d08c-48e8-9d1b-900ca96292ab'
        base_reservation.id_room = 1
        base_reservation.user_name = 'admin'
        base_reservation.user_uuid = '7234fd5c-7486-4206-910e-02aa43282f1e'
        base_reservation.reservation_duration = 1
        base_reservation.reservation_start_datetime = datetime.datetime.now()
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 2
        base_reservation.user_name = 'admin'
        base_reservation.user_uuid = '7234fd5c-7486-4206-910e-02aa43282f1e'
        base_reservation.reservation_duration = 0.5
        base_reservation.reservation_start_datetime = datetime.datetime.now()
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.user_name = 'admin'
        base_reservation.user_uuid = '7234fd5c-7486-4206-910e-02aa43282f1e'
        base_reservation.reservation_duration = 2
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=1)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.user_name = 'admin'
        base_reservation.user_uuid = '7234fd5c-7486-4206-910e-02aa43282f1e'
        base_reservation.reservation_duration = 2
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=1) + timedelta(hours=2)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.user_name = 'admin'
        base_reservation.user_uuid = '7234fd5c-7486-4206-910e-02aa43282f1e'
        base_reservation.reservation_duration = 1.5
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=6)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.user_name = 'admin'
        base_reservation.user_uuid = '7234fd5c-7486-4206-910e-02aa43282f1e'
        base_reservation.reservation_duration = 1.25
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=2)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.user_name = 'admin'
        base_reservation.user_uuid = '7234fd5c-7486-4206-910e-02aa43282f1e'
        base_reservation.reservation_duration = 1
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(hours=2)
        RoomReservationReservation.insert(base_reservation)
