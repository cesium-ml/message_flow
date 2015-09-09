from flask import Flask, render_template, request, jsonify
import json


app = Flask(__name__)


import zmq
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.connect('ipc:///tmp/message_flow_in')


@app.route('/send', methods=['POST'])
def send(*args, **kwargs):
    message = request.form.get('message', '')

    if not message:
        return jsonify(status='error', data='No message submitted')

    else:
        pub.send(b"0 " + json.dumps({'data': message}).encode('utf-8'))
        return jsonify(status='OK', data='Message submitted')


@app.route('/')
def index():
    return render_template('index.html')
