from services.RoomReservation.libbureauactif.db.Base import db, BaseModel


class RoomReservationRoom(db.Model, BaseModel):
    __tablename__ = "t_rooms"
    id_room = db.Column(db.Integer, db.Sequence('id_data_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, nullable=False)
    room_site_uuid = db.Column(db.String(36), nullable=False)
    room_name = db.Column(db.String, nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend([])
        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        pass

    @staticmethod
    def get_room_by_id(room_id: int):
        return RoomReservationRoom.query.filter_by(id_room=room_id).first()
