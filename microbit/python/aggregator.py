# Aggregator receives messages from collector micro:bits and “print”s them to a computer over USB.

from microbit import *
import radio

radio.on()
radio.config(group=1)

while True:
    message = radio.receive_full()
    if message:
        contents, strength, _ = message
        print('%s,%d' % (contents[3:].decode('utf8'), strength))
