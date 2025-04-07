const MAX_COLLECTED_ITEMS = 100;
const MAX_HISTORY_ITEMS = 50;
const LEDS_PER_ROW = 5;
const NUM_LED_ROWS = 5;
const MAX_CANVAS_SIZE = 700; // Define a max size (adjust if needed)

let socket;
let levelVisualizationScale = 5; // Initial value, will be updated by slider
let scaleSlider;
let scaleValueSpan;

// Calculates the side length for a square canvas based on window size
function calculateCanvasSize() {
    const padding = 30; // Total horizontal padding/margin desired
    // Estimate vertical space needed for title, controls, padding etc.
    const topMargin = 120; // Adjust this based on the actual height of elements above the canvas
    const availableWidth = windowWidth - padding;
    const availableHeight = windowHeight - topMargin;

    // Determine the side length: minimum of available width, height, and max size
    // Use floor to avoid fractional pixels
    let side = floor(min(availableWidth, availableHeight, MAX_CANVAS_SIZE));

    // Ensure a minimum size so it doesn't disappear
    side = max(side, 100); // Minimum size of 100px (adjust as needed)

    return side;
}

class LevelsByIndex {
    constructor(max_elements) {
        this.max_elements = max_elements;
        this.levelsByIndex = [];
    }

    add(index, level) {
        if (this.levelsByIndex[index] === undefined) {
            this.levelsByIndex[index] = [];
        }
        const levels = this.levelsByIndex[index];
        levels.push(level);
        while (levels.length > this.max_elements) {
            levels.shift();
        }
    }

    getMeanAndDeleteLevels(index) {
        const levels = this.levelsByIndex[index];
        if (levels !== undefined && levels.length > 0) {
            const mean = levels.reduce((sum, level) => sum + level, 0) / levels.length;
            this.levelsByIndex[index] = [];
            return mean;
        }
        return 0;
    }

    forEach(callback) {
        this.levelsByIndex.forEach((levels, index) => {
            if (levels !== undefined) {
                callback(levels, index);
            }
        });
    }
}

const collected = new LevelsByIndex(MAX_COLLECTED_ITEMS);
const historical = new LevelsByIndex(MAX_HISTORY_ITEMS);

function updateScale() {
    levelVisualizationScale = scaleSlider.value();
    scaleValueSpan.html(levelVisualizationScale.toFixed(1)); // Show one decimal place
}

function setup() {
    frameRate(10);

    const initialSize = calculateCanvasSize();
    const canvas = createCanvas(initialSize, initialSize);
    canvas.parent('sketch-container');

    scaleSlider = select('#scaleSlider');
    scaleValueSpan = select('#scaleValue');
    scaleSlider.value(levelVisualizationScale);
    scaleSlider.input(updateScale);
    scaleValueSpan.html(levelVisualizationScale);

    // Connect to the Flask-SocketIO server.
    socket = io.connect('http://127.0.0.1:5000');

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('level change', msg => {
        if (!msg || typeof msg.location_level !== 'string') {
            console.log("Received invalid message:", msg);
            return;
        }
        const items = msg.location_level.split(',');
        const missing = items.some(item => item === '');

        if (items.length !== 4 || missing) {
            console.log("Bad data format: " + msg.location_level);
            return;
        }

        const locX = Number(items[0]);
        const locY = Number(items[1]);
        const level = Number(items[2]);

        if (isNaN(locX) || locX < 0 || locX >= LEDS_PER_ROW ||
            isNaN(locY) || locY < 0 || locY >= NUM_LED_ROWS ||
            isNaN(level)) {
            console.log("Bad data values (NaN or out of bounds): " + msg.location_level);
            return;
        }

        collected.add(locX + locY * LEDS_PER_ROW, level);
    });

    socket.on('connect_error', (err) => {
        console.error('Connection Error:', err);
    });

    socket.on('disconnect', (reason) => {
        console.log('Disconnected:', reason);
    });
}

function addHistoryItem() {
    collected.forEach((levels, index) => {
        historical.add(index, collected.getMeanAndDeleteLevels(index));
    })
}

function draw() {
    if (frameCount % 10 === 0) {
        addHistoryItem();
    }

    background('lightblue');
    const cellWidth = width / LEDS_PER_ROW;
    const cellHeight = height / NUM_LED_ROWS;

    historical.forEach((levels, index) => {
        const col = index % LEDS_PER_ROW;
        const row = floor(index / LEDS_PER_ROW);
        const x = col * cellWidth; // Cell's top-left x
        const y = row * cellHeight; // Cell's top-left y

        if (levels && levels.length > 0) {
            stroke(0)
            fill(255)
            rect(x, y, cellWidth, cellHeight);

            const numBars = levels.length;
            const barWidth = cellWidth / MAX_HISTORY_ITEMS;
            fill('green');
            noStroke();

            for (let i = 0; i < numBars; i++) {
                const barHeight = constrain(levels[i] * levelVisualizationScale, 0, cellHeight);
                rect(x + i * barWidth, y + cellHeight - barHeight, barWidth, barHeight);
            }
        }
    });
}

function windowResized() {
    const newSize = calculateCanvasSize();
    resizeCanvas(newSize, newSize);
}
