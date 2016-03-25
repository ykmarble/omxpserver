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
    """
    Make a UNIX domain socket which recieves command of omxpserver from other processes.
    """

    def __init__(self, command_listener, path=SOCKET_PATH):
        """
        @command_listener: Function which will be called if command is recieved.
        @path: The path of UNIX domain socket.
        """
        self.socket_path = path
        self.command_listener = command_listener

    def start(self):
        """
        Start reciever thread.
        """
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.bind(self.socket_path)
        self.socket.listen(1)


        t = threading.Thread(target=self.mainloop)
        t.daemon = True
        t.start()

    def mainloop(self):
        """
        The main loop of reciver thread.
        This method will be called by start method.
        """
        while True:
            csock, addr = self.socket.accept()
            try:
                rawdata = recieve_chunked_stream(csock)
            except CommunicationError as e:
                send_chunked_stream(csock, str(e))
                csock.close()
                continue
            data = None
            try:
                data = json.loads(rawdata)
            except ValueError:
                print "Recieved invalied data."
                send_chunked_stream(csock, "Recieved invalied data.")
                csock.close()
                continue
            try:
                self.command_listener(
                    lambda d: send_chunked_stream(csock, d),
                    data)
            except Exception as e:
                print e
                send_chunked_stream(csock, str(e))
                csock.close()
                continue
