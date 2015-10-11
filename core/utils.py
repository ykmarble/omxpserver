#!/usr/bin/python2
# -*- coding: utf-8 -*-

class CommunicationError(StandardError):
    pass

def recieve_chunked_stream(socket):
    length = 0
    while True:
        buf = socket.recv(1)
        if buf == '\0':
            break
        try:
            length = length *10 + int(buf)
        except ValueError:
            raise CommunicationError("Recieved invalied data"
                                     + " buf={}".format(buf)
                                     + " length={}".format(length))
    res = ""
    while len(res) < length:
        res += socket.recv(length - len(res))
    return res

def send_chunked_stream(socket, data):
    length = len(data)
    socket.send(str(length))
    socket.send('\0')
    socket.send(data)
    return
