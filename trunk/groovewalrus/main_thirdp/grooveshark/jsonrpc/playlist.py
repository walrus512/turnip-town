#!/usr/bin/python

import song as gssong

def playlistFromData(gsapi, data):
    """function: Create a playlist from song list data"""
    return Playlist(gsapi, data)

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
