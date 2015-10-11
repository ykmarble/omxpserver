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
        with open(playlist_path) as f:
            self.play_queue += [l.strip() for l in f.readlines()]

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

    def run(self):
        '''Start server.'''
        while True:
            if not self.is_playing() and len(self.play_queue) != 0:
                self.play(self.pop_playlist())
            sock, data = self.pop_command()
            if data == None:
                time.sleep(1)
                continue
            command = data['command']
            res = ""
            if command == 'status':
                res = "is_playing: {}\n".format(self.is_playing()) \
                    + "status: {}\n".format(self.playing_status) \
                    + "media_path: {}".format(self.playing_media_path)
            elif command == 'stop':
                self.stop()
                res = 'stop is awesome.'
            elif command == 'pause':
                self.pause()
                res = 'pause is awesome.'
            elif command == 'omx':
                os.write(self.omxp_pipe, " ".join(data["args"]))
            elif command == 'add_media':
                res = ''
                for p in data['path']:
                    self.add_media(p)
                res = 'Add media:\n'
                res += "\n".join(self.play_queue)
            elif command == 'add_playlist':
                for p in data['path']:
                    self.add_playlist(p)
                res = 'Add media:\n'
                res += "\n".join(self.play_queue)
            elif command == 'list_queue':
                res = "\n".join(self.play_queue)
            elif command == 'quit':
                res = 'See you'
                if sock == None:
                    print res
                else:
                    send_chunked_stream(sock, res)
                exit()
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
