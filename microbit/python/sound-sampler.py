from microbit import *
import radio

TILT_SENSITIVITY = 0.01  # Something between 0 and 1 to slow down a bit
adjust_mode = True

class Location:
    def __init__(self):
        self.x = 2.0
        self.y = 2.0
        self.prev_x = 0
        self.prev_y = 0

    def show_coords(self):
        if round(self.x) == self.prev_x and round(self.y) == self.prev_y:
            return
        display.set_pixel(self.prev_x, self.prev_y, 0)
        display.set_pixel(round(self.x), round(self.y), 9)
        self.prev_x = round(self.x)
        self.prev_y = round(self.y)

    def update_from_tilt(self):
        self.x = self.constrain(self.x + accelerometer.get_x() / 1023 * TILT_SENSITIVITY)
        self.y = self.constrain(self.y + accelerometer.get_y() / 1023 * TILT_SENSITIVITY)
        self.show_coords()

    @staticmethod
    def constrain(value, lower=0, upper=4):
        return min(max(value, lower), upper)

def display_level(level):
    num_graph_leds = round(level / 255.0 * 25)
    led_num = 0
    for y in range(4, -1, -1):  # bottom to top
        for x in range(5):      # left to right
            display.set_pixel(x, y, 5 if led_num <= num_graph_leds else 0)
            led_num += 1

loc = Location()
radio.on()
radio.config(group=1)

last_message = None

while True:
    if button_a.was_pressed():  # Toggle adjust mode
        adjust_mode = not adjust_mode

    # If adjust mode is on, update coordinates based on tilt.
    if adjust_mode:
        loc.update_from_tilt()
        continue

    level = microphone.sound_level()
    display_level(level)
    message = ','.join(str(item) for item in (round(loc.x), round(loc.y), level))
    if message != last_message:
        last_message = message
        print(message)
        radio.send(message)

    sleep(50)
