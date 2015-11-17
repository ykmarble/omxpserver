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

ROOT_PATH = os.path.dirname(sys.argv[0])
PID_FILE_PATH = os.path.join(ROOT_PATH, 'omxpserver.pid')
OMXP_PATH = '/usr/bin/omxplayer'
OMXP_OPT = '-o local'

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

    # open socket to recieve command
    cmd_socket = OMXPSocket(server.consume_command)
    cmd_socket.start()

    server.run()


if __name__ == '__main__':
    try:
        main()
    finally:
        if os.path.exists(PID_FILE_PATH):
            os.remove(PID_FILE_PATH)
