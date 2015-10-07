#!/usr/bin/python2
# -*- coding: utf-8 -*-

import socket
import argparse
import json
import sys
from core.omxpsocket import SOCKET_PATH
from core.utils import recieve_chunked_stream, send_chunked_stream

cmd_dict = {"status": lambda args: len(args)==0,
            "omx": lambda args: True}
cmd_description = \
"""
command list
status: print status
omx: pass to omxplayer
"""

def send_cmd(dst, cmd, args):
    data = {}
    data["command"] = cmd
    data["args"] = args
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
    print send_cmd(args.socketpath, args.cmd, args.args)

if __name__ == '__main__':
    main()
