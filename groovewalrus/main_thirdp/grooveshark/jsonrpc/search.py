#!/usr/bin/python

from playlist import Playlist


def searchResults(gsapi, query):
    """function: Get search results playlist from query"""
    parameters = {
        "query": query,
        "type": "Songs"}

    response = gsapi.request(parameters, "getSearchResultsEx").send()

    return SearchResults(gsapi, query, response["result"])


class SearchResults(Playlist):
    """class: Represents Grooveshark Search Results"""

    def __init__(self, gsapi, query, songs):
        """function: Initiates SearchResults class"""
        self.query = query
        Playlist.__init__(self, gsapi, songs)
