import json

from flask import jsonify, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext
from datetime import datetime, timedelta

from services.RoomReservation import Globals
from opentera.services.ServiceAccessManager import ServiceAccessManager
from services.RoomReservation.FlaskModule import default_api_ns as api
from services.RoomReservation.libroomreservation.db.models.RoomReservationReservation import RoomReservationReservation
from services.RoomReservation.libroomreservation.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_reservation', type=int, help='ID of the reservation to query')
get_parser.add_argument('id_room', type=int, help='ID of the room from which to get all reservations')
get_parser.add_argument('start_date', type=str, help='Date of first day to query')
get_parser.add_argument('end_date', type=str, help='Date of last day to query')
get_parser.add_argument('overlaps', type=inputs.boolean, help='Return only overlapping reservations')
get_parser.add_argument('full', type=inputs.boolean, help='Get additional information for reservation')

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
    @ServiceAccessManager.token_required()
    def get(self):
        parser = get_parser

        reservation_access = DBManager.reservationAccess()
        args = parser.parse_args()

        reservations = []
        if args['overlaps']:
            if not args['id_room'] or not args['start_date'] or not args['end_date']:
                return 'Missing date arguments', 400
            else:
                # Find reservation overlaps
                start_time = datetime.fromisoformat(args['start_date'])
                end_time = datetime.fromisoformat(args['end_date'])
                reservations = reservation_access.query_overlaps(args['id_room'], start_time, end_time)
        else:
            if args['id_reservation']:
                reservations = [reservation_access.query_reservation_by_id(reservation_id=args['id_reservation'])]
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

                if not args['overlaps']:
                    # Get the name of the user who booked the event
                    endpoint = '/api/service/users'
                    params = {'user_uuid': reservation.user_uuid}
                    response = Globals.service.get_from_opentera(endpoint, params)
                    if response.status_code == 200 and response is not None:
                        user = response.json()
                        reservation_json['user_fullname'] = user['user_firstname'] + ' ' + user['user_lastname']

                # If reservation has a session associated to it, get it from OpenTera
                if reservation.session_uuid and args['full'] is True:
                    endpoint = '/api/service/sessions'
                    params = {'uuid_session': reservation.session_uuid, 'with_session_type': True}
                    response = Globals.service.get_from_opentera(endpoint, params)

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
    @ServiceAccessManager.token_required()
    def post(self):
        reservation_access = DBManager.reservationAccess()
        # Using request.json instead of parser, since parser messes up the json!
        reservation_json = request.json['reservation']

        # Validate if we have an id
        if 'id_reservation' not in reservation_json or 'id_room' not in reservation_json:
            return gettext('Missing id_reservation or id_room arguments'), 400

        # Check if there is already a reservation for that room between the times of the reservation
        start_time = datetime.fromisoformat(reservation_json['reservation_start_datetime'])
        end_time = datetime.fromisoformat(reservation_json['reservation_end_datetime'])
        overlapping_reservations = reservation_access.query_overlaps(reservation_json['id_room'], start_time, end_time,
                                                                     reservation_json['id_reservation'])
        if overlapping_reservations:
            return gettext('A reservation already uses this time slot'), 400

        # Create the session associated with the reservation
        if 'session' in reservation_json:
            session = reservation_json['session']
            endpoint = '/api/service/sessions'
            params = {'session': session}
            response = Globals.service.post_to_opentera(endpoint, params)

            if response.status_code == 200:
                session_info = response.json()
                reservation_json['session_uuid'] = session_info[0]['session_uuid']
                reservation_json['session'] = session_info
            else:
                return 'Unauthorized', 403

        # Remove room from object
        del reservation_json['room']

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
    @ServiceAccessManager.token_required()
    def delete(self):
        parser = delete_parser
        # current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        reservation_access = DBManager.reservationAccess()

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # TODO Only site admins can delete a reservation
        reservation = RoomReservationReservation.get_reservation_by_id(id_todel)

        # If we are here, we are allowed to delete.
        try:
            RoomReservationReservation.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         QueryReservations.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
