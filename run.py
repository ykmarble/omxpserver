#!/usr/bin/python2
# -*- coding: utf-8 -*-

from core.omxpserver import OMXPSever
from core.omxpsocket import OMXPSocket
import argparse
import os
import sys
import time
import threading
import subprocess
import logging

ROOT_PATH = os.path.dirname(sys.argv[0])
PID_FILE_PATH = os.path.join(ROOT_PATH, 'omxpserver.pid')
OMXP_PATH = '/usr/bin/omxplayer'
OMXP_OPT = '-o local'

logging.basicConfig(level=logging.INFO)

def main():
    # parse argument
    parser = argparse.ArgumentParser(description='omxplayer frontend with queue.')
    parser.add_argument('-v', '--verbose', action='store_true')
    arg = parser.parse_args()

    # check already omxpserver or omxp is running
    if (os.path.exists(PID_FILE_PATH) and
            subprocess.call(['pgrep', '-F', PID_FILE_PATH]) == 0):
        print 'omxpserver is already running.'
        return

    # make PID file
    with open(PID_FILE_PATH, 'w') as f:
        f.write(str(os.getpid()) + "\n")

    server = OMXPSever()
    server.destructer = lambda : os.remove(PID_FILE_PATH)

    # open socket to recieve command
    cmd_socket = OMXPSocket(server.consume_command)
    cmd_socket.start()
    cmd_socket.daemon = True

    server.run()


if __name__ == '__main__':
    try:
        main()
    finally:
        if os.path.exists(PID_FILE_PATH):
            os.remove(PID_FILE_PATH)
