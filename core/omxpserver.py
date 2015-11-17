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

    def __init__(self):
        self.play_queue = []
        self.playing_status = 'pause'
        self.playing_media_path = ''
        self.omxp_process = None
        self.omxp_pipe = None
        self.command_queue = Queue.Queue()

    def pop_playlist(self):
        '''Pop next media path.'''
        return self.play_queue.pop(0)

    def add_playlist(self, playlist_path):
        '''Add medias in playlist.'''
        media_paths = []
        with open(playlist_path) as f:
            media_paths += [l.strip() for l in f.readlines()]
        self.play_queue.extend(media_paths)
        return media_paths

    def add_media(self, media_path):
        '''Add media'''
        self.play_queue.append(media_path)

    def is_playing(self):
        '''Check already running omxplayer.'''
        return (self.omxp_process != None and
                self.omxp_process.poll() == None)

    def pop_command(self):
        '''Pop command from command_queue with tuple.
           Return None if new available data is nothing.'''
        sock = None
        data = None
        try:
            sock, data = self.command_queue.get_nowait()
        except Queue.Empty:
            pass
        return sock, data

    def push_command(self, sock, data):
        self.command_queue.put((sock, data))

    def consume_command(self, send_res, data):
        command = data['command']
        res = "is_playing: {}\n".format(self.is_playing()) \
            + "status: {}\n".format(self.playing_status) \
            + "media_path: {}".format(self.playing_media_path)
        if command == 'status':
            pass
        elif command == 'stop':
            self.stop()
        elif command == 'pause':
            self.pause()
        elif command == 'omx':
            os.write(self.omxp_pipe, " ".join(data["args"]))
        elif command == 'add_media':
            valid_paths = [i for i in data['path'] if os.path.isfile(i)]
            valid_paths = [i.encode('utf-8') if isinstance(i, unicode) else i for i in valid_paths]
            for p in valid_paths:
                self.add_media(p)
            res = ''
            res = 'Add media:\n'
            res += "\n".join(valid_paths)
        elif command == 'add_playlist':
            valid_paths = [i for i in data['path'] if os.path.isfile(i)]
            valid_paths = [i.encode('utf-8') if isinstance(i, unicode) else i for i in valid_paths]
            add_medium = []
            for p in valid_paths:
                add_medium.extend(self.add_playlist(p))
            res = ''
            res = 'Add media:\n'
            res += "\n".join(add_medium)
        elif command == 'list_queue':
            res = "\n".join(self.play_queue)
        elif command == 'quit':
            send_res('See you')
            exit()
        else:
            os.write(self.omxp_pipe, command)
        send_res(res)

    def run(self):
        '''Start server.'''
        while True:
            if not self.is_playing() and len(self.play_queue) != 0:
                self.play(self.pop_playlist())

    def play(self, media_path):
        '''Play media with omxplayer.'''
        r, w = os.pipe()
        self.omxp_process = subprocess.Popen(
            ['/usr/bin/omxplayer', '-o', 'local', media_path]
            , stdin=r)
        self.omxp_pipe = w
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
