#!/usr/bin/python2
# -*- coding: utf-8 -*-

import socket
import threading
import json
import os
from utils import recieve_chunked_stream, send_chunked_stream
from utils import CommunicationError

SOCKET_PATH = "/tmp/omxplayer.sock"

class OMXPSocket(object):
    '''Socket wrapper to recieve command from other processes.'''

    def __init__(self, command_listener, path=SOCKET_PATH):
        self.socket_path = path
        self.command_listener = command_listener

    def start(self):
        '''Start reciever thread.'''
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.bind(self.socket_path)
        self.socket.listen(1)

        def _run():
            while True:
                try:
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
                    self.command_listener(send_res, data)
                except Exception as e:
                    print e
                    continue

        t = threading.Thread(target=_run)
        t.daemon = True
        t.start()
