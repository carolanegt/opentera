from services.VideoDispatch.ConfigManager import ConfigManager
from messages.python.CreateSession_pb2 import CreateSession
from modules.BaseModule import BaseModule, ModuleNames

import os
import subprocess


class ActiveSession:
    def test(self):
        pass


class WebRTCModule(BaseModule):

    def __init__(self, config: ConfigManager):
        BaseModule.__init__(self, "VideoDispatchService.WebRTCModule", config)
        self.processList = []

    def __del__(self):
        # self.unsubscribe_pattern_with_callback("webrtc.*", self.webrtc_message_callback_deprecated)
        pass

    def setup_module_pubsub(self):
        # Additional subscribe
        # TODO change those messages to use complete protobuf messaging system
        # self.subscribe_pattern_with_callback("webrtc.*", self.webrtc_message_callback_deprecated)
        pass

    def setup_rpc_interface(self):
        self.rpc_api['create_session'] = {'args': [],
                                          'returns': 'dict',
                                          'callback': self.create_webrtc_session}

    def create_webrtc_session(self, *args, **kwargs):
        print('Should create WebRTC session')

        # Return empty dict
        return {}

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('WebRTCModule - Received message ', pattern, channel, message)
        pass

    def create_session(self, message: CreateSession):

        print('create_session', message)

        # For now just launch test
        port = 8080
        key = "test"

        url = 'https://'+self.config.webrtc_config['hostname'] + ':' + str(port) + '/teraplus?key=' + key
        self.launch_node(port=port, key=key)
        self.publish(message.reply_to, url)

    def webrtc_message_callback_deprecated(self, pattern, channel, message):
        print('WebRTCModule message received', pattern, channel, message)
        parts = channel.split('.')
        if len(parts) == 2 and 'webrtc' in parts[0]:
            # Verify command
            if 'create_session' in parts[1]:
                len_message = len(message)
                protobuf_message = CreateSession()
                protobuf_message.ParseFromString(message.encode('utf-8'))
                print('got protobuf_message: ', protobuf_message)

                """
                got protobuf_message:  source: "UserManagerModule"
                2019-04-02 15:27:40-0400 [-] command: "create_session"
                2019-04-02 15:27:40-0400 [-] reply_to: "server.f9ee231b-8fce-43c2-8075-a9c6f90368fe.create_session"
                """
                self.create_session(protobuf_message)
                # self.publish(protobuf_message.reply_to, 'should send back webrtc server info')

    def launch_node(self, port=8080, key="test"):
        command = [self.config.webrtc_config['executable'],
                   self.config.webrtc_config['script'], str(port), str(key)]

        # stdout=os.subprocess.PIPE, stderr=os.subprocess.PIPE)
        process = subprocess.Popen(command, cwd=os.path.realpath(self.config.webrtc_config['working_directory']))

        # One more process
        self.processList.append({'process': process, 'port': port, 'key': key})

        print('started process', process)


if __name__ == '__main__':
    # Mini test
    from services.VideoDispatch.Globals import config_man
    from twisted.internet import reactor, task
    import services.VideoDispatch.Globals as Globals
    from modules.RedisVars import RedisVars
    from libtera.redis.RedisClient import RedisClient
    from twisted.python import log
    import sys
    from twisted.internet import defer

    # Used for redis events...
    log.startLogging(sys.stdout)

    # Load configuration
    config_man.load_config('VideoDispatchService.ini')

    # Init global variables
    Globals.redis_client = RedisClient(config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Create module
    module = WebRTCModule(config_man)


    def callback_later():
        # Create session message
        from messages.python.CreateSession_pb2 import CreateSession
        from messages.python.RPCMessage_pb2 import RPCMessage
        from libtera.redis.RedisClient import RedisClient
        from libtera.redis.RedisRPCClient import RedisRPCClient
        from datetime import datetime

        print('Calling RPC')
        # Using RPC API
        rpc = RedisRPCClient(config_man.redis_config)

        result = rpc.call('VideoDispatchService.WebRTCModule', 'create_session',
                          bool(True), int(5), float(3.0), b'bytes', str('rien'))

        print(result)
        # ret.addCallback(subscribed_callback)

    # Deferred to call function in 5 secs.
    d = task.deferLater(reactor, 5.0, callback_later)
    reactor.run()
