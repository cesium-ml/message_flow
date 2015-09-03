from tornado import websocket, web, ioloop


# Could also use: http://aaugustin.github.io/websockets/


class WebSocket(websocket.WebSocketHandler):
    participants = set()

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in self.participants:
            self.participants.append(self)

    def on_close(self):
        if self in self.participants:
            self.participants.remove(self)

    def on_message(self, message):
        # Ignore incoming messages
        pass

    # http://mrjoes.github.io/2013/06/21/python-realtime.html
    @classmethod
    def broadcast(cls, data):
        print('Sending to websocket: {}'.format(data))
        for p in self.participants:
            p.write_message(data)


if __name__ == "__main__":
    PORT = 4567
    LOCAL_OUTPUT = 'inproc://out'

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
