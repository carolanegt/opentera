from services.RoomReservation.FlaskModule import FlaskModule, flask_app
from services.RoomReservation.ConfigManager import ConfigManager
from opentera.redis import RedisVars
from opentera.redis.RedisClient import RedisClient
import services.RoomReservation.Globals as Globals
from sqlalchemy.exc import OperationalError
from opentera.services.ServiceOpenTera import ServiceOpenTera
from twisted.internet import defer, reactor
from opentera.modules.BaseModule import ModuleNames, create_module_event_topic_from_name
import opentera.messages.python as messages
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

from opentera.services.ServiceAccessManager import ServiceAccessManager

from twisted.python import log
import sys

import os


class ServiceRoomReservation(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

        # Create REST backend
        self.flaskModule = FlaskModule(Globals.config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

    def notify_service_messages(self, pattern, channel, message):
        pass

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        pass

    @defer.inlineCallbacks
    def register_to_events(self):
        # Need to register to events produced by UserManagerModule
        ret1 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
            ModuleNames.DATABASE_MODULE_NAME, 'session'), self.database_event_received)

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

        if event.type == messages.DatabaseEvent.DB_DELETE:
            print("Delete Session Event")
            # TODO delete reservation linked to the deleted session, event_name = 'session'
            # Resend invitation to newly connected user
            pass


if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('RoomReservationService.json'):
        print('Invalid config')
        exit(1)

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': Globals.config_man.db_config['username'],
        'pw': Globals.config_man.db_config['password'],
        'db': Globals.config_man.db_config['name'],
        'host': Globals.config_man.db_config['url'],
        'port': Globals.config_man.db_config['port']
    }

    try:
        Globals.db_man.open(POSTGRES, True)
    except OperationalError:
        print("Unable to connect to database - please check settings in config file!")
        quit()

    with flask_app.app_context():
        Globals.db_man.create_defaults(Globals.config_man)

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_device_static_token_key = Globals.redis_client.redisGet(RedisVars.RedisVars.RedisVar_DeviceStaticTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVars.RedisVar_ParticipantTokenAPIKey)
    Globals.api_participant_static_token_key = \
        Globals.redis_client.redisGet(RedisVars.RedisVars.RedisVar_ParticipantStaticTokenAPIKey)

    # Update Service Access information
    ServiceAccessManager.api_user_token_key = Globals.api_user_token_key
    ServiceAccessManager.api_participant_token_key = Globals.api_participant_token_key
    ServiceAccessManager.api_participant_static_token_key = Globals.api_participant_static_token_key
    ServiceAccessManager.api_device_token_key = Globals.api_device_token_key
    ServiceAccessManager.api_device_static_token_key = Globals.api_device_static_token_key
    ServiceAccessManager.config_man = Globals.config_man

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVars.RedisVar_ServicePrefixKey +
                                                 Globals.config_man.service_config['name'])

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

    # Update service uuid
    Globals.config_man.service_config['ServiceUUID'] = service_info['service_uuid']

    # Update port, hostname, endpoint
    Globals.config_man.service_config['port'] = service_info['service_port']
    Globals.config_man.service_config['hostname'] = service_info['service_hostname']

    # Create the Service
    Globals.service = ServiceRoomReservation(Globals.config_man, service_info)

    # Start App / reactor events
    reactor.run()

    print('RoomReservationService - done!')
