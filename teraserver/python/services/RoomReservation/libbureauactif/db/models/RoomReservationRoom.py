from services.RoomReservation.libbureauactif.db.Base import db, BaseModel


class RoomReservationRoom(db.Model, BaseModel):
    __tablename__ = "t_rooms"
    id_room = db.Column(db.Integer, db.Sequence('id_data_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, nullable=False)
    room_site_uuid = db.Column(db.String(36), nullable=False)
    room_name = db.Column(db.String, nullable=False)

    room_site = db.relationship("TeraSite")
    room_session = db.relationship("TeraSession")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['room_site'])
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add name of site
        if 'site_name' not in ignore_fields and not minimal:
            rval['site_name'] = self.room_site.site_name

        return rval

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
