#!/usr/bin/python2
# -*- coding: utf-8 -*-

import subprocess
import os
import time
import Queue
from utils import send_chunked_stream


class OMXPSever(object):
    def __init__(self, playlist_path):
        self.playlist_path = playlist_path
        self.playlist = []
        self.is_playing = False
        self.playing_status = 'pause'
        self.playing_media_path = ''
        self.omxp_process = None
        self.omxp_pipe = None
        self.command_queue = Queue.Queue()
        self.consume_list = True

    def pop_playlist(self):
        if self.consume_list:
            with open(self.playlist_path) as f:
                playlist = f.readlines()
            if len(playlist) == 0:
                return ''
            media_path = playlist.pop(0).strip()
            with open(self.playlist_path, 'w') as f:
                f.write("".join(playlist))
            return media_path
        if len(self.playlist) == 0:
            return ''
        return self.playlist.pop(0)

    def set_playlist(self):
        with open(self.playlist_path) as f:
            self.playlist = [l.strip() for l in f.readlines()]

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
                    socket, data = self.command_queue.get_nowait()
                    command = data["command"]
                    args = data["args"]
                    res = ""
                    if command == 'status':
                        res = "is_playing: {}\n".format(self.is_playing) \
                            + "status: {}\n".format(self.playing_status) \
                            + "media_path: {}".format(self.playing_media_path)
                    elif command == 'stop':
                        res = 'stop is awesome.'
                    elif command == 'pause':
                        res = 'pause is awesome.'
                    elif command == 'play':
                        res = 'play is awesome.'
                    elif command == 'omx':
                        os.write(self.omxp_pipe, " ".join(args))
                    else:
                        os.write(self.omxp_pipe, command)
                    if socket == None:
                        print res
                    else:
                        send_chunked_stream(socket, res)
                        socket.close()
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
            , stdin=r)
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
