#!/usr/bin/python

import urllib
import urllib2

def songFromData(gsapi, data):
    return Song(gsapi, data)

class Song:
    """class: Represents a Grooveshark song"""

    def __init__(self, gsapi, data):
        """function: Initiates the Song class"""
        self._gsapi = gsapi
        self._parseData(data)

    _lastStreamKey = None
    _lastStreamServer = None
    _lastStreamServerID = None

    def _parseData(self, data):
        """function: Parses raw track data from Grooveshark"""
        self.id = data["SongID"]
        self.name = data["Name"]
        self.artistName = data["ArtistName"]
        self.artistID = data["ArtistID"]
        self.albumName = data["AlbumName"]
        self.albumID = data["AlbumID"]
        self.verified = False
        try:
            if "1" == data["IsVerified"]:
                self.verified = True
        except:
            pass
        self.artistVerified = False
        self.albumVerified = False
        try:
            if "1" == data["ArtistVerified"]:
                self.artistVerified = True
        except:
            pass
        try:
            if "1" == data["AlbumVerified"]:
                self.albumVerified = True
        except:
            pass
        try:
            self.trackNum = int(data["TrackNum"])
        except:
            self.trackNum = None

        self.popularity = 0
        try:
            self.popularity = int(data["Popularity"])
        except:
            pass

    def markDownloaded(self):
        """function: Tells Grooveshark you have downloaded a song"""
        parameters = {
            "streamKey": self._lastStreamKey,
            "streamServerID": self._lastStreamServerID,
            "songID": self.id}
        self._gsapi.request(parameters, "markSongDownloaded").send()

    def mark30Seconds(self):
        """function: Tells Grooveshark song has played over 30 seconds"""
        parameters = {
            "streamKey": self._lastStreamKey,
            "streamServerID": self._lastStreamServerID,
            "songID": self.id,
            "songQueueSongID": 0,
            "songQueueID": 0}
        self._gsapi.request(parameters, "markStreamKeyOver30Seconds",
                "service").send()

    def getStreamDetails(self):
        """function: Gets a stream key and host to get song content"""
        parameters = {
            "songID": self.id,
            "prefetch": False, 
            "country": {"CC3":"0","CC2":"0","ID":"1","CC1":"0","CC4":"0"}}
        response = self._gsapi.request(parameters,
                "getStreamKeyFromSongIDEx").send()
        print response
        self._lastStreamKey = response["result"]["streamKey"]
        self._lastStreamServer = response["result"]["ip"]
        self._lastStreamServerID = response["result"]["streamServerID"]

    # Only sometimes works
    def getStreamURL(self):
        """function: Stream the song to a file"""
        self.getStreamDetails()
        postData = {
            "streamKey": self._lastStreamKey}
        postData = urllib.urlencode(postData)

        request = urllib2.Request("http://" + self._lastStreamServer +
                "/stream.php", postData)
        response = urllib2.urlopen(request)

        return response.geturl()

    def download(self, filename, reportHook=None):
        """function: Download a song to a file"""
        self.getStreamDetails()
        postData = {
            "streamKey": self._lastStreamKey}
        postData = urllib.urlencode(postData)

        urllib.FancyURLopener().retrieve( "http://" +
                self._lastStreamServer + "/stream.php",
                filename, reportHook, postData)
