#!/usr/bin/python2
# -*- coding: utf-8 -*-

from core.omxpserver import OMXPSever
import argparse
import os
import sys
import time
import threading
import errno

ROOT_PATH = os.path.dirname(sys.argv[0])
PLAYLIST_PATH = os.path.join(ROOT_PATH, 'playlist')
PID_FILE_PATH = os.path.join(ROOT_PATH, 'omxpserver.pid')
COMMAND_PIPE_PATH = os.path.join(ROOT_PATH, 'omxpserver-pipe')
OMXP_PATH = '/usr/bin/omxplayer'
OMXP_OPT = '-o local'

def main():
    parser = argparse.ArgumentParser(description='omxplayer frontend with queue.')
    parser.add_argument('-p', '--playlist')
    parser.add_argument('-q', '--queue', default=PLAYLIST_PATH)
    parser.add_argument('-v', '--verbose', action='store_true')
    arg = parser.parse_args()
    if arg.queue != PLAYLIST_PATH and arg.playlist != None:
        print "Don't specify playlist and queue both."
        return
    if arg.playlist != None and not os.path.isfile(arg.playlist):
        print '{} is not file.'.format(arg.playlist)
        return
    elif os.path.exists(arg.queue) and not os.path.isfile(arg.queue):
        print '{} is not file.'.format(arg.queue)
        return

    # check already omxpserver or omxp is running
    if os.path.exists(PID_FILE_PATH):
        print 'omxpserver is already running.'
        return

    with open(PID_FILE_PATH, 'w') as f:
        f.write(str(os.getpid()))

    if arg.playlist != None:
        server = OMXPSever(arg.playlist)
        server.consume_list = False
        server.set_playlist()
    else:
        server = OMXPSever(arg.queue)
    frontend_stdin = threading.Thread(target=lambda: stdin_reader(server.command_queue))
    frontend_stdin.daemon = True
    frontend_stdin.start()
    frontend_pipe = threading.Thread(target=lambda: command_reader(server.command_queue))
    frontend_pipe.daemon = True
    frontend_pipe.start()
    server.run()

def stdin_reader(queue):
    while True:
        queue.put(raw_input())

def command_reader(queue):
    # make fifo for sending message to omxpserver
    if os.path.exists(COMMAND_PIPE_PATH):
        os.remove(COMMAND_PIPE_PATH)
    os.mkfifo(COMMAND_PIPE_PATH)
    command_fd = os.open(COMMAND_PIPE_PATH, os.O_RDONLY | os.O_NONBLOCK)

    while True:
        try:
            buffer = os.read(command_fd, 4096)
        except OSError as err:
            if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                buffer = ''
            else:
                raise
        if buffer == '':
            time.sleep(1)
            continue
        queue.put(buffer.strip())

if __name__ == '__main__':
    try:
        main()
    finally:
        if os.path.exists(PID_FILE_PATH):
            os.remove(PID_FILE_PATH)
        if os.path.exists(COMMAND_PIPE_PATH):
            os.remove(COMMAND_PIPE_PATH)
