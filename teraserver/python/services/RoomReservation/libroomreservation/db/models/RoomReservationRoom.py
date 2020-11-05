from services.RoomReservation.libroomreservation.db.Base import db, BaseModel


class RoomReservationRoom(db.Model, BaseModel):
    __tablename__ = "t_rooms"
    id_room = db.Column(db.Integer, db.Sequence('id_room_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, nullable=False)
    room_name = db.Column(db.String, nullable=False)

    room_reservations = db.relationship('RoomReservationReservation')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        if minimal:
            ignore_fields += ['room_reservations']

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_room_by_id(room_id: int):
        return RoomReservationRoom.query.filter_by(id_room=room_id).first()

    @staticmethod
    def create_defaults():
        base_room = RoomReservationRoom()
        base_room.room_name = 'A-021'
        base_room.id_site = 1
        RoomReservationRoom.insert(base_room)

        base_room2 = RoomReservationRoom()
        base_room2.room_name = 'C-302'
        base_room2.id_site = 1
        RoomReservationRoom.insert(base_room2)

        secret_room = RoomReservationRoom()
        secret_room.room_name = "B-1154"
        secret_room.id_site = 2
        RoomReservationRoom.insert(secret_room)
