import redis
from messages.python.RPCMessage_pb2 import RPCMessage, Value
from datetime import datetime
import json
import uuid


class RedisRPCClient:
    def __init__(self, config: dict, timeout=5):
        self.config = config
        self.timeout = timeout
        # Create a unique random pattern
        self.pattern = 'RedisRPCClient.' + str(uuid.uuid4())
        self.msg_id = 0

    def call(self, module_name: str, function_name: str, *args):
        print(self.pattern, ' calling:', module_name, function_name, args)
        # Get redis instance
        r = redis.StrictRedis(host=self.config['hostname'], port=self.config['port'], db=self.config['db'])
        p = r.pubsub()

        message = RPCMessage()
        message.method = function_name
        message.timestamp = datetime.now().timestamp()
        message.id = self.msg_id
        self.msg_id = self.msg_id + 1
        message.reply_to = self.pattern

        topic = 'module.' + module_name + '.rpc'

        # Iterate through args
        rpc_args = []
        for arg in args:
            if isinstance(arg, bool):
                val = Value()
                val.bool_value = arg
                rpc_args.append(val)
            elif isinstance(arg, float):
                val = Value()
                val.double_value = arg
                rpc_args.append(val)
            elif isinstance(arg, int):
                val = Value()
                val.int_value = arg
                rpc_args.append(val)
            elif isinstance(arg, str):
                val = Value()
                val.string_value = arg
                rpc_args.append(val)
            elif isinstance(arg, bytes):
                val = Value()
                val.bytes_value = arg
                rpc_args.append(val)
            else:
                print('Invalid arg:', arg)

        # Set args
        message.args.extend(rpc_args)

        # Will answer on the replay_to field
        p.subscribe(message.reply_to)
        # Publish request

        r.publish(topic, message.SerializeToString())
        # Read answer (waiting)
        # First message is for subscribe result
        message = p.get_message(timeout=self.timeout)
        # Second message is data received
        message = p.get_message(timeout=self.timeout)

        if message:
            result = json.loads(message['data'])
            return result['return_value']

        return None


