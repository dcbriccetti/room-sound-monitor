# Aggregator receives messages from collector micro:bits and “print”s them to a computer over USB.

from microbit import uart, display
import radio

PREFIX_LEN = 3  # receive_full includes extra bytes

radio.on()
radio.config(group=1)

while True:
    message = radio.receive_full()
    if message:
        contents, strength, _ = message
        print('%s,%d' % (contents[PREFIX_LEN:].decode('utf8'), strength))

    if uart.any():
        line = uart.readline()
        if line:
            command = line.decode().strip()
            display.show(command)
