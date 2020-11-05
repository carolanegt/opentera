from services.RoomReservation.libroomreservation.db.Base import db, BaseModel


class RoomReservationRoomSession(db.Model, BaseModel):
    __tablename__ = "t_room_sessions"
    id_room_session = db.Column(db.Integer, db.Sequence('id_room_session_sequence'), primary_key=True,
                                autoincrement=True)
    id_room = db.Column(db.Integer, db.ForeignKey('t_rooms'), nullable=False)
    session_uuid = db.Column(db.String(36), nullable=False, unique=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_room_sessions_by_room(room_id: int):
        return RoomReservationRoomSession.query.filter_by(id_room=room_id).all()

    @staticmethod
    def create_defaults():
        base_room_session = RoomReservationRoomSession()
        base_room_session.session_uuid = 'e5a7e3ef-d08c-48e8-9d1b-900ca96292ab'
        base_room_session.id_room = 1
        RoomReservationRoomSession.insert(base_room_session)