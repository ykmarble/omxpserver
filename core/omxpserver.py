#!/usr/bin/python2
# -*- coding: utf-8 -*-

import subprocess
import os
import threading


class OMXPSever(object):
    '''omxplayer with play queue.'''

    def __init__(self):
        self.play_queue = []
        self.playing_status = 'play'
        self.playing_media_path = ''
        self.omxp_process = None
        self.omxp_pipe = None
        self.destructer = lambda : None
        self.updating = threading.RLock()
        self.wake_run = threading.Event()

    def pop_playlist(self):
        '''Pop next media path.'''
        with self.updating:
            return self.play_queue.pop(0)

    def add_playlist(self, playlist_path):
        '''Add medias in playlist.'''
        media_paths = []
        with open(playlist_path) as f:
            media_paths += [l.strip() for l in f.readlines()]
        with self.updating:
            self.play_queue.extend(media_paths)
        return media_paths

    def add_media(self, media_path):
        '''Add media'''
        with self.updating:
            self.play_queue.append(media_path)

    def is_playing(self):
        '''Check already running omxplayer.'''
        return (self.omxp_process != None and
                self.omxp_process.poll() == None)

    def consume_command(self, send_res, data):
        command = data['command']
        res = ''
        if command == 'status':
            pass
        elif command == 'play':
            self.play()
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
            with self.updating:
                res = "\n".join(self.play_queue)
        elif command == 'quit':
            send_res('See you')
            self.stop()
            self.destructer()
        else:
            os.write(self.omxp_pipe, command)
        if res == '':
            with self.updating:
                res = "is_playing: {}\n".format(self.is_playing()) \
                    + "status: {}\n".format(self.playing_status) \
                    + "media_path: {}".format(self.playing_media_path)
        send_res(res)
        self.wake_run.set()

    def run(self):
        '''Start server.'''
        while self.wake_run.wait():
            self.updating.acquire()
            if self.is_playing():
                self.updating.release()
            elif len(self.play_queue) != 0 and self.playing_status != 'stop':
                p = self.pop_playlist()
                self.updating.release()
                self.play(p)
            else:
                self.updating.release()

    def play(self, media_path=None):
        '''Play media with omxplayer.'''
        if media_path is None:
            with self.updating:
                if self.playing_status == 'pause':
                    self.pause()
                else:
                    self.playing_status = 'play'
            return
        with self.updating:
            r, w = os.pipe()
            self.omxp_process = subprocess.Popen(
                ['/usr/bin/omxplayer', '-o', 'local', media_path]
                , stdin=r)
            self.omxp_pipe = w
            def watch():
                self.omxp_process.wait()
                os.close(r)
                os.close(w)
                self.wake_run.set()
            t = threading.Thread(target=watch)
            t.daemon = True
            self.playing_status = 'play'
            self.playing_media_path = media_path

    def stop(self):
        '''Kill omxplayer.'''
        with self.updating:
            if self.is_playing():
                os.write(self.omxp_pipe, "q")
            self.playing_status = 'stop'
            self.playing_media_path = ''
            self.omxp_process = None
            self.omxp_pipe = None

    def pause(self):
        '''Stop omxplayer, but omxplayer process will continue running.'''
        with self.updating:
            if not self.is_playing():
                return
            os.write(self.omxp_pipe, " ")
            if self.playing_status == 'play':
                self.playing_status = 'pause'
            else:
                self.playing_status == 'play'
