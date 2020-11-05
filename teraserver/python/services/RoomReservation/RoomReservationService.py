from services.RoomReservation.FlaskModule import FlaskModule, flask_app
from services.RoomReservation.TwistedModule import TwistedModule
from services.RoomReservation.ConfigManager import ConfigManager
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
import services.RoomReservation.Globals as Globals
from sqlalchemy.exc import OperationalError
from services.shared.ServiceOpenTera import ServiceOpenTera
from twisted.internet import defer
from modules.BaseModule import ModuleNames, create_module_event_topic_from_name
import messages.python as messages
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

import os


class ServiceRoomReservation(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

        # Active sessions
        self.sessions = dict()

    def notify_service_messages(self, pattern, channel, message):
        pass

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        pass

    @defer.inlineCallbacks
    def register_to_events(self):
        # Need to register to events produced by UserManagerModule
        ret1 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
            ModuleNames.DATABASE_MODULE_NAME, 'TeraSession'), self.database_event_received)

        print(ret1)

    def database_event_received(self, pattern, channel, message):
        print('RoomReservationService - database_event_received', pattern, channel, message)
        try:
            tera_event = messages.TeraEvent()
            if isinstance(message, str):
                ret = tera_event.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_event.ParseFromString(message)

            database_event = messages.DatabaseEvent()

            # Look for DatabaseEvent
            for any_msg in tera_event.events:
                if any_msg.Unpack(database_event):
                    self.handle_database_event(database_event)

        except DecodeError as d:
            print('RoomReservationService - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('RoomReservationService - Failure in redisMessageReceived', e)

    def handle_database_event(self, event: messages.DatabaseEvent):
        print('RoomReservationService.handle_database_event', event)
        # Verify each session
        for id_session in self.sessions:
            session_info = self.sessions[id_session]

            # Verify if it contains the user_uuid
            if event.user_uuid in session_info['session_users']:
                # Verify the event type
                print(event)
                if event.type == messages.DatabaseEvent.DB_DELETE:
                    # TODO delete reservation linked to the deleted session, event_name = 'session'
                    # Resend invitation to newly connected user
                    print('Resending invitation to ', event, session_info)

                    self.send_join_message(session_info=session_info, target_devices=[], target_participants=[],
                                           target_users=[event.user_uuid])


if __name__ == '__main__':

    # Load configuration
    from services.RoomReservation.Globals import config_man
    config_man.load_config('RoomReservationService.json')

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': config_man.db_config['username'],
        'pw': config_man.db_config['password'],
        'db': config_man.db_config['name'],
        'host': config_man.db_config['url'],
        'port': config_man.db_config['port']
    }

    try:
        Globals.db_man.open(POSTGRES, True)
    except OperationalError:
        print("Unable to connect to database - please check settings in config file!")
        quit()

    with flask_app.app_context():
        Globals.db_man.create_defaults(config_man)

    # Global redis client
    Globals.redis_client = RedisClient(config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey + config_man.service_config['name'])
    import sys
    if service_info is None:
        sys.stderr.write('Error: Unable to get service info from OpenTera Server - is the server running and config '
                         'correctly set in this service?')
        exit(1)
    import json
    service_info = json.loads(service_info)
    if 'service_uuid' not in service_info:
        sys.stderr.write('OpenTera Server didn\'t return a valid service UUID - aborting.')
        exit(1)

    config_man.service_config['ServiceUUID'] = service_info['service_uuid']

    # Creates communication interface with OpenTera
    Globals.service_opentera = ServiceRoomReservation(config_man, service_info)

    # TODO: Set port from service config from server?

    # Main Flask module
    flask_module = FlaskModule(config_man)

    # Main Twisted module
    twisted_module = TwistedModule(config_man)

    # Run reactor
    twisted_module.run()

    print('RoomReservationService - done!')
