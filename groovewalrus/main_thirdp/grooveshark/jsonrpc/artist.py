#!/usr/bin/python

from playlist import Playlist

def artistFromID(gsapi, id, offset=0, item=None):
    """function: Make an artist from an artistID"""
    try:
        verified = item.artistVerified
    except:
        verified = False

    parameters = {
        "offset": offset,
        "isVerified": verified,
        "artistID": id}

    response = gsapi.request(parameters, "artistGetSongs").send()

    return Artist(gsapi, response["result"], item)

def artistFromItem(gsapi, item, offset=0):
    """function: Make an artist from a song instance"""
    return artistFromID(gsapi, item.artistID, offset, item)


class Artist(Playlist):
    """class: Respresent a Grooveshark artist"""

    def __init__(self, gsapi, data, item=None):
        """function: Initiates the Artist class"""
        self._gsapi = gsapi
        self._parseItem(item)
        self._parseData(data["Result"])
        Playlist.__init__(self, gsapi, data["Result"]["songs"])

    id = None
    name = ""
    verified = False
    hasMore = False

    def _parseData(self, data):
        """function: Parse information from json data"""
        song = data["songs"][0]
        self.id = song["ArtistID"]
        self.name = song["ArtistName"]
        try:
            if None == self.verified and "1" == song["ArtistVerified"]:
                self.verified = True
        except:
            pass

        try:
            self.hasMore = data["hasMore"]
        except:
            pass

    def _parseItem(self, item):
        """function: Get aditional information from a song or album"""
        try:
            self.verified = item.artistVerified
        except:
            pass
