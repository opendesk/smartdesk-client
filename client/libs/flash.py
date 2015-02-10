try:
    import RPi.GPIO as gpio
except ImportError:
    import dummy_gpio as gpio
import time


def led(r, g, b, count, dur):
    gpio.setmode(gpio.BOARD)

    if r < 0:
        r = 0
    if g < 0:
        g = 0
    if b < 0:
        b = 0
    if r > 1:
        r = 1
    if g > 1:
        g = 1
    if b > 1:
        b = 1

    gpio.setup(11, gpio.OUT)
    gpio.setup(13, gpio.OUT)
    gpio.setup(15, gpio.OUT)

    for i in range(count):
        _flash(r, g, b, dur)

    gpio.cleanup()


def _flash(r, g, b, dur):

    gpio.output(11, r)
    gpio.output(13, g)
    gpio.output(15, b)
    time.sleep(dur)
    gpio.output(11, 0)
    gpio.output(13, 0)
    gpio.output(15, 0)
    time.sleep(dur)