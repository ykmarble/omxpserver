#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
from core.omxpsocket import SOCKET_PATH
from core.utils import send_cmd
import os
import urllib


DEBUG = True
MEDIA_ROOT = "/media/share/"

app = Flask(__name__)
pjoin = os.path.join


def validate_path(path, root=MEDIA_ROOT):
    """
    Check taken path is valid or not.
    """
    return path



@app.route("/contents/")
@app.route("/contents/<path:dirpath>/")
def show_content(dirpath=""):
    valid_path = validate_path(dirpath)
    if valid_path is None:
        return "Invalid Parameter."
    real_path = pjoin(MEDIA_ROOT, valid_path)
    dirs = os.listdir(real_path)
    itemlist = [{"href": pjoin("/", dirpath, item), "caption": item}
                for item in dirs if os.path.isfile(pjoin(real_path, item))]
    dirlist = [{"href": pjoin("/contents", dirpath, item), "caption": item}
               for item in dirs if os.path.isdir(pjoin(real_path, item))]
    return render_template("base.html", itemlist=itemlist, dirlist=dirlist)

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
    valid_path = validate_path(path)
    if valid_path is None:
        # TODO: Implement function handling error messages.
        return "Invalid Parameter."
    real_path = pjoin(MEDIA_ROOT, valid_path[1:])
    print real_path
    params = {}
    params["command"] = "add_media"
    params["path"] = [real_path]
    return send_cmd(SOCKET_PATH, params)


@app.route("/control/status")
def player_status():
    """
    Inquire status of omxpserver and return it.
    """
    params = {}
    params["command"] = "status"
    return send_cmd(SOCKET_PATH, params)


@app.route("/control/play", methods=["POST"])
def play():
    """
    Imediately play specified media in form of path.
    """
    if "path" not in request.form:
        return "Invalid Parameter."
    path = request.form["path"]
    valid_path = validate_path(path)
    if valid_path is None:
        return "Invalid Parameter."
    return "Not Implemented."
    params = {}
    params["command"] = "play"
    return ""


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
