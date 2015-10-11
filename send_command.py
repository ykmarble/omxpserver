#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import os.path
import socket
import argparse
import json
import sys
from core.omxpsocket import SOCKET_PATH
from core.utils import recieve_chunked_stream, send_chunked_stream

cmd_dict = {"status": lambda args: len(args)==0,
            "omx": lambda args: True,
            "add_media": lambda args: True,
            "add_playlist": lambda args: True,
            "list_queue": lambda args: True,
            "quit": lambda args: True}
cmd_description = \
"""
command list
status: print status
omx: pass to omxplayer
"""

def send_cmd(dst, data):
    data_json = json.dumps(data)
    soc = socket.socket(socket.AF_UNIX)
    soc.connect(dst)
    send_chunked_stream(soc, data_json)
    res = recieve_chunked_stream(soc)
    soc.close()
    return res

def main():
    parser = argparse.ArgumentParser(epilog=cmd_description)
    parser.add_argument("-s", "--socketpath", default=SOCKET_PATH)
    parser.add_argument("cmd")
    parser.add_argument("args", nargs='*')
    args = parser.parse_args()
    if not args.cmd in cmd_dict.keys():
        print "{} is not command.".format(args.cmd)
        parser.print_help()
        return
    if not cmd_dict[args.cmd](args.args):
        print "invalid argument"
        parser.print_help()
        return
    data = {}
    data["command"] = args.cmd
    if args.cmd == "omx":
        data["args"] = args.args
    elif args.cmd == "add_playlist":
        data["path"] = []
        for a in args.args:
            if a[0] == '/':
                data['path'].append(a)
            else:
                data["path"].append(os.path.join(os.getcwd(), a))
    elif args.cmd == 'add_media':
        data["path"] = []
        for a in args.args:
            if a[0] == '/':
                data['path'].append(a)
            else:
                data["path"].append(os.path.join(os.getcwd(), a))
    elif args.cmd == 'list_queue':
        pass
    print send_cmd(args.socketpath, data)

if __name__ == '__main__':
    main()
