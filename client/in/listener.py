import requests
from requests.adapters import ReadTimeout
import threading
import json

class SmartDeskListener(object):

    def __init__(self, url, queue):

        self.url = url
        self.queue = queue
        self.thread = None
        self.alive = threading.Event()

    def start(self):
        self._StartThread()

    def stop(self):
        self._StopThread()

    def _StartThread(self):
        self.thread = threading.Thread(target=self._threadEntry)
        self.thread.setDaemon(1)
        self.alive.set()
        self.thread.start()

    def _StopThread(self):
        if self.thread is not None:
            self.alive.clear()          #clear alive event for thread
            self.thread.join()          #wait until thread has finished
            self.thread = None


    def _threadEntry(self):

        print "starting listener"
        while self.alive.isSet():
            buffer = []
            try:
                r = requests.get(self.url, stream=True)
                for content in r.iter_content():
                    if content == "\r\n":
                        if buffer:
                            self.queue.append(json.loads("".join(buffer)))
                            buffer = []
                            if not self.alive.isSet():
                                break
                    else:
                        buffer.append(content)
            except ReadTimeout:
                print "timeout"

            print "starting again"



