from tornado import websocket, web, ioloop
import json


# Could also use: http://aaugustin.github.io/websockets/


class WebSocket(websocket.WebSocketHandler):
    participants = set()

    def __init__(self, *args, **kwargs):
        websocket.WebSocketHandler.__init__(self, *args, **kwargs)

        self.authenticated = False
        self.auth_failures = 0
        self.user = None

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in self.participants:
            self.participants.add(self)
            self.request_auth()

    def on_close(self):
        if self in self.participants:
            self.participants.remove(self)

    def on_message(self, auth_token):
        self.authenticate(auth_token)
        if not self.authenticated and self.auth_failures < 3:
            self.request_auth()

    def request_auth(self):
        self.auth_failures += 1
        self.send_json(id="AUTH REQUEST")

    def send_json(self, **kwargs):
        self.write_message(json.dumps(kwargs))

    def authenticate(self, auth_token):
        # TODO MUST UPDATE THIS
        self.authenticated = True
        try:
            self.user, token = json.loads(auth_token)["token"].split()
        except:
            self.send_json(id="AUTH FAILED")
            return False

        # !! Validate token here !!
        # check_token(token)

        self.send_json(id="AUTH OK")

    # http://mrjoes.github.io/2013/06/21/python-realtime.html
    @classmethod
    def broadcast(cls, data):
        channel, data = data[0].decode('utf-8').split(" ", 1)
        user = json.loads(data)["user"]

        for p in cls.participants:
            if p.authenticated and p.user == user:
                p.write_message(data)


if __name__ == "__main__":
    PORT = 4567
    LOCAL_OUTPUT = 'ipc:///tmp/message_flow_out'

    import zmq

    # https://zeromq.github.io/pyzmq/eventloop.html
    from zmq.eventloop import ioloop, zmqstream

    ioloop.install()

    ctx = zmq.Context()

    sub = ctx.socket(zmq.SUB)
    sub.connect(LOCAL_OUTPUT)
    sub.setsockopt(zmq.SUBSCRIBE, b'')

    print('[websocket_server] Broadcasting {} to all websockets'.format(LOCAL_OUTPUT))
    stream = zmqstream.ZMQStream(sub)
    stream.on_recv(WebSocket.broadcast)

    server = web.Application([
        (r'/websocket', WebSocket),
    ])
    server.listen(PORT)

    print('[websocket_server] Listening for incoming websocket connections on port {}'.format(PORT))
    ioloop.IOLoop.instance().start()
