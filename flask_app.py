from flask import Flask, render_template, request, jsonify
import json
import threading


app = Flask(__name__)


import zmq
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.connect('ipc:///tmp/message_flow_in')


def long_process(message):
    import time
    import random

    m0 = time.monotonic()
    time.sleep(2 + random.random())
    m1 = time.monotonic()

    processed_message = 'Message processed, "{}" in {:.2f} seconds'.format(message, m1 - m0)
    pub.send(b"0 " + json.dumps({'data': processed_message}).encode('utf-8'))


@app.route('/send', methods=['POST'])
def send(*args, **kwargs):
    message = request.form.get('message', '')

    if not message:
        return jsonify(status='error', data='No message submitted')
    else:
        threading.Thread(target=long_process, args=(message,)).start()
        return jsonify(status='OK', data='Message submitted for processing')


@app.route('/')
def index():
    return render_template('index.html')
