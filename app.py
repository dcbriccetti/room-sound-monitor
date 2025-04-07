# Room Sound Monitor app.py
# Reads the serial port for messages from the aggregator, and via Flask-SocketIO, pushes them
# to a p5.js sketch for display.

import eventlet
eventlet.monkey_patch()
import glob
import serial
from flask import Flask, render_template
from flask_socketio import SocketIO

def find_microbit_port():
    ports = glob.glob('/dev/tty.usbmodem*')
    if ports:
        return ports[0]
    else:
        raise Exception("No micro:bit device found.")

def read_and_push_aggregated_samples():
    while True:
        if ubit_serial.in_waiting > 0:
            try:
                location_level = ubit_serial.readline().decode('utf-8').strip()
                socketio.emit('level change', {'location_level': location_level})
            except Exception as e:
                print("Error reading line:", e)
        socketio.sleep(0.15)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")

port = find_microbit_port()
print("Using port:", port)
ubit_serial = serial.Serial(port, 115200, timeout=0.5)

socketio.start_background_task(read_and_push_aggregated_samples)
socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
