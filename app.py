# Room Sound Monitor app.py
# Reads the serial port for messages from the aggregator, and via Flask-SocketIO, pushes them
# to a p5.js sketch for display.

import eventlet
eventlet.monkey_patch()
import glob
import serial
import time
from flask import Flask, render_template
from flask_socketio import SocketIO
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

def find_microbit_port():
    ports = glob.glob('/dev/tty.usbmodem*')
    if ports:
        return ports[0]
    else:
        raise Exception("No micro:bit device found.")

port = find_microbit_port()
ubit_serial = serial.Serial(port, 115200, timeout=0.5)
print("Using port:", port)
time.sleep(2)

def read_and_push_aggregated_samples():
    while True:
        if ubit_serial.in_waiting > 0:
            try:
                line = ubit_serial.readline().decode('utf-8').strip()
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
    socketio.start_background_task(read_and_push_aggregated_samples)
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
