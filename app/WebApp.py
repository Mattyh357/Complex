import sys
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import eventlet


class WebApp:

    flask: Flask
    socketio: SocketIO

    port = 1234

    def __init__(self, ip, port):
        eventlet.monkey_patch()

        self.flask = Flask(__name__, static_folder='web', template_folder='web')
        self.socketio = SocketIO(self.flask, cors_allowed_origins="*")

        @self.flask.route('/')
        def index():
            return render_template('index.html')

    def send_data(self, data):
        print("Emitting:", data)
        self.socketio.emit('data', data)

    def start(self):
        self.socketio.run(self.flask, host='0.0.0.0', port=self.port, debug=False)