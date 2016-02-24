#!/usr/bin/python2
# -*- coding: utf-8 -*-

import json
import socket


class CommunicationError(StandardError):
    pass


def recieve_chunked_stream(sock):
    """
    Recieve data like http chuncked stream from sock.
    This function returns raw string.
    """
    length = 0
    while True:
        buf = sock.recv(1)
        if buf == '\0':
            break
        try:
            length = length * 10 + int(buf)
        except ValueError:
            raise CommunicationError("Recieved invalied data"
                                     + " buf={}".format(buf)
                                     + " length={}".format(length))
    res = ""
    while len(res) < length:
        res += sock.recv(length - len(res))
    return res


def send_chunked_stream(sock, data):
    """
    Send data like http chuncked stream to sock.
    This function treats @data parameter as raw string.
    """
    if isinstance(data, unicode):
        data = data.encode('utf-8', 'ignore')
    length = len(data)
    sock.send(str(length))
    sock.send('\0')
    sock.send(data)
    return


def send_cmd(dst, data):
    """
    Send command over omxpsocket.
    @dst: destination, end point of omxpserver socket
    @data: dict-like data, which will be convert to json.
    """
    data_json = json.dumps(data)
    sock = socket.socket(socket.AF_UNIX)
    sock.connect(dst)
    send_chunked_stream(sock, data_json)
    res = recieve_chunked_stream(sock)
    sock.close()
    return res
