# Room Sound Monitor app.py
# Reads the serial port for messages from the aggregator, and via WebSockets, pushes them
# to a p5.js sketch.

import eventlet
eventlet.monkey_patch()
import serial
import time
from flask import Flask, render_template
from flask_socketio import SocketIO
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

ser = serial.Serial('/dev/tty.usbmodem102', 115200, timeout=0.5)
time.sleep(2)

def read_microbit():
    while True:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8').strip()
                print(line)
                socketio.emit('data', {'data': line})
            except Exception as e:
                print("Error reading line:", e)
        socketio.sleep(0.15)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == '__main__':
    socketio.start_background_task(read_microbit)
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
