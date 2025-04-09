# Room Sound Monitor app.py
# Reads the serial port for messages from the aggregator, and via Flask-SocketIO, pushes them
# to a p5.js sketch for display.

import eventlet
eventlet.monkey_patch()
import glob
import serial
from flask import Flask, render_template
from flask_socketio import SocketIO

def find_microbit_port() -> str:
    ports = glob.glob('/dev/tty.usbmodem*')
    if ports:
        return ports[0]
    else:
        raise Exception("No micro:bit device found.")


def read_and_push_aggregated_samples() -> None:
    last_sequence_numbers = {}  # Dictionary to store the last sequence number for each (x, y)

    while True:
        if ubit_serial.in_waiting > 0:
            try:
                location_level = ubit_serial.readline().decode('utf-8').strip()
                print(location_level)
                parts = location_level.split(",")
                if len(parts) != 5:
                    raise ValueError(f"Expected 5 fields but got {len(parts)}: {parts}")
                x, y, sequence_number, level, _ = map(int, parts)
                location_key = (x, y)

                if location_key in last_sequence_numbers and sequence_number != last_sequence_numbers[location_key] + 1:
                    print("Sequence number skipped for location", location_key, "Last:",
                          last_sequence_numbers[location_key], "New:", sequence_number)

                last_sequence_numbers[location_key] = sequence_number
                socketio.emit('level change', {'location_level': location_level})
            except ValueError as ve:
                print("Value error processing line:", ve)
            except Exception as e:
                print("Error reading line:", e)
        socketio.sleep(0.1)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

@app.route('/')
def index() -> str:
    return render_template('index.html')

@socketio.on('connect')
def handle_connect() -> None:
    print("Client connected")

port = find_microbit_port()
print("Using port:", port)
ubit_serial = serial.Serial(port, 115200, timeout=0.5)

socketio.start_background_task(read_and_push_aggregated_samples)
socketio.run(app, debug=False, allow_unsafe_werkzeug=True)  # debug=True causes errors with serial reading, and with dict corruption
