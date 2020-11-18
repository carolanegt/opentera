import json

from flask import jsonify, request
from flask_restx import Resource, reqparse
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

from services.RoomReservation.Globals import service_opentera
from services.RoomReservation.AccessManager import AccessManager
from services.RoomReservation.FlaskModule import default_api_ns as api
from services.RoomReservation.libroomreservation.db.models.RoomReservationReservation import RoomReservationReservation
from services.RoomReservation.libroomreservation.db.models.RoomReservationRoom import RoomReservationRoom
from services.RoomReservation.libroomreservation.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_reservation', type=int, help='ID of the reservation to query')
get_parser.add_argument('id_room', type=int, help='ID of the room from which to get all reservations')
get_parser.add_argument('start_date', type=str, help='Date of first day to query')
get_parser.add_argument('end_date', type=str, help='Date of last day to query')

post_parser = api.parser()
delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Reservation ID to delete', required=True)


class QueryReservations(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.expect(get_parser)
    @api.doc(description='Get reservations information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of reservations',
                        500: 'Database error'})
    @AccessManager.token_required
    def get(self):
        parser = get_parser

        reservation_access = DBManager.reservationAccess()
        args = parser.parse_args()

        reservations = []
        if args['id_reservation']:
            reservations = reservation_access.query_reservation_by_id(reservation_id=args['id_reservation'])
        if args['id_room']:
            if not args['start_date'] or not args['end_date']:
                return 'Missing date arguments', 400
            else:
                reservations = reservation_access.query_reservation_by_room(room_id=args['id_room'],
                                                                            start_date=args['start_date'],
                                                                            end_date=args['end_date'])

        try:
            reservations_list = []

            for reservation in reservations:
                reservation_json = reservation.to_json()

                # If reservation has a session associated to it, get it from OpenTera
                if reservation.session_uuid and args['id_reservation']:
                    endpoint = '/api/service/sessions'
                    params = {'uuid_session': reservation.session_uuid}
                    response = service_opentera.get_from_opentera(endpoint, params)

                    if response.status_code == 200:
                        session_info = response.json()
                        reservation_json['session'] = session_info
                    else:
                        return 'Unauthorized', 403

                reservations_list.append(reservation_json)

            return jsonify(reservations_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         QueryReservations.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.expect(post_parser)
    @api.doc(description='Create / update reservations. id_reservation must be set to "0" to create a new '
                         'reservation. A reservation can be created/modified if the user has admin rights to the '
                         'related site.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified reservation',
                        400: 'Badly formed JSON or missing fields(id_site) in the JSON body',
                        500: 'Internal error occurred when saving reservation'})
    @AccessManager.token_required
    def post(self):
        reservation_access = DBManager.reservationAccess()
        # Using request.json instead of parser, since parser messes up the json!
        reservation_json = request.json['reservation']

        # Validate if we have an id
        if 'id_reservation' not in reservation_json or 'id_room' not in reservation_json:
            return gettext('Missing id_reservation or id_room arguments'), 400

        # Do the update!
        if reservation_json['id_reservation'] > 0:
            # Already existing
            try:
                RoomReservationReservation.update(reservation_json['id_reservation'], reservation_json)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             QueryReservations.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_reservation = RoomReservationReservation()
                new_reservation.from_json(reservation_json)
                RoomReservationReservation.insert(new_reservation)
                # Update ID for further use
                reservation_json['id_reservation'] = new_reservation.id_reservation
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             QueryReservations.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_reservation = RoomReservationReservation.get_reservation_by_id(reservation_json['id_reservation'])

        return jsonify([update_reservation.to_json()])

    @api.expect(delete_parser)
    @api.doc(description='Delete a specific reservation',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete reservation (only site admin can delete)',
                        500: 'Database error.'})
    @AccessManager.token_required
    def delete(self):
        parser = delete_parser
        # current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        reservation_access = DBManager.reservationAccess()

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # TODO Only site admins can delete a reservation
        reservation = RoomReservationRoom.get_reservation_by_id(id_todel)

        if reservation_access.get_site_role(reservation.reservation_site.id_site) != 'admin':
            return gettext('Forbidden'), 403

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
