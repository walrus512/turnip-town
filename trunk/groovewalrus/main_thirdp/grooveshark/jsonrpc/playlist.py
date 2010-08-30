#!/usr/bin/python

import song as gssong

def playlistFromData(gsapi, data):
    """function: Create a playlist from song list data"""
    return Playlist(gsapi, data)
    
def playlistFromId(gsapi, id_list):
    """ Javi S. 2010/08/29 """
    parameters = {"playlistID":id_list}
    response = gsapi.request(parameters, "playlistGetSongs").send()
    return Playlist(gsapi, response["result"]["Songs"])

class Playlist:
    """class: Base class for items with multiple songs"""

    def __init__(self, gsapi, songs):
        """function: Initiates the Playlist class"""
        self._gsapi = gsapi
        self.songs = self._parseSongs(songs)

    songs = []

    def _parseSongs(self, songs):
        """function: Parses a song list into a list of songs"""
        list = []
        for song in songs:
            list.append(gssong.songFromData(self._gsapi, song))

        return list
