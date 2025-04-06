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
