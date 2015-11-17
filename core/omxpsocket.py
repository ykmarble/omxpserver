#!/usr/bin/python2
# -*- coding: utf-8 -*-

import socket
import threading
import json
import Queue
import os
from utils import recieve_chunked_stream, send_chunked_stream
from utils import CommunicationError

SOCKET_PATH = "/tmp/omxplayer.sock"

class OMXPSocket(object):
    '''Socket wrapper to recieve command from other processes.'''

    def __init__(self, path=SOCKET_PATH):
        self.socket_path = path
        self.queue = Queue.Queue()

    def start(self):
        '''Start reciever thread.'''
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.bind(self.socket_path)
        self.socket.listen(1)

        def _run():
            while True:
                csock, addr = self.socket.accept()
                try:
                    rawdata = recieve_chunked_stream(csock)
                except CommunicationError as e:
                    print e
                    continue
                data = None
                try:
                    data = json.loads(rawdata)
                except ValueError:
                    csock.close()
                    continue
                def send_res(d):
                    try:
                        send_chunked_stream(csock, d)
                    except socket.error:
                        pass
                self.queue.put((send_res, data))

        t = threading.Thread(target=_run)
        t.daemon = True
        t.start()

    def pop_data(self):
        '''Pop command data. Return None if new arrival data is nothing'''
        try:
            return self.queue.get()
        except Queue.Empty:
            return None
