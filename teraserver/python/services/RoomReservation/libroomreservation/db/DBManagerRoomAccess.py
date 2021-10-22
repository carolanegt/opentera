from services.RoomReservation.libroomreservation.db.models.RoomReservationRoom import RoomReservationRoom
import datetime
import calendar


class DBManagerRoomAccess:

    def query_room_by_id(self, room_id: int):
        room = RoomReservationRoom.get_room_by_id(room_id)
        return room

    def query_rooms_for_site(self, site_id: int):
        rooms = RoomReservationRoom.query.filter_by(id_site=site_id).all()

        if rooms:
            return rooms
        return []

    def query_rooms(self, sites):
        site_ids = [site['id_site'] for site in sites]
        rooms = RoomReservationRoom.query.filter(RoomReservationRoom.id_site.in_(site_ids)).all()

        if rooms:
            return rooms
        return []
