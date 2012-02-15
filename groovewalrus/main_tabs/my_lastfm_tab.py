"""
GrooveWalrus: My Last.fm Tab
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
from main_utils import default_app_open
from main_thirdp import pylast
from threading import Thread
from main_utils import options
from main_utils import system_files

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

PER_TIMES = ['recent', '7day', '3month', '6month', '12month', 'overall']

EVT_NEW_MYLAST = wx.PyEventBinder(wx.NewEventType(), 0)

class MyLastEvent(wx.PyCommandEvent):
    def __init__(self, eventType=EVT_NEW_MYLAST.evtType[0], id=0):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self.data = None

class MyLastfmTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent
        self.sys_files = system_files.GetDirectories(self)
        self.FILEDB = self.sys_files.DatabaseLocation()

        # controls ---------------------------
        self.tc_mylast_search_user = xrc.XRCCTRL(self.parent, 'm_tc_mylast_search_user')
        self.st_mylast_me = xrc.XRCCTRL(self.parent, 'm_st_mylast_me')
        self.st_mylast_friends = xrc.XRCCTRL(self.parent, 'm_st_mylast_friends')
        self.st_mylast_neigh = xrc.XRCCTRL(self.parent, 'm_st_mylast_neigh')
        self.st_mylast_loved = xrc.XRCCTRL(self.parent, 'm_st_mylast_loved')
        ##self.st_mylast_recomm = xrc.XRCCTRL(self, 'm_st_mylast_recomm')
        self.rx_mylast_period = xrc.XRCCTRL(self.parent, 'm_rx_mylast_period')
               
        # my last.fm list control -------------
        self.lc_mylast = xrc.XRCCTRL(self.parent, 'm_lc_mylast')
        self.lc_mylast.InsertColumn(0,"Rating")
        self.lc_mylast.InsertColumn(1,"Artist")
        self.lc_mylast.InsertColumn(2,"Song")
        self.lc_mylast.InsertColumn(3,"User")
        self.lc_mylast.InsertColumn(4,"Match")
        self.lc_mylast.InsertColumn(5,"Date")
        self.lc_mylast.InsertColumn(6,"Count")
        
        self.parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnMyLastListClick, self.lc_mylast)
        self.parent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnMyLastListDoubleClick, self.lc_mylast)
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnMyLastRightClick, self.lc_mylast)
        # wxGTK
        self.lc_mylast.Bind(wx.EVT_RIGHT_UP, self.OnMyLastRightClick)
        self.lc_mylast.Bind(wx.EVT_CHAR, self.parent.OnChar)

        #bindings ----------------
        self.st_mylast_me.Bind(wx.EVT_LEFT_UP, self.OnMyLastMeClick)
        self.st_mylast_friends.Bind(wx.EVT_LEFT_UP, self.OnMyLastFriendsClick)
        self.st_mylast_neigh.Bind(wx.EVT_LEFT_UP, self.OnMyLastNeighClick)
        self.parent.Bind(wx.EVT_BUTTON, self.OnMyLastClearClick, id=xrc.XRCID('m_bb_mylast_clear'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnMyLastSearchClick, id=xrc.XRCID('m_bb_mylast_search'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnMyLastWebClick, id=xrc.XRCID('m_bb_mylast_goweb'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnMyLastAddSelected, id=xrc.XRCID('m_bb_mylast_add'))
        self.st_mylast_loved.Bind(wx.EVT_LEFT_UP, self.OnMyLastLovedClick)  
        self.parent.Bind(wx.EVT_BUTTON, self.OnAutoGenerateMyLastPlayist, id=xrc.XRCID('m_bb_mylast_plize'))
        
        self.network = pylast.LastFMNetwork(api_key = API_KEY)
        self.current_page = 0
        self.total_pages = 0
        
        self.parent.Bind(EVT_NEW_MYLAST, self.GenerateScrobbList2)
        
# --------------------------------------------------------- 
# My last.fm ----------------------------------------------

    def MyLastThread(self, last_query, page=1, period='overall'):
        last_thread = GetLFThread(self, page, period)
        last_thread.SetType(last_query)
        self.ShowLoading()
        last_thread.start()

    def OnMyLastClearClick(self, event):
        # clear lastfm search field
        self.tc_mylast_search_user.Clear()

    def OnMyLastSearchClick(self, event):
        # search for user
        self.user = self.tc_mylast_search_user.GetValue()
        tperiod = self.rx_mylast_period.GetSelection()
        period = PER_TIMES[tperiod]
        page = 1
        
        if self.user != '':
            if period == 'recent':
                self.MyLastThread('user')
            else:
                self.MyLastThread('user_top_tracks', page, period)
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_user_top_songs(user, tperiod)
            #self.GenerateScrobbList2(top_tracks_list)
            
    def OnMyLastMeClick(self, event):
        # search for user
        self.user = options.GetSetting('lastfm-username', self.FILEDB) #self.parent.tc_options_username.GetValue()
        tperiod = self.rx_mylast_period.GetSelection()
        period = PER_TIMES[tperiod]
        page = 1
        if self.user:
            if period == 'recent':
                self.MyLastThread('user')
            else:
                self.MyLastThread('user_top_tracks', page, period)
            #top_tracks_list = audioscrobbler_lite.Scrobb().make_user_top_songs(user, tperiod)
            #self.GenerateScrobbList2(top_tracks_list)
            
    def OnMyLastFriendsClick(self, event):
        # search for user
        self.user = options.GetSetting('lastfm-username', self.FILEDB)
        if self.user:
            self.MyLastThread('friends')
            
    def OnMyLastNeighClick(self, event):
        # search for user
        self.user = options.GetSetting('lastfm-username', self.FILEDB)# self.parent.tc_options_username.GetValue()
        if self.user:
            self.MyLastThread('neighbours')
            
    def OnMyLastLovedClick(self, event):
        #grab your loved tracks
        self.user = self.tc_mylast_search_user.GetValue()
        if self.user == '':
            self.user = options.GetSetting('lastfm-username', self.FILEDB)# self.parent.tc_options_username.GetValue()
        if self.user:
            self.MyLastThread('loved_songs')
            
    def OnMyLastRecommenedArtistsClick(self, event):
        # search for user
        #self.session_key = self.song_scrobb._get_session_id()
        #if len(self.session_key) > 0:            
        #    print self.session_key
        #    auth_user = pylast.get_authenticated_user(API_KEY, SECRET, self.session_key)
        #    print auth_user
        #    while not auth_user.is_end_of_recommended_artists():
        #       print auth_user.get_recommended_artists_page()
        pass
                       
    def GenerateScrobbList2(self, event): #top_list, albums=False, artists=False):
        self.ShowLoading(False)
        top_list = event.data[0]
        self.current_page = event.data[1]
        self.total_pages = event.data[2]
        #tags=event.data[3]
        # put some data in a list control
        counter = 0
        self.lc_mylast.DeleteAllItems()
        for x in top_list:
            if len(x) == 3:
                # just printing artist/song
                self.lc_mylast.InsertStringItem(counter, '')
                self.lc_mylast.SetStringItem(counter, 1, x[0])
                self.lc_mylast.SetStringItem(counter, 2, x[1])
                self.lc_mylast.SetStringItem(counter, 3, '')
                self.lc_mylast.SetStringItem(counter, 4, '')
                if x[2].isdigit():
                    self.lc_mylast.SetStringItem(counter, 6, x[2])
                    self.lc_mylast.SetStringItem(counter, 5, '')
                else:
                    self.lc_mylast.SetStringItem(counter, 6, '')
                    self.lc_mylast.SetStringItem(counter, 5, x[2]) 
            if len(x) == 2:
                self.lc_mylast.InsertStringItem(counter, '')
                self.lc_mylast.SetStringItem(counter, 1, '')
                self.lc_mylast.SetStringItem(counter, 2, '')
                self.lc_mylast.SetStringItem(counter, 3, x[0])
                self.lc_mylast.SetStringItem(counter, 4, x[1])
                self.lc_mylast.SetStringItem(counter, 5, '')
                self.lc_mylast.SetStringItem(counter, 6, '')
                
            #self.lc_lastfm.SetItemData(counter, x[1] + ':' + x[0])
            counter = counter + 1
        
        for t in range(0, 7):
            if len(self.lc_mylast.GetItem(0, t).GetText()) >= 1:
                if t == 6:
                    self.lc_mylast.SetColumnWidth(t, wx.LIST_AUTOSIZE_USEHEADER)
                else:
                    self.lc_mylast.SetColumnWidth(t, wx.LIST_AUTOSIZE)
            else:
                self.lc_mylast.SetColumnWidth(t, 0)    
        #self.lc_mylast.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        #self.lc_mylast.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        #self.lc_mylast.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        #self.lc_mylast.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
        #self.nb_main.SetPageText(2, 'last.fm (' + str(counter) + ')')
                    
    def OnMyLastListClick(self, event):
        # past the artist + track in the search field
        val = self.lc_mylast.GetFirstSelected()
        user = self.lc_mylast.GetItem(val, 3).GetText()
        #set new value        
        self.tc_mylast_search_user.SetValue(user)
        
    def OnMyLastWebClick(self, event):
        # open website
        lw = 'http://www.last.fm/user/'        
        if len(self.tc_mylast_search_user.GetValue()) > 0:
            address = lw + self.tc_mylast_search_user.GetValue()
        elif options.GetSetting('lastfm-username', self.FILEDB):
            address = lw + options.GetSetting('lastfm-username', self.FILEDB)
        else:
            address = lw
        default_app_open.dopen(address)
        
    def OnMyLastRightClick(self, event):
        val = self.lc_mylast.GetFirstSelected()
        if val != -1:
            if (self.lc_mylast.GetItem(val, C_ARTIST).GetText() != '') & (self.lc_mylast.GetItem(val, C_SONG).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 1
                ID_CLEAR = 2
                ID_NEXT = 3
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")
                menu.AppendSeparator()
                menu.Append(ID_CLEAR, "Clear Playlist")
                menu.AppendSeparator()
                # a submenu in the 2nd menu
                submenu = wx.Menu()
                for s in range(1, self.total_pages):
                    submenu.Append(2000 + s, "Page " + str(s))
                menu.AppendMenu(203, "Results", submenu)
                wx.EVT_MENU(self.parent, ID_PLAYLIST, self.OnMyLastAddSelected)
                wx.EVT_MENU(self.parent, ID_CLEAR, self.parent.OnClearPlaylistClick)       
                self.parent.PopupMenu(menu)
                menu.Destroy()
        
    # playlist adding ---------------
                
    def OnAutoGenerateMyLastPlayist(self, event):
        """ add all the list items to the playlist """
        if self.lc_mylast.GetItemCount() > 0:
            if self.lc_mylast.GetItem(0, C_SONG).GetText() != '':
                self.parent.AddAll(self.lc_mylast)
                
    def OnMyLastAddSelected(self, event):
        """ add the selected list items to the playlist """
        val = self.lc_mylast.GetFirstSelected()
        if self.lc_mylast.GetSelectedItemCount() > 0:
            if self.lc_mylast.GetItem(val, C_SONG).GetText() != '':
                self.parent.AddSelected(self.lc_mylast)
                
    def OnMyLastListDoubleClick(self, event):
        """ add the selected list items to the playlist """
        # past the artist + track in the search field
        val = self.lc_mylast.GetFirstSelected()
        artist = self.lc_mylast.GetItem(val, C_ARTIST).GetText()
        song = self.lc_mylast.GetItem(val, C_SONG).GetText()
        user = self.lc_mylast.GetItem(val, 3).GetText()
        #search for selected song, or album if song is empty
        if song != '':
            # search for db-clicked song
            self.parent.AddSelected(self.lc_mylast)            
        if len(user) > 0:
            # display the details for the clicked user
            self.OnMyLastSearchClick(None)
        ##if (len(song) == 0) & (len(artist) > 0):
        ##    # get the top songs for the selected artist
        ##    self.nb_main.SetSelection(NB_LAST)            
        ##    top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_song_list(artist)
        ##    self.parent.tab_lastfm.GenerateScrobbList(top_tracks_list)
            
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
    def __init__(self, parent, page=1, period='overall'):
        Thread.__init__(self)
        self.parent = parent
        self.page = page
        self.period = period
        self.get_type =''
        self.load_state = False
        
        self.network = pylast.LastFMNetwork(api_key = API_KEY)
        
    def SetType(self, get_type):
        self.get_type = get_type        
                        
    def run(self):
        event = MyLastEvent()
        lfm_user = self.network.get_user(self.parent.user)
        if self.get_type == 'loved_songs':
            results = lfm_user.get_loved_tracks(page=self.page)
        elif self.get_type == 'neighbours':
            results = lfm_user.get_neighbours(page=self.page)
        elif self.get_type == 'friends':
            results = lfm_user.get_friends(page=self.page)
        elif self.get_type == 'user':            
            results = lfm_user.get_recent_tracks(page=self.page)
        elif self.get_type == 'user_top_tracks':            
            results = lfm_user.get_top_tracks(page=self.page, period=self.period)
            
        top_tracks_list = results['results']
        #print top_tracks_list
        self.current_page = int(results['page'])
        self.total_pages = int(results['total_pages'])
        event.data = (top_tracks_list, self.current_page, self.total_pages, False)
        
        wx.PostEvent(self.parent.parent, event) 
                   