"""
GrooveWalrus: Last.fm Tab
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
#from main_utils import audioscrobbler_lite
from threading import Thread
from main_thirdp import pylast

#columns
C_RATING = 0
C_ARTIST = 1
C_SONG = 2
C_ALBUM = 3
C_ID = 4
C_TIME = 5

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
API_KEY = "13eceb51a4c2e0f825c492f04bf693c8"

EVT_NEW_LAST = wx.PyEventBinder(wx.NewEventType(), 0)

class LastEvent(wx.PyCommandEvent):
    def __init__(self, eventType=EVT_NEW_LAST.evtType[0], id=0):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self.data = None

class LastfmTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent

        # controls ---------------------------
        self.st_last_ts_artist = xrc.XRCCTRL(self.parent, 'm_st_last_ts_artist')
        self.st_last_ta_artist = xrc.XRCCTRL(self.parent, 'm_st_last_ta_artist')
        self.st_last_ts_geo = xrc.XRCCTRL(self.parent, 'm_st_last_ts_geo')
        self.st_last_ts_genre = xrc.XRCCTRL(self.parent, 'm_st_last_ts_genre')
        self.st_last_ts_album = xrc.XRCCTRL(self.parent, 'm_st_last_ts_album')
        self.st_last_ts_similar = xrc.XRCCTRL(self.parent, 'm_st_last_ts_similar')
        self.st_last_art_similar = xrc.XRCCTRL(self.parent, 'm_st_last_art_similar')
        self.st_last_tt_song = xrc.XRCCTRL(self.parent, 'm_st_last_tt_song')
        
        self.tc_last_search_album = xrc.XRCCTRL(self.parent, 'm_tc_last_search_album')
        self.tc_last_search_artist = xrc.XRCCTRL(self.parent, 'm_tc_last_search_artist')
        self.tc_last_search_song = xrc.XRCCTRL(self.parent, 'm_tc_last_search_song')
        self.ch_last_country = xrc.XRCCTRL(self.parent, 'm_ch_last_country')
        self.co_last_tag = xrc.XRCCTRL(self.parent, 'm_co_last_tag')
        self.ch_last_page = xrc.XRCCTRL(self.parent, 'm_ch_last_page')
        
        # last.fm list control ----------------
        self.lc_lastfm = xrc.XRCCTRL(self.parent, 'm_lc_lastfm')
        self.lc_lastfm.InsertColumn(0,"Rating")
        self.lc_lastfm.InsertColumn(1,"Artist")
        self.lc_lastfm.InsertColumn(2,"Song")
        self.lc_lastfm.InsertColumn(3,"Album")
        self.lc_lastfm.InsertColumn(4,"Match")
        self.lc_lastfm.InsertColumn(5,"Tag")
        self.lc_lastfm.InsertColumn(6,"Count")
        
        self.parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLastfmListClick, self.lc_lastfm)
        self.parent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnLastfmListDoubleClick, self.lc_lastfm)
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnLastfmRightClick, self.lc_lastfm)
        # wxGTK
        self.lc_lastfm.Bind(wx.EVT_RIGHT_UP, self.OnLastfmRightClick)
        self.lc_lastfm.Bind(wx.EVT_CHAR, self.parent.OnChar)
        
        #bindings ------------------
        self.st_last_ts_artist.Bind(wx.EVT_LEFT_UP, self.OnLastTSArtistClick)
        self.st_last_ta_artist.Bind(wx.EVT_LEFT_UP, self.OnLastTAArtistClick)
        self.st_last_ts_geo.Bind(wx.EVT_LEFT_UP, self.OnLastTSGeoClick)
        self.st_last_ts_genre.Bind(wx.EVT_LEFT_UP, self.OnLastTSGenreClick)
        ##self.st_last_ts_album.Bind(wx.EVT_LEFT_UP, self.OnLastTSAlbumClick)
        self.st_last_ts_similar.Bind(wx.EVT_LEFT_UP, self.OnLastTSSimilarClick)
        self.st_last_art_similar.Bind(wx.EVT_LEFT_UP, self.OnLastArtistSimilarClick)
        self.st_last_tt_song.Bind(wx.EVT_LEFT_UP, self.OnLastTTSongClick)
        self.parent.Bind(wx.EVT_BUTTON, self.OnClearLastSearchClick, id=xrc.XRCID('m_bb_last_clear_search'))
        self.parent.Bind(wx.EVT_BUTTON, self.LastfmAddPlaylist, id=xrc.XRCID('m_bb_last_add'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnAutoGenerateLastfmPlayist, id=xrc.XRCID('m_bb_last_plize'))
        self.parent.Bind(wx.EVT_CHOICE, self.OnPageSelect, self.ch_last_page)
      
        self.parent.Bind(EVT_NEW_LAST, self.GenerateScrobbList)  
        
        self.current_page = 0
        self.total_pages = 0
        self.get_type = ""     
        
# --------------------------------------------------------- 
# last.fm ------------------------------------------------- 

    def GetLastThree(self):
        # figure out where we should get the artist/song/ablum info to search on
        artist = self.tc_last_search_artist.GetValue()        
        if len(artist) == 0:
            artist = self.parent.current_song.artist
            
        song = self.tc_last_search_song.GetValue()        
        if len(song) == 0:
            song = self.parent.current_song.song
            
        album = self.tc_last_search_album.GetValue()
        if len(album) == 0:
            album = self.parent.current_song.album

        return artist, song, album
        
    def LastThread(self, last_query, page=1):
        last_thread = GetLFThread(self, page)
        last_thread.SetType(last_query)
        self.ShowLoading()
        last_thread.start()

    def OnClearLastSearchClick(self, event):
        # clear lastfm search field
        self.tc_last_search_artist.Clear()
        self.tc_last_search_album.Clear()
        self.tc_last_search_song.Clear()
        
    def OnPageSelect(self, event):
        # get result page
        page = int(event.GetString())
        if self.get_type != '':
            self.LastThread(self.get_type, page)
        
    def SetPageChoices(self, page_total):
        # set the number of results pages
        self.ch_last_page.Clear()
        for x in range(int(page_total)):
            self.ch_last_page.Append(str(x+1))
        self.ch_last_page.SetSelection(self.current_page - 1)        

    def OnLastfmListClick(self, event):
        # past the artist + track in the search field
        val = self.lc_lastfm.GetFirstSelected()
        artist = self.lc_lastfm.GetItem(val, 1).GetText()
        song = self.lc_lastfm.GetItem(val, 2).GetText()
        album = self.lc_lastfm.GetItem(val, 3).GetText()
        tag = self.lc_lastfm.GetItem(val, 5).GetText()
        #set new value        
        self.tc_last_search_artist.SetValue(artist)
        self.tc_last_search_song.SetValue(song)
        self.tc_last_search_album.SetValue(album)
        self.co_last_tag.SetValue(tag)
    
    def OnLastTSSimilarClick(self, event):
        # grab similar tracks from last fm
        self.artist, self.song, self.album = self.GetLastThree()
        page = 1
        
        if len(self.song) > 0:                        
            self.LastThread('similar_track', page)
            self.get_type = 'similar_track'
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_similar_song_list(artist, song)
            #self.GenerateScrobbList(top_tracks_list)
        else:    
            dlg = wx.MessageDialog(self.parent, 'Song not entered / playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastArtistSimilarClick(self, event):
        # grab similar tracks from last fm
        # get artist from artist search box, if blank get from current playing song
        self.artist, self.song, self.album = self.GetLastThree()        
        if len(self.artist) > 0:
            self.LastThread('similar_artist')
            self.get_type = 'similar_artist'
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_similar_artist_list(artist)
            #print top_tracks_list
            #self.GenerateScrobbList(top_tracks_list, False, True)
        else:    
            dlg = wx.MessageDialog(self.parent, 'Artist not entered / song not playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    ##def OnLastTSAlbumClick(self, event):
        # get top tracks for a given album
        #$$$$ not threaded
    ##    self.artist, self.song, self.album = self.GetLastThree()
        #if (self.album == '') & (len(self.song) > 0):
            # check for album of playing song
            #track_stuff = self.parent.GetSongAlbumInfo(self.artist, self.song)
            #self.album = track_stuff[1]        
        # get album id
        # get top tracks
   ##     if len(self.album) > 0:
    ##        self.LastThread('top_tracks_album')
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_album_top_song_list(artist, album)
            #self.parent.TTA(top_tracks_list)
            #self.GenerateScrobbList(top_tracks_list, False, False)
    ##    else:
    ##        dlg = wx.MessageDialog(self.parent, 'Artist not entered / album not entered.', 'Problems...', wx.OK | wx.ICON_WARNING)
     ##       dlg.ShowModal()
     ##       dlg.Destroy()
        
    def OnLastTSArtistClick(self, event):
        # grab top tracks from last fm
        self.artist, self.song, self.album = self.GetLastThree()
        if len(self.artist) > 0:
            self.LastThread('top_artist')
            self.get_type = 'top_artist'
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_song_list(artist)
            #self.GenerateScrobbList(top_tracks_list)
        else:    
            dlg = wx.MessageDialog(self.parent, 'Artist not entered / song not playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastTAArtistClick(self, event):
        # grab top albums from last fm
        self.artist, self.song, self.album = self.GetLastThree()
        if len(self.artist) > 0:
            self.LastThread('top_albums')
            self.get_type = 'top_albums'
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_album_list(artist)
            #self.GenerateScrobbList(top_tracks_list, True)
        else:    
            dlg = wx.MessageDialog(self.parent, 'Artist not entered / song not playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastTSGeoClick(self, event):
        # grab top tracks from last fm per country
        self.country = self.ch_last_country.GetStringSelection()
        if len(self.country) > 0:
            self.LastThread('country')
            self.get_type = 'country'
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_geo_top_song_list(country)
            #self.GenerateScrobbList(top_tracks_list)        
        
    def OnLastTSGenreClick(self, event):
        # grab top tracks from last fm per country
        self.genre = self.co_last_tag.GetValue() #(0)#Selection()
        if len(self.genre) > 0:
            self.LastThread('genre')
            self.get_type = 'genre'
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_genre_top_song_list(genre)
            #self.GenerateScrobbList(top_tracks_list)
        
    def OnLastTTSongClick(self, event):
        # grab top tags per song
        self.artist, self.song, self.album = self.GetLastThree()

        if len(self.song) > 0:
            self.LastThread('song_tags')
            self.get_type = 'song_tags'
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_song_top_tags_list(artist, song)
            #self.GenerateScrobbList(top_tracks_list, False, False, True)
        else:    
            dlg = wx.MessageDialog(self.parent, 'Song not entered / playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()

    def GenerateScrobbList(self, event): #top_list, albums=False, artists=False, tags=False):
        self.ShowLoading(False)
        top_list = event.data[0]
        self.current_page = event.data[1]
        self.total_pages = event.data[2]
        columns = event.data[3]
        self.SetPageChoices(self.total_pages)
        # put some data in a list control
        counter = 0
        self.lc_lastfm.DeleteAllItems()
        
        for x in top_list:
            #if len(x) == 3:            
                # just printing artist/album
            self.lc_lastfm.InsertStringItem(counter, '')
            self.lc_lastfm.SetStringItem(counter, 1, '')
            if 'artist' in columns:
                self.lc_lastfm.SetStringItem(counter, 1, x[0])
            self.lc_lastfm.SetStringItem(counter, 2, '')
            if 'song' in columns:
                self.lc_lastfm.SetStringItem(counter, 2, x[1])
            self.lc_lastfm.SetStringItem(counter, 3, '')
            if 'album' in columns:
                self.lc_lastfm.SetStringItem(counter, 3, x[1]) 
            self.lc_lastfm.SetStringItem(counter, 4, '')
            if 'match' in columns:
                if len(x) == 3:
                    self.lc_lastfm.SetStringItem(counter, 4, x[2])
                else:
                    self.lc_lastfm.SetStringItem(counter, 4, x[1])
            self.lc_lastfm.SetStringItem(counter, 5, '')
            if 'tag' in columns:
                self.lc_lastfm.SetStringItem(counter, 5, x[0]) 
            self.lc_lastfm.SetStringItem(counter, 6, '')
            if 'count' in columns:
                if len(x) == 3:
                    self.lc_lastfm.SetStringItem(counter, 6, x[2])
                else:
                    self.lc_lastfm.SetStringItem(counter, 6, x[1])
            #else:
                # just printing artist
            #    self.lc_lastfm.InsertStringItem(counter, '')
            #    self.lc_lastfm.SetStringItem(counter, 1, x[0])
             #   self.lc_lastfm.SetStringItem(counter, 2, '')
             #   self.lc_lastfm.SetStringItem(counter, 3, '')
             #   self.lc_lastfm.SetStringItem(counter, 4, x[1])
             #   self.lc_lastfm.SetStringItem(counter, 5, '')
             #   self.lc_lastfm.SetStringItem(counter, 6, '')
            counter = counter + 1
              
        for t in range(0, 7):
            if len(self.lc_lastfm.GetItem(0, t).GetText()) >= 1:
                #if t == 6:
                #    self.lc_mylast.SetColumnWidth(t, wx.LIST_AUTOSIZE_USEHEADER)
                #else:
                self.lc_lastfm.SetColumnWidth(t, wx.LIST_AUTOSIZE)
            else:
                self.lc_lastfm.SetColumnWidth(t, 0) 
             
        #self.lc_lastfm.SetColumnWidth(0, 0)
        #self.lc_lastfm.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        #self.lc_lastfm.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        #self.lc_lastfm.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        #self.lc_lastfm.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
        #self.lc_lastfm.SetColumnWidth(5, wx.LIST_AUTOSIZE)
        #self.nb_main.SetPageText(2, 'last.fm (' + str(counter) + ')')  
                
    def OnLastfmRightClick(self, event):
        val = self.lc_lastfm.GetFirstSelected()
        if val != -1:
            if (self.lc_lastfm.GetItem(val, C_ARTIST).GetText() != '') & (self.lc_lastfm.GetItem(val, C_SONG).GetText() != ''):
                # make a menu
                ID_PLAYLIST = 1
                ID_CLEAR = 2
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")
                menu.AppendSeparator()
                menu.Append(ID_CLEAR, "Clear Playlist")
                wx.EVT_MENU(self.parent, ID_PLAYLIST, self.LastfmAddPlaylist)
                wx.EVT_MENU(self.parent, ID_CLEAR, self.parent.OnClearPlaylistClick)       
                self.parent.PopupMenu(menu)
                menu.Destroy()

    # playlist adding ---------------
                
    def OnAutoGenerateLastfmPlayist(self, event):
        """ add all the list items to the playlist """
        if self.lc_lastfm.GetItemCount() > 0:
            if self.lc_lastfm.GetItem(0, C_SONG).GetText() != '':
                self.parent.AddAll(self.lc_lastfm)
        
    def LastfmAddPlaylist(self, event):    
        """ add the selected list items to the playlist """
        val = self.lc_lastfm.GetFirstSelected()
        if self.lc_lastfm.GetSelectedItemCount() > 0:
            if self.lc_lastfm.GetItem(val, C_SONG).GetText() != '':
                self.parent.AddSelected(self.lc_lastfm)
        
    def OnLastfmListDoubleClick(self, event):
        # past the artist + track in the search field
        val = self.lc_lastfm.GetFirstSelected()
        artist = self.lc_lastfm.GetItem(val, 1).GetText()
        song = self.lc_lastfm.GetItem(val, 2).GetText()
        album = self.lc_lastfm.GetItem(val, 3).GetText()
        tag = self.lc_lastfm.GetItem(val, 5).GetText()
        #search for selected song, or album if song is empty
        if song != '':
            # search for db-clicked song
            #self.tc_search.SetValue(artist + ' ' + song)
            #self.SearchIt(artist + ' ' + song)
            self.parent.AddSelected(self.lc_lastfm)
            # display search page
            #self.nb_main.SetSelection(NB_PLAYLIST)
            #self.lc_search.SetFocus()
            #self.search_window.lc_search.Select(0)
        elif (len(song) == 0) & (len(album) != 0):
            # display the details for the clicked album
            # get all the tracks in teh album and display on the album page
            track_stuff = self.parent.GetAlbumAlbumInfo(artist, album)
            #print track_stuff
            self.parent.tab_album.tc_album_search_album.SetValue(track_stuff[1])
            self.parent.tab_album.tc_album_search_artist.SetValue(artist)
            self.parent.tab_album.tc_album_search_song.SetValue('')
            if len(track_stuff) > 0:
                track_list = self.parent.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.parent.tab_album.FillAlbumList(track_list, artist, track_stuff[1])
                # display album page
                self.parent.nb_main.SetSelection(NB_ALBUM)
        elif (len(song) == 0) & (len(album) == 0) & (len(tag) == 0):
            # get the top songs for the selected artist            
            if len(artist) > 0:
                self.OnLastTSArtistClick(event=None)
                #top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_song_list(artist)
                #self.GenerateScrobbList(top_tracks_list)
        elif (len(tag) != 0):
            #doble-clik on a tag, get list of top songs for tag
            self.OnLastTSGenreClick(event=None)
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_genre_top_song_list(tag)
            #self.GenerateScrobbList(top_tracks_list)
            
    def ShowLoading(self, loading=True):
        if loading:        
            message = "Loading Last.fm..."
            self.busy = PBI.PyBusyInfo(message, parent=None, title="Retrieving Data") #, icon=images.Smiles.GetBitmap())
            #wx.Yield()
        else:
            try:
                del self.busy
            except Exception, expt:
                print 'last.fm: ' + str(expt)+str(Exception)    
            
# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 
import wx.lib.agw.pybusyinfo as PBI

class GetLFThread(Thread): 
    # another thread to update download progress
    def __init__(self, parent, page):
        Thread.__init__(self)
        self.parent = parent
        self.page = page
        self.get_type =''
        self.load_state = False
        
        self.network = pylast.LastFMNetwork(api_key = API_KEY)
        
    def SetType(self, get_type):
        self.get_type = get_type        
  
    def run(self):
        event = LastEvent()
        
        if self.get_type == 'country':
            lfm_country = self.network.get_country(self.parent.country)
            results = lfm_country.get_top_tracks(page=self.page)
            columns = ('artist', 'song', 'count')            
        elif self.get_type == 'genre':
            lfm_tag = self.network.get_tag(self.parent.genre)
            results = lfm_tag.get_top_tracks(page=self.page)
            columns = ('artist', 'song')            
        else:        
            lfm_track = self.network.get_track(self.parent.artist, self.parent.song)
            lfm_artist = self.network.get_artist(self.parent.artist)
            #lfm_album = self.network.get_album(self.parent.artist, self.parent.album)
            
            if self.get_type == 'similar_track':
                results = lfm_track.get_similar(page=self.page)
                columns = ('artist', 'song', 'match')
            elif self.get_type == 'similar_artist':
                results = lfm_artist.get_similar(page=self.page)
                columns = ('artist', 'match')
            ##elif self.get_type == 'top_tracks_album':
            ##    results = lfm_album.get_info()
                #results = lfm_album.get_tracks()          
            elif self.get_type == 'top_artist':
                results = lfm_artist.get_top_tracks(page=self.page)
                columns = ('artist', 'song', 'count')
            elif self.get_type == 'top_albums':
                results = lfm_artist.get_top_albums(page=self.page)
                columns = ('artist', 'song', 'count')
            elif self.get_type == 'song_tags':
                results = lfm_track.get_top_tags(page=self.page)
                columns = ('tag', 'count')
            
        top_tracks_list = results['results']
        #print top_tracks_list
        self.current_page = int(results['page'])
        self.total_pages = int(results['total_pages'])
        event.data = (top_tracks_list, self.current_page, self.total_pages, columns)
        
        wx.PostEvent(self.parent.parent, event) 
