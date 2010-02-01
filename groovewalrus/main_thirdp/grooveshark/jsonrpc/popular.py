#!/usr/bin/python

import playlist

def popular(gsapi, type="Songs"):
    """function: Create a playlist of popular songs"""
    parameters = {}

    response = gsapi.request(parameters, "popularGetSongs").send()

    return playlist.playlistFromData(gsapi, response["result"]["Songs"])
