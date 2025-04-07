let socket;
// Object to store the history arrays for each location.
// Keys: locationIndex (0-24), Values: Array of last 50 max values
let locationMaxHistories = {};
const MAX_HISTORY_LENGTH = 50;

// Grid dimensions
const LEDS_PER_ROW = 5;
const NUM_LED_ROWS = 5;
const TOTAL_LEDS = LEDS_PER_ROW * NUM_LED_ROWS; // Total number of locations

function setup() {
    frameRate(10);
    createCanvas(800, 800); // Your canvas size

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
        const newMax = Number(items[2]);

        if (isNaN(locX) || locX < 0 || locX >= LEDS_PER_ROW ||
            isNaN(locY) || locY < 0 || locY >= NUM_LED_ROWS ||
            isNaN(newMax)) {
            console.log("Bad data values (NaN or out of bounds): " + msg.location_level);
            return;
        }

        const locationIndex = locX + locY * LEDS_PER_ROW;
        locationMaxHistories[locationIndex] = locationMaxHistories[locationIndex] || [];
        const history = locationMaxHistories[locationIndex];
        history.push(newMax);

        while (history.length > MAX_HISTORY_LENGTH) {
            history.shift();
        }
    });

    socket.on('connect_error', (err) => {
        console.error('Connection Error:', err);
    });

    socket.on('disconnect', (reason) => {
        console.log('Disconnected:', reason);
    });
}

function draw() {
    background('lightblue'); // Black background
    const cellWidth = width / LEDS_PER_ROW;
    const cellHeight = height / NUM_LED_ROWS;

    // Iterate through all possible location indices (0 to 24)
    for (let index = 0; index < TOTAL_LEDS; index++) {
        const history = locationMaxHistories[index]; // Get history array for this index

        // Calculate grid position (top-left corner of the cell)
        const col = index % LEDS_PER_ROW;
        const row = Math.floor(index / LEDS_PER_ROW);
        const x = col * cellWidth; // Cell's top-left x
        const y = row * cellHeight; // Cell's top-left y

        // Check if there is history data for this cell
        if (history && history.length > 0) {
            const numBars = history.length;

            // Calculate width for each bar.
            // Option 1: Bars fill cell width exactly (no spacing)
            // const barWidth = cellWidth / numBars;
            // const startX = x;

            // Option 2: Bars use slightly less width to create padding/spacing
            const totalBarAreaWidth = cellWidth * 0.9; // Use 90% of cell width for bars
            const horizontalPadding = cellWidth * 0.1; // Remaining 10% is padding
            const barWidth = totalBarAreaWidth / numBars; // Width of each individual bar
            const startX = x + horizontalPadding / 2; // Start drawing after half the padding

            // --- Draw the bars ---
            fill(255); // Bar color (e.g., white)
            noStroke(); // No outline for the bars for a cleaner look

            // Iterate through the historical values (oldest to newest)
            for (let i = 0; i < numBars; i++) {
                const value = history[i]; // Get the historical value

                // Calculate bar height based on the value, scaled and constrained
                const barHeight = constrain(value * 5, 0, cellHeight);

                // Calculate the x position for this specific bar
                const barX = startX + i * barWidth;

                // Draw the thin vertical bar for this historical value
                // Drawing from the bottom edge (y + cellHeight) upwards
                rect(barX, y + cellHeight - barHeight, barWidth, barHeight);
            }
        }
        // If no history exists for this index, the cell remains black (background color)
    }
}
