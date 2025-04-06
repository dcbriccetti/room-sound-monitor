# Room Sound Monitor

Uses multiple micro:bits, and p5.js to monitor and display sound levels at various points in a room.

## Components

### sound-sampler.py
This runs on multiple micro:bits placed around the room where you want to monitor sound.
Every half-second or so it sends sound level data (min, mean, max) by radio to the aggregator
micro:bit.

### aggregator.py
Receives radio messages from the sound samplers and writes them to the serial port. The
micro:bit running this is connected to a computer able to run full Python and a web browser.

### app.py
Reads the serial port for messages from the aggregator, and via WebSockets, pushes them
to a p5.js sketch.

### sketch.js
Visually displays the sound levels from the various samplers.

## Installation
- Use Mu to flash sound-sampler.py onto one or more micro:bits whose microphones will
be used to monitor sound. (As of 2025-04-06, Dave Briccetti finds that the
python.makecode.org editor uses a version of MicroPython that fails to get sound
levels correctly after flashing, then disconnecting the USB cable, then reconnecting.)
When the program starts, it’s in a mode where you specify which of 25 spots in the
room (corresponding to the micro:bit’s 5 ⨉ 5 LED grid) the micro:bit will be placed in.
Tilt the micro:bit until the light moves to the correct position, then press “A”.
Press “A” again if you want to reset the location.
- Flash aggregator.py onto one micro:bit, and leave it connected to a “host” (teacher)
computer
- Run app.py on the host computer, then go to 127.0.0.1:5000 in a Web browser.
