#!/usr/bin/env python

from listener import SmartDeskListener
from collections import deque
import time
import os
import sys
import imp
import signal
try:
    import RPi.GPIO as gpio
except ImportError:
    import libs.dummy_gpio as gpio

LIBRARY_PATH = os.path.join(os.path.dirname(__file__), "libs")

TEST_DATA = {
    "dotted_path": "flash.random_led",
    "args": [],
    "kwargs": {}
}

def process_request(data):

    dotted_path = data.get("dotted_path")
    elements = dotted_path.split(".")
    module = elements[-2]
    func_name = elements[-1]
    args = data.get("args")
    kwargs = data.get("kwargs")

    sys.path.append(os.path.join(LIBRARY_PATH, *(elements[:-2])))
    f, pathname, description =  imp.find_module(module)
    library_module = imp.load_module(module, f, pathname, description)
    func = getattr(library_module, func_name, None)

    if func:
        func(*args, **kwargs)


def main():

    uuid = "a" * 4

    url = "https://smartdesk-cc.herokuapp.com/input/%s/consume" % uuid
    listener = SmartDeskListener(url)
    listener.start()

    while True:
        try:
            data = listener.read()
            if data is not None:
                process_request(data)
            else:
                pass
                # process_request(TEST_DATA)
            time.sleep(1.0)
        except KeyboardInterrupt:
            listener.stop()
            gpio.cleanup()
            break
        except SystemExit:
            listener.stop()
            gpio.cleanup()
            break


if __name__ == "__main__":
    main()