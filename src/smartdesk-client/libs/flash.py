try:
    import RPi.GPIO as gpio
except ImportError:
    import dummy_gpio as gpio
import time

import random
import itertools


RANDOM_VALUES = [
    {"r": False, "g": False, "b": True, "count": 5 , "dur": 0.5},
    {"r": False, "g": True, "b": False, "count": 5 , "dur": 0.5},
    {"r": True, "g": False, "b": False, "count": 5 , "dur": 0.5},
    {"r": False, "g": False, "b": True, "count": 3 , "dur": 1.0},
    {"r": False, "g": True, "b": False, "count": 3 , "dur": 1.0},
    {"r": True, "g": False, "b": False, "count": 3 , "dur": 1.0},
    {"r": False, "g": False, "b": True, "count": 20 , "dur": 0.1},
    {"r": False, "g": True, "b": False, "count": 20 , "dur": 0.1},
    {"r": True, "g": False, "b": False, "count": 20 , "dur": 0.1},
]



def random_led(*args, **kwargs):
    v = RANDOM_VALUES[random.randint(0, 8)]
    led(**v)


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

    gpio.output(11, red)
    gpio.output(13, green)
    gpio.output(15, blue)
    time.sleep(dur)

    gpio.output(11, 1)
    gpio.output(13, 1)
    gpio.output(15, 1)
    time.sleep(dur)