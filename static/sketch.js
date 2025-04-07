let socket;
let maxes = [];  // will hold values for indices 0 to 24
const LEDS_PER_ROW = 5;
const NUM_LED_ROWS = 5;

function setup() {
    frameRate(10);
    createCanvas(800, 800, WEBGL);

    // Connect to the Flask-SocketIO server.
    socket = io.connect('http://127.0.0.1:5000');

    socket.on('data', msg => {
        const items = msg.data.split(',');
        const missing = items.some(item => item === '');
        if (items.length === 4 && !missing) {
            const locX = Number(items[0]);
            const locY = Number(items[1]);
            if ([locX, locY].some(item => isNaN(item) || item < 0 || item > 4)) {
                console.log("Bad data: " + msg.data);
            } else {
                maxes[locX + locY * LEDS_PER_ROW] = Number(items[2]);
            }
        } else {
            console.log("Bad data: " + msg.data);
        }
    });
}

function draw() {
    background('tan');
    ortho();

    // Define spacing between boxes.
    let spacing = 150;
    // Center the grid horizontally and vertically.
    let startX = -((LEDS_PER_ROW - 1) * spacing) / 2;
    let startY = -((NUM_LED_ROWS - 1) * spacing) / 2;

    // Loop over 5 rows and 5 columns.
    for (let row = 0; row < NUM_LED_ROWS; row++) {
        for (let col = 0; col < LEDS_PER_ROW; col++) {
            let idx = col + row * LEDS_PER_ROW;
            push();
            // Position each object.
            translate(startX + col * spacing, startY + row * spacing, 0);
            if (maxes[idx] !== undefined && maxes[idx] !== "") {
                let val = maxes[idx];
                fill(100, 150, 240);
                sphere(5 + val / 255 * 500);
            } else {
                // Draw a placeholder if no data exists.
                noFill();
                stroke(150);
                sphere(5);
            }
            pop();
        }
    }
}
