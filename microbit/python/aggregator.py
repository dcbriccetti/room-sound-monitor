from microbit import *
import radio

radio.on()
radio.config(group=1)

while True:
    message = radio.receive_full()
    if message:
        b, sig_str, t = message
        print('%s,%d' % (b[3:].decode('utf8'), sig_str))
