try:
    import RPi.GPIO as gpio
except ImportError:
    import dummy_gpio as gpio
import time



def led(r, g, b, count, dur):
    gpio.setmode(gpio.BOARD)

    red = 0 if r else 1
    green = 0 if g else 1
    blue = 0 if b else 1

    gpio.setup(11, gpio.OUT)
    gpio.setup(13, gpio.OUT)
    gpio.setup(15, gpio.OUT)

    for i in range(count):
        _flash(red, green, blue, dur)

    gpio.cleanup()


def _flash(red, green, blue, dur):
    print "on"
    gpio.output(11, red)
    gpio.output(13, green)
    gpio.output(15, blue)
    time.sleep(dur)
    print "off"
    gpio.output(11, 1)
    gpio.output(13, 1)
    gpio.output(15, 1)
    time.sleep(dur)