"""
GrooveWalrus: Album Tab
Copyright (C) 2010
11y3y3y3y43@gmail.com
gardener@turnip-town.net
http://groove-walrus.turnip-town.net
-----
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""
import wx
import wx.xrc as xrc
#import sqlite3
#import os
#from main_controls import ratings_button
#from main_utils import system_files
#from main_utils import local_songs

# notebook pages
NB_PLAYLIST = 0
NB_LAST = 1
NB_MYLAST = 2
NB_ALBUM = 3
NB_BIO = 4
NB_COLLECTION = 5
NB_FAVES = 6
NB_SIFT = 7
NB_OPTIONS = 8
NB_ABOUT = 9
WN_SEARCH = 99

class AlbumTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent

        # controls
        ##self.st_album_get_tracks = xrc.XRCCTRL(self, 'm_st_album_get_tracks')
        self.tc_album_search_artist = xrc.XRCCTRL(self.parent, 'm_tc_album_search_artist')
        self.tc_album_search_song = xrc.XRCCTRL(self.parent, 'm_tc_album_search_song')
        self.tc_album_search_album = xrc.XRCCTRL(self.parent, 'm_tc_album_search_album')
        self.bm_cover_large = xrc.XRCCTRL(self.parent, 'm_bm_cover_large')
        
        # album list control -------------
        self.lc_album = xrc.XRCCTRL(self.parent, 'm_lc_album')
        self.lc_album.InsertColumn(0,"Artist")
        self.lc_album.InsertColumn(1,"Song")
        self.lc_album.InsertColumn(2,"Album")
        #self.lc_album.InsertColumn(3,"Id")
        self.parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAlbumListClick, self.lc_album)
        self.parent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnAlbumDoubleClick, self.lc_album)
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnAlbumRightClick, self.lc_album)
        # wxGTK
        self.lc_album.Bind(wx.EVT_RIGHT_UP, self.OnAlbumRightClick)
        self.lc_album.Bind(wx.EVT_CHAR, self.parent.OnChar)
        
        #bindings ----------------
        self.parent.Bind(wx.EVT_BUTTON, self.OnAlbumGetTracks, id=xrc.XRCID('m_bu_album_tracks'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnClearAlbumSearchClick, id=xrc.XRCID('m_bb_album_clear_search'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnAlbumSearchClick, id=xrc.XRCID('m_bb_album_search'))
        self.bm_cover_large.Bind(wx.EVT_LEFT_UP, self.parent.OnAlbumCoverClick)
        self.parent.Bind(wx.EVT_BUTTON, self.OnAutoGenerateAlbumPlayist, id=xrc.XRCID('m_bu_album_plize'))
        
# --------------------------------------------------------- 
# album page ----------------------------------------------  
         
    def OnClearAlbumSearchClick(self, event):
        # clear album search field
        self.tc_album_search_artist.Clear()
        self.tc_album_search_song.Clear()
        self.tc_album_search_album.Clear()
        
    def OnAlbumSearchClick(self, event):
        # search field, then search
        artist = self.tc_album_search_artist.GetValue()
        song = self.tc_album_search_song.GetValue()
        album = self.tc_album_search_album.GetValue()
        
        #find album based on artist and song
        # or find album based on artist and album
        if (len(artist) != 0) & (len(album) != 0):
            track_stuff = self.parent.GetAlbumAlbumInfo(artist, album)            
            self.tc_album_search_album.SetValue(track_stuff[1])
            self.tc_album_search_artist.SetValue(artist)
            if len(track_stuff) > 0:
                track_list = self.parent.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.FillAlbumList(track_list, artist, track_stuff[1])
        elif (len(artist) != 0) & (len(song) != 0) & (len(album) == 0):            
            track_stuff = self.parent.GetSongAlbumInfo(artist, song)
            self.tc_album_search_album.SetValue(track_stuff[1])
            self.tc_album_search_artist.SetValue(artist)
            if len(track_stuff) > 0:
                track_list = self.parent.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.FillAlbumList(track_list, artist, track_stuff[1])
        elif (len(artist) != 0) & (len(song) == 0) & (len(album) == 0):
            # change to last.fm and display albums for artist
            self.parent.tc_last_search_artist.SetValue(artist)
            self.parent.OnLastTAArtistClick(None)
            self.parent.nb_main.SetSelection(NB_LAST)
        else:            
            dlg = wx.MessageDialog(self.parent, 'Artist or Artist/Song or Artist/Album not entered.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnAlbumListClick(self, event):
        # past the artist + track in the search field
        val = self.lc_album.GetFirstSelected()
        artist = self.lc_album.GetItem(val, 0).GetText()
        song = self.lc_album.GetItem(val, 1).GetText()
        #clear
        #self.tc_search.SetValue('')
        #set new value
        self.parent.tc_search.SetValue(artist + ' ' + song)        
        
    def OnAlbumDoubleClick(self, event):
        # past the artist + track in the search field
        val = self.lc_album.GetFirstSelected()
        artist = self.lc_album.GetItem(val, 0).GetText()
        song = self.lc_album.GetItem(val, 1).GetText()
        #search for selected song
        #self.SearchIt(artist + ' ' + song)
        self.parent.SearchOrPlaylist(artist, song)
        # display search page
        #self.nb_main.SetSelection(NB_PLAYLIST)
        #self.lc_search.SetFocus()
        #self.lc_search.Select(0)
        
    def OnAlbumGetTracks(self, event):
        # get album info from musicbrainz        
        #self.nb_main.SetSelection(NB_ALBUM)
        track_list = []
        # just get the current track playing, use artist/song to get album info
        
        artist = self.parent.current_song.artist
        song = self.parent.current_song.song
        self.tc_album_search_artist.SetValue(artist)
        self.tc_album_search_song.SetValue(song)
        
        if len(artist) > 0:
            #print 'boo'
            track_stuff = self.parent.GetSongAlbumInfo(artist, song)
            #print track_stuff
            self.tc_album_search_album.SetValue(track_stuff[1])
            if len(track_stuff) > 0:
                track_list = self.parent.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.FillAlbumList(track_list, artist, track_stuff[1])        
                
    def FillAlbumList(self, track_list, artist, album):
        # fill list        
        self.lc_album.DeleteAllItems()
        counter = 0;
        for x in track_list:
            if x[1] != '':
                artist = x[1]
            self.lc_album.InsertStringItem(counter, artist)
            self.lc_album.SetStringItem(counter, 1, x[0])
            self.lc_album.SetStringItem(counter, 2, album)
            self.lc_album.SetStringItem(counter, 3, '')            
            counter = counter + 1
               
        self.lc_album.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lc_album.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.lc_album.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        #self.lc_lastfm.SetColumnWidth(3, wx.LIST_AUTOSIZE)
           
    def OnAutoGenerateAlbumPlayist(self, event):
        # lets just add all the items to your playlist
        # search for song from groove shark on demand, ie, when you go to play it?
        # *** merge this the lastfm auto generate which does the same thing
        self.parent.CheckClear()
        insert_at = self.parent.lc_playlist.GetItemCount()
        for x in range(self.lc_album.GetItemCount(), 0, -1):
            artist = self.lc_album.GetItem(x-1, 0).GetText()
            song = self.lc_album.GetItem(x-1, 1).GetText()
            album = self.lc_album.GetItem(x-1, 2).GetText()
            self.parent.SetPlaylistItem(insert_at, artist, song, album)
        #save the playlist
        self.parent.SavePlaylist(self.parent.main_playlist_location)
        # switch tabs
        self.parent.nb_main.SetSelection(NB_PLAYLIST) 
        
    def OnAlbumRightClick(self, event):
        val = self.lc_album.GetFirstSelected()
        if val != -1:
            if (self.lc_album.GetItem(val, 0).GetText() != '') & (self.lc_album.GetItem(val, 1).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 1
                ID_CLEAR = 2
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")
                menu.AppendSeparator()
                menu.Append(ID_CLEAR, "Clear Playlist")
                wx.EVT_MENU(self.parent, ID_PLAYLIST, self.AlbumAddPlaylist)
                wx.EVT_MENU(self.parent, ID_CLEAR, self.parent.OnClearPlaylistClick)       
                self.parent.PopupMenu(menu)
                menu.Destroy()
                
    def AlbumAddPlaylist(self, event):    
        self.parent.GenericAddToPlaylist(self.lc_album, add_album=True)