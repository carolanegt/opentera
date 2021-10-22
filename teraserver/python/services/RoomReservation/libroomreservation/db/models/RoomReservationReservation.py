import datetime
from datetime import timedelta
from sqlalchemy import ARRAY
from services.RoomReservation.libroomreservation.db.Base import db, BaseModel


class RoomReservationReservation(db.Model, BaseModel):
    __tablename__ = "t_reservations"
    id_reservation = db.Column(db.Integer, db.Sequence('id_reservation_sequence'), primary_key=True, autoincrement=True)
    id_room = db.Column(db.Integer, db.ForeignKey('t_rooms'), nullable=True)
    name = db.Column(db.String, nullable=False)
    session_uuid = db.Column(db.String(36), nullable=True, unique=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    reservation_start_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    reservation_end_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    session_participant_uuids = db.Column(ARRAY(db.String), default=[])

    room = db.relationship('RoomReservationRoom')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = ['room']

        json = super().to_json(ignore_fields=ignore_fields)
        json['room'] = self.room.to_json(minimal=True)
        return json

    @staticmethod
    def get_reservation_by_id(reservation_id: int):
        return RoomReservationReservation.query.filter_by(id_reservation=reservation_id).first()

    @staticmethod
    def create_defaults():
        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.name = 'Réunion'
        base_reservation.user_uuid = '14783a2d-8fe0-4988-9254-e09d21312459'
        base_reservation.reservation_end_datetime = datetime.datetime.now() + timedelta(hours=1)
        base_reservation.reservation_start_datetime = datetime.datetime.now()
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 2
        base_reservation.name = 'Séance télé avec monsieur Dupont'
        base_reservation.user_uuid = '7b41b394-78a3-489e-bd7e-7b4d47e31175'
        base_reservation.reservation_end_datetime = datetime.datetime.now() + timedelta(hours=1)
        base_reservation.reservation_start_datetime = datetime.datetime.now()
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.name = 'Séance de formation télé'
        base_reservation.user_uuid = '14783a2d-8fe0-4988-9254-e09d21312459'
        base_reservation.reservation_end_datetime = datetime.datetime.now() + timedelta(days=1, hours=1.5)
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=1)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.name = 'Séance de téléréadaptation avec Micheline Tremblay'
        base_reservation.user_uuid = '14783a2d-8fe0-4988-9254-e09d21312459'
        base_reservation.reservation_end_datetime = datetime.datetime.now() + timedelta(days=1, hours=3)
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=1, hours=2)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.name = 'Séance de téléréadaptation avec Micheline Tremblay'
        base_reservation.user_uuid = '14783a2d-8fe0-4988-9254-e09d21312459'
        base_reservation.reservation_end_datetime = datetime.datetime.now() + timedelta(days=6, hours=2)
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=6)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.name = 'Séance de téléréadaptation avec Micheline Tremblay'
        base_reservation.user_uuid = '14783a2d-8fe0-4988-9254-e09d21312459'
        base_reservation.reservation_end_datetime = datetime.datetime.now() + timedelta(days=2, hours=1.5)
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(days=2)
        RoomReservationReservation.insert(base_reservation)

        base_reservation = RoomReservationReservation()
        base_reservation.id_room = 1
        base_reservation.name = 'Séance de physio avec Tintin'
        base_reservation.user_uuid = '14783a2d-8fe0-4988-9254-e09d21312459'
        base_reservation.reservation_end_datetime = datetime.datetime.now() + timedelta(hours=5)
        base_reservation.reservation_start_datetime = datetime.datetime.now() + timedelta(hours=2)
        RoomReservationReservation.insert(base_reservation)
