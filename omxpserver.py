#!/usr/bin/python2
# -*- coding: utf-8 -*-

import subprocess
import json
import argparse
import os
import sys
import subprocess

ROOT_PATH = os.path.dirname(sys.argv[0])
PLAYLIST_PATH =  os.path.join(ROOT_PATH, 'playlist')
PID_FILE_PATH = os.path.join(ROOT_PATH, 'omxpserver.pid')
OMXP_PATH = '/usr/bin/omxplayer'
OMXP_OPT = '-o local'

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
    if subprocess.call(['pgrep', 'omxplayer']):
        print 'omxplayer is already running.'
        return

    with open(PID_FILE_PATH, 'w') as f:
        f.write(str(os.getpid()))

    while True:
        media_path = ''
        with open(arg.path, 'r') as f:
            playlist = f.readlines()
        if len(playlist) == 0:
            print 'Bye'
            return
        media_path = playlist.pop().strip()
        with open(arg.path, 'w') as f:
            f.write("".join(playlist))

        p = subprocess.Popen(['/usr/bin/omxplayer', '-o', 'local', media_path])
        p.wait()


if __name__ == '__main__':
    try:
        main()
    finally:
        os.remove(PID_FILE_PATH)
