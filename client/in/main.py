from listener import SmartDeskListener
from collections import deque
from task_library import TaskLibrary
import time
import os

LIBRARY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "libs")
LIBRARY_MODULE = "test_library"
LIBRARY_CLASS = "TestLibrary"


def process_request(library, data):

    print "data", data

    func = getattr(library, "test", None)

    if func:
        func("apples")




def main():

    uuid = "a" * 4

    queue = deque()
    url = "https://smartdesk-cc.herokuapp.com/input/%s/consume" % uuid

    # /kghf.asg.dd?foo=bazz
    #

    listener = SmartDeskListener(url, deque)
    listener.start()
    library = TaskLibrary(LIBRARY_PATH, LIBRARY_MODULE, LIBRARY_CLASS, a="hello", b=2)

    data = "hello"

    while True:
        try:
            data = queue.popleft()
            process_request(library, data)
        except IndexError:
            # print "no data"
            time.sleep(1.0)
        except KeyboardInterrupt:
            listener.stop()
            break
    print "listener finish"



if __name__ == "__main__":
    main()