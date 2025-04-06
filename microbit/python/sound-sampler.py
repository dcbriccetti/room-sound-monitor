from microbit import *
import radio

TILT_SENSITIVITY = 0.01  # Something between 0 and 1 to slow down a bit
adjust_mode = True
x = 2.0
y = 2.0
prev_x = 0
prev_y = 0

def show_coords():
    global prev_x, prev_y
    if round(x) == prev_x and round(y) == prev_y:
        return
    display.set_pixel(prev_x, prev_y, 0)
    display.set_pixel(round(x), round(y), 9)
    prev_x = round(x)
    prev_y = round(y)

def update_coord(current, delta, lower=0, upper=4):
    return min(max(current + delta, lower), upper)

def display_level(level):
    num_graph_leds = round(level / 255.0 * 25)
    led_num = 0
    for y in range(4, -1, -1):  # bottom to top
        for x in range(5):      # left to right
            display.set_pixel(x, y, 5 if led_num <= num_graph_leds else 0)
            led_num += 1

radio.on()
radio.config(group=1)

while True:
    if button_a.was_pressed():  # Toggle adjust mode
        adjust_mode = not adjust_mode

    # If adjust mode is on, update coordinates based on tilt.
    if adjust_mode:
        x = update_coord(x, accelerometer.get_x() / 1023 * TILT_SENSITIVITY)
        y = update_coord(y, accelerometer.get_y() / 1023 * TILT_SENSITIVITY)
        show_coords()
    else:
        levels = []
        start_time = running_time()

        while running_time() - start_time < 500:
            levels.append(microphone.sound_level())
            sleep(50)

        num_levels = len(levels)
        mean_level = sum(levels) / num_levels
        max_level = max(levels)
        display_level(max_level)

        message = ','.join(str(item) for item in
                           (round(x),
                            round(y),
                            num_levels,
                            min(levels),
                            mean_level,
                            max_level
                            ))
        print(message)
        radio.send(message)
