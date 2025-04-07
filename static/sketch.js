let socket;
const MAX_COLLECTED_ITEMS = 100;
const MAX_HISTORY_ITEMS = 50;
const LEDS_PER_ROW = 5;
const NUM_LED_ROWS = 5;
const LEVEL_VISUALIZATION_SCALE = 5;

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

function setup() {
    frameRate(10);
    const canvas = createCanvas(700, 700);
    canvas.parent('sketch-container');

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
        const mean = collected.getMeanAndDeleteLevels(index);
        historical.add(index, mean);
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
        const row = Math.floor(index / LEDS_PER_ROW);
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
                const barHeight = constrain(levels[i] * LEVEL_VISUALIZATION_SCALE, 0, cellHeight);
                rect(x + i * barWidth, y + cellHeight - barHeight, barWidth, barHeight);
            }
        }
    })
}
