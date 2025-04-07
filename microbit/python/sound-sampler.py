from microbit import *
import radio
from random import randint

INTER_SAMPLE_DELAY = 10
SEND_DELAY_RANGE = 200, 210
LOCATION_BRIGHTNESS = 9
LEVEL_BRIGHTNESS = 5
TILT_SENSITIVITY = 0.01

adjust_mode = True

class Location:
    def __init__(self):
        self.x = 2.0
        self.y = 2.0
        self.prev_rx = None
        self.prev_ry = None

    def rx(self):
        return round(self.x)

    def ry(self):
        return round(self.y)

    def show_coords(self):
        if self.rx() == self.prev_rx and self.ry() == self.prev_ry:
            return
        if self.prev_rx is not None:
            display.set_pixel(self.prev_rx, self.prev_ry, 0)
        display.set_pixel(self.rx(), self.ry(), 9)
        self.prev_rx = self.rx()
        self.prev_ry = self.ry()

    def update_from_tilt(self):
        self.x = self.constrain(self.x + accelerometer.get_x() / 1023 * TILT_SENSITIVITY)
        self.y = self.constrain(self.y + accelerometer.get_y() / 1023 * TILT_SENSITIVITY)
        self.show_coords()

    @staticmethod
    def constrain(value, lower=0, upper=4):
        return min(max(value, lower), upper)

def display_level(level):
    num_graph_leds = int(level / 255.0 * 25)
    led_num = 0
    for y in range(4, -1, -1):  # bottom to top
        for x in range(5):      # left to right
            display.set_pixel(x, y, LEVEL_BRIGHTNESS if led_num <= num_graph_leds else 0)
            led_num += 1

loc = Location()
radio.on()
radio.config(group=1)

last_message = None

while True:
    if button_a.was_pressed():  # Toggle adjust mode
        adjust_mode = not adjust_mode

    if adjust_mode:
        loc.update_from_tilt()
        continue

    highest_level = 0
    for n in range(10):
        level = microphone.sound_level()
        if level > highest_level:
            highest_level = level
        sleep(INTER_SAMPLE_DELAY)
    display_level(highest_level)
    display.set_pixel(round(loc.x), round(loc.y), LOCATION_BRIGHTNESS)
    message = ','.join(str(item) for item in (loc.rx(), loc.ry(), highest_level))
    if message != last_message:
        last_message = message
        radio.send(message)

    sleep(randint(*SEND_DELAY_RANGE))  # Randomize to hopefully reduce radio collisions
