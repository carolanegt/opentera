from flask import jsonify, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client
from services.RoomReservation import Globals
from services.RoomReservation.FlaskModule import default_api_ns as api
from services.RoomReservation.libroomreservation.db.models.RoomReservationRoom import RoomReservationRoom
from services.RoomReservation.libroomreservation.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_room', type=int, help='ID of the room to query')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all rooms')
get_parser.add_argument('reservations', type=inputs.boolean, help='Flag that expands the returned data to include '
                                                                  'reservations')

post_schema = api.schema_model('room', {'properties': RoomReservationRoom.get_json_schema(),
                                        'type': 'object',
                                        'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Room ID to delete', required=True)


class QueryRooms(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.expect(get_parser)
    @api.doc(description='Get rooms information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of rooms',
                        500: 'Database error'})
    @ServiceAccessManager.token_required()
    def get(self):
        parser = get_parser

        room_access = DBManager.roomAccess()
        args = parser.parse_args()

        rooms = []
        if args['id_room']:
            rooms = [RoomReservationRoom.get_room_by_id(args['id_room'])]
        elif args['id_site']:
            # If we have a site id, query for rooms of that site
            rooms = room_access.query_rooms_for_site(site_id=args['id_site'])
        else:
            # Get all accessible sites for user
            user = current_user_client.get_user_info()
            sites = user[0]['sites']
            if sites:
                # Get all rooms
                rooms = room_access.query_rooms(sites)

        try:
            rooms_list = []

            for room in rooms:
                room_json = room.to_json(minimal=True)

                # If room has a site associated to it, get it from OpenTera
                if room.id_site:
                    endpoint = '/api/service/sites'
                    params = {'id_site': room.id_site}
                    response = Globals.service.get_from_opentera(endpoint, params)

                    if response.status_code == 200:
                        site_info = response.json()
                        room_json['site'] = site_info

                rooms_list.append(room_json)

            return jsonify(rooms_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         QueryRooms.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.expect(post_schema)
    @api.doc(description='Create / update rooms. id_room must be set to "0" to create a new '
                         'room. A room can be created/modified if the user has admin rights to the '
                         'related site.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified room',
                        400: 'Badly formed JSON or missing fields(id_site) in the JSON body',
                        500: 'Internal error occurred when saving room'})
    @ServiceAccessManager.token_required()
    def post(self):
        room_access = DBManager.roomAccess()
        # Using request.json instead of parser, since parser messes up the json!
        room_json = request.json['room']

        # Validate if we have an id
        if 'id_room' not in room_json or 'id_site' not in room_json:
            return gettext('Missing id_room or id_site arguments'), 400

        if 'room_reservations' in room_json:
            room_reservations = room_json.pop('room_reservations')

        # TODO Only site admins can create or update rooms
        # if room_json['id_room'] == 0 and room_json['id_site'] not in room_access.get_accessible_sites_ids(
        #        admin_only=True):
        #    return gettext('Forbidden'), 403

        # Do the update!
        if room_json['id_room'] > 0:
            # Already existing
            try:
                RoomReservationRoom.update(room_json['id_room'], room_json)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             QueryRooms.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_room = RoomReservationRoom()
                new_room.from_json(room_json)
                RoomReservationRoom.insert(new_room)
                # Update ID for further use
                room_json['id_room'] = new_room.id_room
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             QueryRooms.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_room = RoomReservationRoom.get_room_by_id(room_json['id_room'])

        return jsonify([update_room.to_json()])

    @api.expect(delete_parser)
    @api.doc(description='Delete a specific room',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete room (only site admin can delete)',
                        500: 'Database error.'})
    @ServiceAccessManager.token_required()
    def delete(self):
        parser = delete_parser
        # current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        room_access = DBManager.roomAccess()

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # TODO Only site admins can delete a room
        # if room_access.get_site_role(room.room_site.id_site) != 'admin':
        #   return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            RoomReservationRoom.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         QueryRooms.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
