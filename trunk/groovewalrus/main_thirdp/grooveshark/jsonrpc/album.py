#!/usr/bin/python

from playlist import Playlist

def albumFromID(gsapi, id, offset=0, song=None):
    """function: Make an album from an albumID"""
    try:
        verified = song.albumVerified
    except:
        verified = False

    parameters = {
        "offset": offset,
        "isVerified": verified,
        "albumID": id}

    response = gsapi.request(parameters, "albumGetSongs").send()

    return Album(gsapi, response["result"], song)

def albumFromSong(gsapi, song, offset=0):
    """function: Make an album from a song instance"""
    return albumFromID(gsapi, song.albumID, offset, song)


class Album(Playlist):
    """class: Respresent a Grooveshark album"""

    def __init__(self, gsapi, data, song=None):
        """function: Initiates the Album class"""
        self._gsapi = gsapi
        self._parseData(data)
        self._parseSong(song)
        Playlist.__init__(self, gsapi, data["songs"])

    id = None
    name = ""
    artistId = None
    artistName = ""
    artistVerified = False
    coverArt = None
    verified = False
    hasMore = False

    def _parseData(self, data):
        """function: Parse information from json data"""
        song = data["songs"][0]
        self.id = song["AlbumID"]
        self.name = song["AlbumName"]
        self.artistName = song["ArtistName"]
        self.artistID = song["ArtistID"]

        try:
            self.coverArt = song["CoverArtFilename"]
        except:
            pass
        try:
            self.hasMore = data["hasMore"]
        except:
            pass

    def _parseSong(self, song):
        """function: Get some aditional information from a song instance"""
        try:
            self.artistVerified = song.artistVerified
            self.verified = song.albumVerified
        except:
            pass
