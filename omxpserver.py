#!/usr/bin/python2
# -*- coding: utf-8 -*-

import subprocess
import json
import argparse
import os
import sys
import subprocess
import time
import threading
import curses
import Queue
import errno

ROOT_PATH = os.path.dirname(sys.argv[0])
PLAYLIST_PATH =  os.path.join(ROOT_PATH, 'playlist')
PID_FILE_PATH = os.path.join(ROOT_PATH, 'omxpserver.pid')
COMMAND_PIPE_PATH = os.path.join(ROOT_PATH, 'omxpserver-pipe')
OMXP_PATH = '/usr/bin/omxplayer'
OMXP_OPT = '-o local'

class OMXPSever(object):
    def __init__(self, playlist_path):
        self.playlist_path = playlist_path
        self.is_playing = False
        self.playing_status = 'pause'
        self.playing_media_path = ''
        self.omxp_process = None
        self.omxp_pipe = None
        self.command_queue = Queue.Queue()

    def pop_playlist(self):
        with open(self.playlist_path) as f:
            playlist = f.readlines()
        if len(playlist) == 0:
            return ''
        media_path = playlist.pop(0).strip()
        with open(self.playlist_path, 'w') as f:
            f.write("".join(playlist))
        return media_path

    def run(self):
        if self.is_playing:
            self.stop()
        while True:
            next = self.pop_playlist()
            if next == '':
                time.sleep(5)
                continue
            self.play(next)
            while self.omxp_process.poll() == None:
                try:
                    command = self.command_queue.get_nowait()
                    if command == 'status':
                        print "is_playing: {}".format(self.is_playing)
                        print "status: {}".format(self.playing_status)
                        print "media_path: {}".format(self.playing_media_path)
                    elif command == 'stop':
                        print 'stop is awesome.'
                    elif command == 'pause':
                        print 'pause is awesome.'
                    elif command == 'play':
                        print 'play is awesome.'
                    else:
                        os.write(self.omxp_pipe, command)
                except Queue.Empty:
                    pass
                time.sleep(1)

    def play(self, media_path):
        if subprocess.call(['pgrep', 'omxplayer']) == 0:
            print 'omxplayer is already running.'
            return
        r, w = os.pipe()
        self.omxp_process = subprocess.Popen(
            ['/usr/bin/omxplayer', '-o', 'local', media_path]
            ,stdin=r)
        self.omxp_pipe = w
        self.is_playing = True
        self.playing_status = 'play'
        self.playing_media_path = media_path
        return

    def stop(self):
        pass

    def pause(self):
        pass

    def inc_volume(self):
        pass

    def dec_volume(self):
        pass


def main():
    parser = argparse.ArgumentParser(description='omxplayer frontend with queue.')
    parser.add_argument('-p', '--path', default=PLAYLIST_PATH)
    parser.add_argument('-v', '--verbose', action='store_true')
    arg = parser.parse_args()
    if  (os.path.exists(arg.path) and not os.path.isfile(arg.path)):
        print '{} is not file.'.format(arg.path)
        return

    # check already omxpserver or omxp is running
    if (os.path.exists(PID_FILE_PATH)):
        print 'omxpserver is already running.'
        return

    with open(PID_FILE_PATH, 'w') as f:
        f.write(str(os.getpid()))

    server = OMXPSever(arg.path)
    frontend_stdin = threading.Thread(target=lambda : stdin_reader(server.command_queue))
    frontend_stdin.daemon = True
    frontend_stdin.start()
    frontend_pipe = threading.Thread(target=lambda : command_reader(server.command_queue))
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
