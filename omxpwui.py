#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
from core.omxpsocket import SOCKET_PATH
from core.utils import send_cmd
import os
import urllib


DEBUG = True
MEDIA_ROOT = "/media/share/exports"

app = Flask(__name__)
pjoin = os.path.join


def is_valid_path(fake_path, root=MEDIA_ROOT):
    """
    Check taken path is valid or not.
    """
    norm_path = os.path.normpath(fake_path)
    return norm_path.startswith("/")


def build_real_path(fake_path, root=MEDIA_ROOT):
    """
    Convert fake_path to real path.
    fake_path means path of fake root, or virtual contents tree.
    real path means actualy to be passed to filesystem.
    """
    return os.path.join(root, fake_path[1:])


def is_valid_media(real_path):
    """
    Check the file indecated by path is supported or not.
    """
    exts = ["mp3", "wav", "aac", "m4a", "m2ts", "ts", "mp4"]
    return real_path.split(".")[-1] in exts


@app.route("/contents/")
@app.route("/contents/<path:dirpath>/")
def show_content(dirpath=""):
    """
    Endpoint that displays contents tree.
    dirpath will be only used in contents tree.
    """
    fake_path = "/" + dirpath
    if not is_valid_path(fake_path):
        return "Invalid Parameter."
    real_path = build_real_path(fake_path)
    dirs = sorted(os.listdir(real_path))
    if dirpath != "":
        dirs = ["../"] + dirs
    itemlist = []
    dirlist = []
    for item in dirs:
        item_fake_path = pjoin(fake_path, item)
        item_real_path = build_real_path(item_fake_path)
        if os.path.isdir(item_real_path):
            dirlist.append({"href": "/contents"+item_fake_path, "caption": item})
        elif is_valid_media(item_real_path):
            itemlist.append({"href": item_fake_path, "caption": item})
    return render_template("base.html", title=fake_path,
                           itemlist=itemlist, dirlist=dirlist)


@app.route("/queue/list")
def list_queue():
    """
    Inquire items in queue to omxpserver.
    And return them.
    """
    params = {}
    params["command"] = "list_queue"
    return send_cmd(SOCKET_PATH, params)


@app.route("/queue/add", methods=["POST"])
def enqueue():
    """
    Add item to queue in omxpserver.
    """
    if "path" not in request.form:
        # TODO: Implement function handling error messages.
        return "Invalid Parameter."
    path = request.form["path"]
    if not is_valid_path(path):
        # TODO: Implement function handling error messages.
        return "Invalid Parameter."
    real_path = build_real_path(path)
    params = {}
    params["command"] = "add_media"
    params["path"] = [real_path]
    res = send_cmd(SOCKET_PATH, params)
    return res


@app.route("/control/status")
def player_status():
    """
    Inquire status of omxpserver and return it.
    """
    params = {}
    params["command"] = "status"
    return send_cmd(SOCKET_PATH, params)


@app.route("/control/play")
def play():
    """
    Start to play.
    """
    params = {}
    params["command"] = "play"
    return send_cmd(SOCKET_PATH, params)


@app.route("/control/stop")
def stop():
    """
    Stop playing media, corresponding the same method of omxpserver.
    """
    params = {}
    params["command"] = "stop"
    return send_cmd(SOCKET_PATH, params)


@app.route("/control/pause", methods=["GET", "POST"])
def pause():
    """
    Pause playing media, corresponding the same method of omxpserver.
    If requested method is http GET, toggle playing or pausing.
    And http POST can specifies play or pause.
    """
    if request.method == "GET":
        params = {}
        params["command"] = "pause"
        return send_cmd(SOCKET_PATH, params)
    return "Not Implemented."


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=DEBUG)
