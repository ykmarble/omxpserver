#!/usr/bin/python2
# -*- coding: utf-8 -*-

import subprocess
import os
import time
import Queue
import socket
from utils import send_chunked_stream


class OMXPSever(object):
    '''omxplayer with play queue.'''

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
        '''Pop next media path.'''
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
        '''Set playlist from self.media_path'''
        with open(self.playlist_path) as f:
            self.playlist = [l.strip() for l in f.readlines()]

    def run(self):
        '''Start server.'''
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
                    sock, data = self.command_queue.get_nowait()
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
                    if sock == None:
                        print res
                    else:
                        try:
                            send_chunked_stream(sock, res)
                        except socket.error:
                            continue
                        sock.close()
                except Queue.Empty:
                    pass
                time.sleep(1)

    def play(self, media_path):
        '''Play media with omxplayer.'''
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
        '''Kill omxplayer.'''
        pass

    def pause(self):
        '''Stop omxplayer, but omxplayer process will continue running.'''
        pass

    def inc_volume(self, val=1):
        '''Increase volume.'''
        pass

    def dec_volume(self, val=1):
        '''Decrease volume'''
        pass
