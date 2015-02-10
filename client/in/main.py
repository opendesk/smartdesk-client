from listener import SmartDeskListener
from collections import deque
import time
import os
import sys
import imp
try:
    import RPi.GPIO as gpio
except ImportError:
    import dummy_gpio as gpio



LIBRARY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "libs")

TEST_DATA = {
    "dotted_path": "flash.led",
    "args": [],
    "kwargs": {"r": 1, "g": 0, "b": 0, "count": 2 , "dur": 2}
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
    queue = deque()
    url = "https://smartdesk-cc.herokuapp.com/input/%s/consume" % uuid
    listener = SmartDeskListener(url, deque)
    listener.start()

    data = "hello"

    while True:
        try:
            data = queue.popleft()
            process_request(data)
        except IndexError:
            # print "no data"
            process_request(TEST_DATA)
            time.sleep(2.0)
        except KeyboardInterrupt:
            listener.stop()
            break
            
    gpio.cleanup()
    print "listener finish"



if __name__ == "__main__":
    main()