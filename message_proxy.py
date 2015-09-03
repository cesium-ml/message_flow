# http://zguide.zeromq.org/page:all#The-Dynamic-Discovery-Problem
# http://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/devices/forwarder.html

import zmq

IN = 'inproc://in'
OUT = 'inproc://out'

context = zmq.Context()

feed_in = context.socket(zmq.SUB)
feed_in.bind(IN)
feed_in.setsockopt(zmq.SUBSCRIBE, b'')

feed_out = context.socket(zmq.XPUB)
feed_out.bind(OUT)

print('[message_proxy] Forwarding messages between {} and {}'.format(IN, OUT))
zmq.device(zmq.FORWARDER, feed_in, feed_out)
