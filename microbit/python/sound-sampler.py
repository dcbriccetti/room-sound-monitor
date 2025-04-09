from microbit import *
import radio
from random import randint

NUM_SAMPLES_IN_BURST = 10
INTER_SAMPLE_DELAY = 10
SEND_DELAY_RANGE = 300, 350
LOCATION_BRIGHTNESS = 9
LEVEL_BRIGHTNESS = 5
TILT_SENSITIVITY = 0.01

adjust_mode = True

class Location:
    def __init__(self) -> None:
        self.x = 2.0  # Real numbers that can change gradually from tilting in adjust mode
        self.y = 2.0
        self.prev_rx = None  # Previous rounded values used to avoid unnecessary pixel setting
        self.prev_ry = None

    def rx(self) -> int:
        return round(self.x)

    def ry(self) -> int:
        return round(self.y)

    def update_location_from_tilt(self) -> None:
        self.x = self.constrain(self.x + accelerometer.get_x() / 1023 * TILT_SENSITIVITY)
        self.y = self.constrain(self.y + accelerometer.get_y() / 1023 * TILT_SENSITIVITY)

        if self.rx() == self.prev_rx and self.ry() == self.prev_ry:
            return  # Skip updating the display when no change

        if self.prev_rx is not None:  # Need to turn off previous?
            display.set_pixel(self.prev_rx, self.prev_ry, 0)

        display.set_pixel(self.rx(), self.ry(), LOCATION_BRIGHTNESS)

        self.prev_rx = self.rx()
        self.prev_ry = self.ry()

    @staticmethod
    def constrain(value: float, lower=0, upper=4) -> float:
        return min(max(value, lower), upper)

def display_sound_level_graph(level: int) -> None:
    num_graph_leds = int(level / 255.0 * 25)
    led_num = 0
    for y in range(4, -1, -1):  # bottom to top
        for x in range(5):      # left to right
            display.set_pixel(x, y, LEVEL_BRIGHTNESS if led_num < num_graph_leds else 0)
            led_num += 1

def highest_level_from_multiple_samples() -> int:
    highest_level = 0
    for n in range(NUM_SAMPLES_IN_BURST):
        level = microphone.sound_level()
        if level > highest_level:
            highest_level = level
        sleep(INTER_SAMPLE_DELAY)
    return highest_level

def main() -> None:
    global adjust_mode

    loc = Location()
    radio.on()
    radio.config(group=1)

    last_level = None
    sequence_number = 1

    while True:
        if button_a.was_pressed():  # Toggle adjust mode
            adjust_mode = not adjust_mode

        if adjust_mode:
            loc.update_location_from_tilt()
            continue

        level = highest_level_from_multiple_samples()
        display_sound_level_graph(level)
        display.set_pixel(loc.rx(), loc.ry(), LOCATION_BRIGHTNESS)
        if level != last_level:
            last_level = level
            radio.send(','.join(str(item) for item in [loc.rx(), loc.ry(), sequence_number, level]))
            sequence_number += 1

        sleep(randint(*SEND_DELAY_RANGE))  # Randomize to hopefully reduce radio collisions

main()
