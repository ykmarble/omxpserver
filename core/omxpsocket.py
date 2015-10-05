#!/usr/bin/python2
# -*- coding: utf-8 -*-

import socket
import threading
import json
import Queue

SOCKET_PATH = "/tmp/omxplayer.sock"

class OMXPSocket(object):
    def __init__(self, path=SOCKET_PATH):
        self.socket_path = path
        self.queue = Queue.Queue()

    def run(self):
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.bind(self.socket_path)
        self.socket.listen(1)

        def _run():
            while True:
                csock, addr = self.socket.accept()
                rawdata = csock.recv(4096)
                data = None
                try:
                    data = json.loads(rawdata)
                except ValueError:
                    continue
                if not (data.haskey("command") and data.haskey("args")):
                    continue
                self.queue.put(data)

        t = threading.Thread(target=_run)
        t.start()

    def pop_data(self):
        try:
            return self.queue.get_nowait()
        except Queue.Empty:
            return None
