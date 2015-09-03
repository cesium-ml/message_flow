from flask import Flask, render_template, request, jsonify
import json


app = Flask(__name__)


import zmq
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.connect('inproc://in')


@app.route('/send', methods=['POST'])
def send(*args, **kwargs):
    message = request.args.get('message', '')

    if not message:
        return jsonify(status='error', data='No message submitted')

    else:
        pub.send(b"", json.dumps({'data': message}))
        return jsonify(status='OK', data='Message submitted')


@app.route('/')
def index():
    return render_template('index.html')
