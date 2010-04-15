# -*- coding: utf-8 -*-
"""
GrooveWalrus: GrooveWalrus
Copyright (C) 2009
11y3y3y3y43@gmail.com
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
import wx.html
import wx.xrc as xrc
#from wx.lib.flashwin import FlashWindow

import os
import sys
import shutil
import time
import random
# comtypes?
if os.name == 'nt':
    import comtypes
import urllib
from threading import Thread
import sqlite3

from main_utils import musicbrainz
from main_utils import tinysong
from main_utils import read_write_xml
from main_utils import audioscrobbler_lite
from main_utils import default_app_open
from main_utils import local_songs
#from main_utils import mp3_rec
from main_utils import plugin_loader
from main_utils import system_files
from main_utils import file_cache
from main_utils import prefetch
from main_utils import download_feed

from main_controls import drag_and_drop
from main_controls import playback_panel
from main_controls import ratings_button
#from main_controls import custom_slider

from main_windows import version_check
from main_windows import album_viewer
from main_windows import search_window
from main_windows import options_window
from main_windows import details_window
from main_windows import song_collection

from main_tabs import list_sifter_tab
from main_tabs import favorites_tab

from main_thirdp import pylast
if os.name == 'nt':
    from main_thirdp import soundmixer 
else:
    from main_thirdp import soundmixer_linux as soundmixer
from main_thirdp.grooveshark.jsonrpc import *
from main_thirdp import grooveshark_old

#from plugins.x2 import x2
#from plugins.twitter import twitter
#from plugins.flash import flash
#from plugins.played import played
#from plugins.griddle import griddle
#from plugins.ratings import ratings
#from plugins.minimode import minimode
#from plugins.lyrics import lyrics

PROGRAM_VERSION = "0.213"
PROGRAM_NAME = "GrooveWalrus"

PLAY_SONG_URL ="http://listen.grooveshark.com/songWidget.swf?hostname=cowbell.grooveshark.com&style=metal&p=1&songID="
PLAY_SONG_ALTERNATE_URL ="http://listen.grooveshark.com/main.swf?hostname=cowbell.grooveshark.com&p=1&songID="
SONG_SENDER_URL = "http://gwp.turnip-town.net/?"

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0])) #os.getcwd()
GRAPHICS_LOCATION = os.path.join(SYSLOC, 'graphics') + os.sep

RESFILE = SYSLOC + os.sep + "layout.xml"
P_ICON = SYSLOC + os.sep + "gw.ico"

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
SECRET = ""
LASTFM_CLIENT_ID = 'gws'
BUFFER_SIZE = 224000

class MainFrame(wx.Frame): 
    def __init__(self): 
        wx.Frame.__init__(self, None, -1, PROGRAM_NAME + ' ' + PROGRAM_VERSION, size=(690, 530), pos=(200,200), style=wx.DEFAULT_FRAME_STYLE|wx.WANTS_CHARS) #^(wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)) #, style=wx.STAY_ON_TOP) 
        #panel = wx.Panel(self, -1, size=(400, 100)) 
        #self.SetTransparent(180)
        
        # -- initialize i18n
        self.initI18n()
        
        # load menubar from xrc xml file
        res = xrc.XmlResource(RESFILE)
        self.menubar = res.LoadMenuBarOnFrame(self, "m_mb_main")
        self.menu_plugins = self.menubar.GetMenu(5)
        self.menu_tools = self.menubar.GetMenu(4)
                
        # program icon
        ib = wx.IconBundle()
        ib.AddIconFromFile(P_ICON, wx.BITMAP_TYPE_ANY)
        self.SetIcons(ib)
        
        # system tray icon        
        self.tray_icon = None
        
    def UseTrayIcon(self):
        self.tray_icon =wx.TaskBarIcon()
        icon = wx.Icon(P_ICON, wx.BITMAP_TYPE_ICO)
        self.tray_icon.SetIcon(icon, 'GrooveWalrus')
        wx.EVT_TASKBAR_LEFT_UP(self.tray_icon, self.OnTrayLeftClick)
        self.Bind(wx.EVT_ICONIZE, self.OnMinimize)
        
    def OnTrayLeftClick(self, event):
        # toggle showing main form
        if self.IsShown() == True:
            # maximize and show
            self.Show(False)
        else:
            # blah, using iconize to bring to foreground, "show"ing hides it behind other windows
            #self.Iconize(True)
            #self.Iconize(False)
            self.Iconize(False)
            self.SetWindowStyle(wx.STAY_ON_TOP)
            self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE|wx.WANTS_CHARS)
            self.Show(True)
            
    def OnMinimize(self, event):
        if self.tray_icon: #.IsIconInstalled():
            self.Show(False)
            
    def initI18n(self):
        #localization
        #http://wiki.wxpython.org/Internationalization
        #http://wiki.wxpython.org/XRCAndI18N
        wx.Locale.AddCatalogLookupPathPrefix(os.path.join(os.getcwd(), 'locale'))
        self.l18n = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.l18n.AddCatalog('layout')        
        #    u'en' : (wx.LANGUAGE_ENGLISH, u'en_US.UTF-8'),
        #    u'es' : (wx.LANGUAGE_SPANISH, u'es_ES.UTF-8'),
        #    u'fr' : (wx.LANGUAGE_FRENCH, u'fr_FR.UTF-8'),
        #    u'it' : (wx.LANGUAGE_ITALIAN, u'it_IT.UTF-8'),
        #    u'nl' : (wx.LANGUAGE_DUTCH, u'nl_NL.UTF-8'),
        #    u'pl' : (wx.LANGUAGE_POLISH, u'pl_PL.UTF-8'),
        #wx.LANGUAGE_DEFAULT
        #wx.LANGUAGE_TURKISH
        
class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        
        self.parent = parent
        
        # set directories ------------
        system_files.GetDirectories(self).DataDirectory()
        self.image_save_location = system_files.GetDirectories(self).MakeDataDirectory('images') + os.sep
        system_files.GetDirectories(self).MakeDataDirectory('updates') + os.sep
        system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep
        self.playlist_save_location = system_files.GetDirectories(self).MakeDataDirectory('playlists') + os.sep
        self.main_playlist_location = system_files.GetDirectories(self).DataDirectory() + os.sep + "playlist.xspf"
        self.main_playlist_location_bak = system_files.GetDirectories(self).DataDirectory() + os.sep + "playlist.bak"        
        ##self.faves_playlist_location = system_files.GetDirectories(self).DataDirectory() + os.sep + "faves.xspf"
        ##self.faves_playlist_location_bak = system_files.GetDirectories(self).DataDirectory() + os.sep + "faves.bak"
        
        # create/update database ----------
        local_songs.DbFuncs().create_tables()
        
        # xrc gui layout ------------------
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)
        # custom widget handler
        ##res.InsertHandler(custom_slider.MyCustomSliderXmlHandler(self))
        # Now create a panel from the resource data
        self.panel = res.LoadPanel(self, "m_pa_main")        
        
        xrc.XRCCTRL(self, 'm_pa_options_plugins').SetVirtualSize((1000, 1000))
        xrc.XRCCTRL(self, 'm_pa_options_plugins').SetScrollRate(20,20)
        
        #list sifter tab        
        list_sifter = list_sifter_tab.ListSifterTab(self)
        
        #favorites tab        
        self.favorites = favorites_tab.FavoritesTab(self)
               
        # control references ---------------
        # playback        
        self.bb_random = xrc.XRCCTRL(self, 'm_bb_random')
        self.bb_repeat = xrc.XRCCTRL(self, 'm_bb_repeat')
        self.bb_record = xrc.XRCCTRL(self, 'm_bb_record')
        self.tc_search = xrc.XRCCTRL(self, 'm_tc_search')        
        self.sl_volume = xrc.XRCCTRL(self, 'm_sl_volume')
        self.pa_playback = xrc.XRCCTRL(self, 'm_pa_playback')
        
        ##self.sl_volume = res.LoadObject(self, "m_cc_volume_slider", "CustomSlider")
        ##self.sl_volume2 = xrc.XRCCTRL(self, 'm_cc_volume_slider')
        ##self.sl_volume = self.cslid        
        ##self.sl_volume3 = self.FindWindowById( xrc.XRCID('m_cc_volume_slider' ))         
        
        self.bb_update = xrc.XRCCTRL(self, 'm_bb_update')
             
        self.nb_main = xrc.XRCCTRL(self, 'm_nb_main')
        self.pa_options_plugins = xrc.XRCCTRL(self, "m_pa_options_plugins")
        
        self.bm_cover = xrc.XRCCTRL(self, 'm_bm_cover_small')
        self.bm_cover_large = xrc.XRCCTRL(self, 'm_bm_cover_large')
        
        # last fm
        self.st_last_ts_artist = xrc.XRCCTRL(self, 'm_st_last_ts_artist')
        self.st_last_ta_artist = xrc.XRCCTRL(self, 'm_st_last_ta_artist')
        self.st_last_ts_geo = xrc.XRCCTRL(self, 'm_st_last_ts_geo')
        self.st_last_ts_genre = xrc.XRCCTRL(self, 'm_st_last_ts_genre')
        self.st_last_ts_album = xrc.XRCCTRL(self, 'm_st_last_ts_album')
        self.st_last_ts_similar = xrc.XRCCTRL(self, 'm_st_last_ts_similar')
        self.st_last_art_similar = xrc.XRCCTRL(self, 'm_st_last_art_similar')
        self.st_last_tt_song = xrc.XRCCTRL(self, 'm_st_last_tt_song')
        
        self.tc_last_search_album = xrc.XRCCTRL(self, 'm_tc_last_search_album')
        self.tc_last_search_artist = xrc.XRCCTRL(self, 'm_tc_last_search_artist')
        self.tc_last_search_song = xrc.XRCCTRL(self, 'm_tc_last_search_song')
        self.ch_last_country = xrc.XRCCTRL(self, 'm_ch_last_country')
        self.co_last_tag = xrc.XRCCTRL(self, 'm_co_last_tag')
        
        # my last
        self.tc_mylast_search_user = xrc.XRCCTRL(self, 'm_tc_mylast_search_user')
        self.st_mylast_me = xrc.XRCCTRL(self, 'm_st_mylast_me')
        self.st_mylast_friends = xrc.XRCCTRL(self, 'm_st_mylast_friends')
        self.st_mylast_neigh = xrc.XRCCTRL(self, 'm_st_mylast_neigh')
        ##self.st_mylast_recomm = xrc.XRCCTRL(self, 'm_st_mylast_recomm')
        self.rx_mylast_period = xrc.XRCCTRL(self, 'm_rx_mylast_period')       
        
        # album
        ##self.st_album_get_tracks = xrc.XRCCTRL(self, 'm_st_album_get_tracks')
        self.tc_album_search_artist = xrc.XRCCTRL(self, 'm_tc_album_search_artist')
        self.tc_album_search_song = xrc.XRCCTRL(self, 'm_tc_album_search_song')
        self.tc_album_search_album = xrc.XRCCTRL(self, 'm_tc_album_search_album')
        
        # bio
        self.bm_bio_pic = xrc.XRCCTRL(self, 'm_bm_bio_pic')
        self.hm_bio_text = xrc.XRCCTRL(self, 'm_hm_bio_text')        

        # song collection
        self.tc_scol_song = xrc.XRCCTRL(self, 'm_tc_scol_song')
        self.tc_scol_song.Bind(wx.EVT_TEXT, self.OnSColSongText)
        self.rb_scol_folder = xrc.XRCCTRL(self, 'm_rb_scol_folder')
        self.rb_scol_file = xrc.XRCCTRL(self, 'm_rb_scol_file')
        self.Bind(wx.EVT_RADIOBUTTON, self.OnSColRadio, self.rb_scol_folder)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnSColRadio, self.rb_scol_file)
        self.lc_scol_col = xrc.XRCCTRL(self, 'm_lc_scol_col')
        self.lc_scol_col.InsertColumn(0,"Id")
        self.lc_scol_col.InsertColumn(1,"File")
        self.lc_scol_col.InsertColumn(2,"Folder")
        self.lc_scol_col.InsertColumn(3,"Location")
        
        self.lc_scol_col.SetColumnWidth(0, 50)
        self.lc_scol_col.SetColumnWidth(1, 175)
        self.lc_scol_col.SetColumnWidth(2, 150)
        self.lc_scol_col.SetColumnWidth(3, 190)
        self.lc_scol_col.SetItemCount(local_songs.DbFuncs().GetCountAndLast()[0])
        # wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnScolRightClick, self.lc_scol_col)
        # wxGTK
        self.lc_scol_col.Bind(wx.EVT_RIGHT_UP, self.OnScolRightClick)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ScolAddPlaylist, self.lc_scol_col)
        
        # options
        self.tc_options_username = xrc.XRCCTRL(self, 'm_tc_options_username')
        self.tc_options_password = xrc.XRCCTRL(self, 'm_tc_options_password')
        self.rx_options_double_click = xrc.XRCCTRL(self, 'm_rx_options_double_click')
        self.cb_options_list_clear = xrc.XRCCTRL(self, 'm_cb_options_list_clear')
        self.st_options_auth = xrc.XRCCTRL(self, 'm_st_options_auth')
        self.cb_options_alternate = xrc.XRCCTRL(self, 'm_cb_options_alternate')
        self.cb_options_noid = xrc.XRCCTRL(self, 'm_cb_options_noid')
        self.sc_options_gs_wait = xrc.XRCCTRL(self, 'm_sc_options_gs_wait')
        self.sc_options_song_seconds = xrc.XRCCTRL(self, 'm_sc_options_song_seconds')
        self.sc_options_song_minutes = xrc.XRCCTRL(self, 'm_sc_options_song_minutes')
        self.rx_options_scrobble_port = xrc.XRCCTRL(self, 'm_rx_options_scrobble_port')
        self.cb_options_scrobble = xrc.XRCCTRL(self, 'm_cb_options_scrobble')
        self.cb_options_prefetch = xrc.XRCCTRL(self, 'm_cb_options_prefetch')
        self.cb_options_scrobble_album = xrc.XRCCTRL(self, 'm_cb_options_scrobble_album')
        self.cb_options_tray = xrc.XRCCTRL(self, 'm_cb_options_tray')
        self.cb_options_autosave = xrc.XRCCTRL(self, 'm_cb_options_autosave')
        ##self.ch_options_bitrate = xrc.XRCCTRL(self, 'm_ch_options_bitrate')
        self.bu_options_record_dir = xrc.XRCCTRL(self, 'm_bu_options_record_dir')
        
        self.st_options_i18n_default = xrc.XRCCTRL(self, 'm_st_options_i18n_default')
        self.st_options_i18n_default.SetLabel('Locale: ' + wx.Locale(wx.LANGUAGE_DEFAULT).GetCanonicalName())
              
        # list controls ------------
        # last.fm
        self.lc_lastfm = xrc.XRCCTRL(self, 'm_lc_lastfm')
        self.lc_lastfm.InsertColumn(0,"Artist")
        self.lc_lastfm.InsertColumn(1,"Song")
        self.lc_lastfm.InsertColumn(2,"Album")
        self.lc_lastfm.InsertColumn(3,"Count")
        self.lc_lastfm.InsertColumn(4,"Tag")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLastfmListClick, self.lc_lastfm)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnLastfmListDoubleClick, self.lc_lastfm)
        # wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnLastfmRightClick, self.lc_lastfm)
        # wxGTK
        self.lc_lastfm.Bind(wx.EVT_RIGHT_UP, self.OnLastfmRightClick)
        
        # my last.fm
        self.lc_mylast = xrc.XRCCTRL(self, 'm_lc_mylast')
        self.lc_mylast.InsertColumn(0,"Artist")
        self.lc_mylast.InsertColumn(1,"Song")
        self.lc_mylast.InsertColumn(2,"User")
        self.lc_mylast.InsertColumn(3,"Count")        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnMyLastListClick, self.lc_mylast)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnMyLastListDoubleClick, self.lc_mylast)
        # wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnMyLastRightClick, self.lc_mylast)
        # wxGTK
        self.lc_mylast.Bind(wx.EVT_RIGHT_UP, self.OnMyLastRightClick)
        
        # playlist
        # playlist is subclassed to draglist in the xrc
        self.lc_playlist = xrc.XRCCTRL(self,'m_lc_playlist')
        self.lc_playlist.InsertColumn(0,"Artist")
        self.lc_playlist.InsertColumn(1,"Song")
        self.lc_playlist.InsertColumn(2,"Album")
        self.lc_playlist.InsertColumn(3,"Id")
        self.lc_playlist.InsertColumn(4,"Time")
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPlayListPlayClick, self.lc_playlist)
        # wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnPlaylistRightClick, self.lc_playlist)
        # wxGTK
        self.lc_playlist.Bind(wx.EVT_RIGHT_UP, self.OnPlaylistRightClick)
        ##self.lc_playlist.Bind(wx.EVT_CHAR, self.OnPlaylistKeyPress)
        self.lc_playlist.Bind(wx.EVT_KEY_UP, self.OnDeletePress)
        
        ##dynamic listctrl resize
        ##wx.EVT_SIZE(self.parent, self.ResizePlaylist)
        ##wx.EVT_MAXIMIZE(self.parent, self.ResizePlaylist)
        
        # album
        self.lc_album = xrc.XRCCTRL(self, 'm_lc_album')
        self.lc_album.InsertColumn(0,"Artist")
        self.lc_album.InsertColumn(1,"Song")
        self.lc_album.InsertColumn(2,"Album")
        #self.lc_album.InsertColumn(3,"Id")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAlbumListClick, self.lc_album)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnAlbumDoubleClick, self.lc_album)
        # wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnAlbumRightClick, self.lc_album)
        # wxGTK
        self.lc_album.Bind(wx.EVT_RIGHT_UP, self.OnAlbumRightClick)
        
                
        # ---------------------------------------------------------------
        
        
        # and do the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        # bindings ----------------
        #playback                
        self.Bind(wx.EVT_BUTTON, self.OnRandomClick, id=xrc.XRCID('m_bb_random'))
        self.Bind(wx.EVT_BUTTON, self.OnRepeatClick, id=xrc.XRCID('m_bb_repeat'))
        self.Bind(wx.EVT_BUTTON, self.OnRecordClick, id=xrc.XRCID('m_bb_record'))        
        self.Bind(wx.EVT_BUTTON, self.OnBackwardClick, id=xrc.XRCID('m_bb_backward'))
        self.Bind(wx.EVT_BUTTON, self.OnForwardClick, id=xrc.XRCID('m_bb_forward'))
        self.Bind(wx.EVT_BUTTON, self.OnPlayClick, id=xrc.XRCID('m_bb_play'))
        self.Bind(wx.EVT_BUTTON, self.OnStopClick, id=xrc.XRCID('m_bb_stop'))
        self.Bind(wx.EVT_SLIDER, self.OnVolumeClick, id=xrc.XRCID('m_sl_volume'))
        
        #search
        self.Bind(wx.EVT_BUTTON, self.OnSearchClick, id=xrc.XRCID('m_bb_search'))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearchClick, self.tc_search)
        self.search_window = search_window.SearchWindow(self)
        self.parent.Bind(wx.EVT_MOVE, self.search_window.MoveMe)                
        
        #playlist
        self.Bind(wx.EVT_BUTTON, self.OnSavePlaylistClick, id=xrc.XRCID('m_bb_save_playlist'))
        self.Bind(wx.EVT_BUTTON, self.FixPlaylistItem, id=xrc.XRCID('m_bb_fix_song'))
        self.Bind(wx.EVT_BUTTON, self.OnClearPlaylistClick, id=xrc.XRCID('m_bb_clear_playlist'))
        self.Bind(wx.EVT_BUTTON, self.RemovePlaylistItem, id=xrc.XRCID('m_bb_remove_playlist_item'))
        self.Bind(wx.EVT_BUTTON, self.OnLoadPlaylistClick, id=xrc.XRCID('m_bb_load_playlist'))
        
        
        #playlistize        
        self.Bind(wx.EVT_BUTTON, self.OnAutoGenerateLastfmPlayist, id=xrc.XRCID('m_bu_last_plize'))
        self.Bind(wx.EVT_BUTTON, self.OnAutoGenerateMyLastPlayist, id=xrc.XRCID('m_bu_mylast_plize'))
        self.Bind(wx.EVT_BUTTON, self.OnAutoGenerateAlbumPlayist, id=xrc.XRCID('m_bu_album_plize'))
        
        #last.fm        
        self.st_last_ts_artist.Bind(wx.EVT_LEFT_UP, self.OnLastTSArtistClick)
        self.st_last_ta_artist.Bind(wx.EVT_LEFT_UP, self.OnLastTAArtistClick)
        self.st_last_ts_geo.Bind(wx.EVT_LEFT_UP, self.OnLastTSGeoClick)
        self.st_last_ts_genre.Bind(wx.EVT_LEFT_UP, self.OnLastTSGenreClick)
        self.st_last_ts_album.Bind(wx.EVT_LEFT_UP, self.OnLastTSAlbumClick)
        self.st_last_ts_similar.Bind(wx.EVT_LEFT_UP, self.OnLastTSSimilarClick)
        self.st_last_art_similar.Bind(wx.EVT_LEFT_UP, self.OnLastArtistSimilarClick)
        self.st_last_tt_song.Bind(wx.EVT_LEFT_UP, self.OnLastTTSongClick)
        self.Bind(wx.EVT_BUTTON, self.OnClearLastSearchClick, id=xrc.XRCID('m_bb_last_clear_search'))
        
        #albums
        self.Bind(wx.EVT_BUTTON, self.OnAlbumGetTracks, id=xrc.XRCID('m_bu_album_tracks'))
        self.Bind(wx.EVT_BUTTON, self.OnClearAlbumSearchClick, id=xrc.XRCID('m_bb_album_clear_search'))
        self.Bind(wx.EVT_BUTTON, self.OnAlbumSearchClick, id=xrc.XRCID('m_bb_album_search'))
        self.bm_cover_large.Bind(wx.EVT_LEFT_UP, self.OnAlbumCoverClick)
        self.bm_cover.Bind(wx.EVT_LEFT_UP, self.OnAlbumCoverClick)
                
        #my last.fm
        self.st_mylast_me.Bind(wx.EVT_LEFT_UP, self.OnMyLastMeClick)
        self.st_mylast_friends.Bind(wx.EVT_LEFT_UP, self.OnMyLastFriendsClick)
        self.st_mylast_neigh.Bind(wx.EVT_LEFT_UP, self.OnMyLastNeighClick)
        self.Bind(wx.EVT_BUTTON, self.OnMyLastClearClick, id=xrc.XRCID('m_bb_mylast_clear'))
        self.Bind(wx.EVT_BUTTON, self.OnMyLastSearchClick, id=xrc.XRCID('m_bb_mylast_search'))
        self.Bind(wx.EVT_BUTTON, self.OnMyLastWebClick, id=xrc.XRCID('m_bb_mylast_goweb'))
                
        #options
        self.Bind(wx.EVT_RADIOBOX, self.SaveOptions, id=xrc.XRCID('m_rx_options_double_click'))
        self.Bind(wx.EVT_RADIOBOX, self.SaveOptions, id=xrc.XRCID('m_rx_options_scrobble_port'))
        self.Bind(wx.EVT_SPINCTRL, self.SaveOptions, id=xrc.XRCID('m_sc_options_gs_wait'))
        self.Bind(wx.EVT_SPINCTRL, self.SaveOptions, id=xrc.XRCID('m_sc_options_song_minutes'))
        self.Bind(wx.EVT_SPINCTRL, self.SaveOptions, id=xrc.XRCID('m_sc_options_song_seconds'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_list_clear'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_alternate'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_scrobble_album'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_scrobble'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_prefetch'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_noid'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_tray'))
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, id=xrc.XRCID('m_cb_options_autosave'))
        ##self.Bind(wx.EVT_CHOICE, self.SaveOptions, id=xrc.XRCID('m_ch_options_bitrate'))
        self.Bind(wx.EVT_BUTTON, self.OnSaveOptionsClick, id=xrc.XRCID('m_bu_options_save'))        
        self.Bind(wx.EVT_BUTTON, self.OnSetRecordDirClick, id=xrc.XRCID('m_bu_options_record_dir'))
        
        #song collection
        self.Bind(wx.EVT_BUTTON, self.OnSColAddClick, id=xrc.XRCID('m_bb_scol_add'))
        self.Bind(wx.EVT_BUTTON, self.OnSColDeleteClick, id=xrc.XRCID('m_bb_scol_delete'))
        self.Bind(wx.EVT_BUTTON, self.ScolAddPlaylist, id=xrc.XRCID('m_bb_scol_playlist'))
        self.Bind(wx.EVT_BUTTON, self.OnSColClearClick, id=xrc.XRCID('m_bb_scol_clear'))
        
        
        self.Bind(wx.EVT_BUTTON, self.OnUpdateClick, self.bb_update)
        wx.EVT_CLOSE(self.parent, self.OnExit)
           
        # --------------------------------------------------------- 
        #vars
        
        self.flash = None
        # ***self.flash.LoadMovie(0, 'http://listen.grooveshark.com/songWidget.swf?hostname=cowbell.grooveshark.com&songID=13721223&style=metal&p=0')
        self.autoplay = False
        
        #check for playlist
        if len(sys.argv) == 2:
            file_name = sys.argv[1]
            if file_name.endswith('.xspf'):
                self.ReadPlaylist(file_name)
                self.SavePlaylist(self.main_playlist_location)
                self.autoplay = True
            elif file_name.endswith('.m3u'):
                self.ReadWinampPlaylist(file_name)
                self.SavePlaylist(self.main_playlist_location)
                self.autoplay = True
            elif file_name.endswith('.mp3'):
                self.ScolFileAdd(file_name)
                self.SavePlaylist(self.main_playlist_location)
                self.autoplay = True
        elif len(sys.argv) == 3:
            #::C:\Users\[username]\Desktop\GrooveWalrus\gw.exe
            #::-url
            #::gwp://u2:rattle%20and%20hum/
            meat = sys.argv[2].split('gwp://')
            if len(meat) == 2:                
                if len(meat[1].split(':')) == 2:
                    song = meat[1].split(':')[1].replace('%20', ' ').replace('/', '')
                    artist = meat[1].split(':')[0].replace('%20', ' ')
                    self.SetPlaylistItem(0, artist, song)
                    self.autoplay = True
        else:
            self.ReadPlaylist(self.main_playlist_location)
            
       
        
        self.current_play_time = 0
        self.current_track = -1
        # thread for playing a local track
        self.current_local = None
        self.partist = ''
        self.ptrack = ''
        self.palbum = ''
        self.palbum_art_file =''
        self.pmusic_id = 0
        self.pgroove_id = 0
        self.download_percent = 0
        self.pstatus = 'stopped'
        
        #temp for web types
        self.web_music_type = 'GrooveShark'
        self.web_music_url = ''
        self.use_web_music = False
        
        #self.recorder = mp3_rec()
        #self.recording_status = False
        
        self.record_toggle = False
        self.repeat_toggle = False
        self.repeat_toggle_type = 'One'
        self.random_toggle = False
        
        self.gobbled_track = 0
        
        self.bb_update.Show(False)
        

        # set focus to search text control
        self.tc_search.SetFocus()
        
        #version check ----------
        version_check = WebFetchThread(self, '', '', PROGRAM_VERSION, 'VERSION')
        #THREAD
        version_check.start()
        #version_check.VersionCheck(self, PROGRAM_VERSION).CheckVersion()
        
        # grooveshark streaming init ---
        self.groove_session = None
        
        #pre-fetching ----------
        self.prefetch = True
           
        # timer ----------------
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.time_count = 0
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        #wx.CallAfter(self.Refresh)        
        
        # scrobb ----------------
        self.scrobbed_active = 0
        self.auth_attempts = 0
        self.scrobbed_track = 0
        self.session_key2 = None
        #self.SetScrobb()
        
        #autoplay ---------------
        if self.autoplay == True:
            self.OnPlayClick(event=None)           
        
        # album cover
        self.album_viewer = album_viewer.AlbumViewer(self, GRAPHICS_LOCATION)
        #cover_bmp = wx.Bitmap(self.image_save_location + 'no_cover.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.SetImage('no_cover.png', GRAPHICS_LOCATION)
        
        # volume control
        #check for txt, don't adjust volume if present
        if os.path.isfile('disable_set_volume.txt'):
            pass
        else:
            self.SetVolume(self.GetVolume())
               
        # hotkeys ------------------
        backID = 701
        playID = 702
        stopID = 703
        forwID = 704
        saveID = 705
        loadID = 706
        randID = 707
        reapID = 708
        vlupID = 709
        vldnID = 7010
        tbupID = 7012
        muteID = 7011
        #tbdnID = 7011
        ctrldID = 801
        ctrlrID = 802
        ctrlbID = 803
        ctrl9ID = 910
        ctrlfID = 804
        ctrlmID = 805        
        
        self.aTable_values = [
                                   (wx.ACCEL_NORMAL, wx.WXK_F1, backID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F2, playID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F3, stopID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F4, forwID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F5, saveID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F6, loadID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F7, randID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F8, reapID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F9, vldnID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F10, vlupID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F11, muteID),
                                   (wx.ACCEL_NORMAL, wx.WXK_F12, tbupID),
                                   (wx.ACCEL_CTRL, ord('D'), ctrldID),
                                   (wx.ACCEL_CTRL, ord('R'), ctrlrID),
                                   (wx.ACCEL_CTRL, ord('B'), ctrlbID),
                                   (wx.ACCEL_CTRL, ord('9'), ctrl9ID),
                                   (wx.ACCEL_CTRL, ord('F'), ctrlfID),
                                   (wx.ACCEL_CTRL, ord('M'), ctrlmID)
                                           ]
        aTable = wx.AcceleratorTable(self.aTable_values)
        #add to main program
        self.SetAcceleratorTable(aTable)
        #add to album viewer window too
        self.album_viewer.SetAcceleratorTable(aTable)
         
        wx.EVT_MENU(self, backID, self.OnBackwardClick)
        wx.EVT_MENU(self, playID, self.OnPlayClick)
        wx.EVT_MENU(self, stopID, self.OnStopClick)
        wx.EVT_MENU(self, forwID, self.OnForwardClick) 
        
        wx.EVT_MENU(self, saveID, self.OnSavePlaylistClick)
        wx.EVT_MENU(self, loadID, self.OnLoadPlaylistClick)
        wx.EVT_MENU(self, randID, self.OnRandomClick)
        wx.EVT_MENU(self, reapID, self.OnRepeatClick)
        
        wx.EVT_MENU(self, vldnID, self.OnVolumeDown)
        wx.EVT_MENU(self, vlupID, self.OnVolumeUp)
        wx.EVT_MENU(self, muteID, self.OnMuteClick)
        wx.EVT_MENU(self, tbupID, self.OnNextTab)
        
        wx.EVT_MENU(self, ctrldID, self.OnClearPlaylistClick)
        wx.EVT_MENU(self, ctrlrID, self.ResetPosition)
        wx.EVT_MENU(self, ctrlbID, self.RandomBackgroundColour)
        wx.EVT_MENU(self, ctrlfID, self.OnSearchClick)
        
        wx.EVT_MENU(self, ctrl9ID, self.ClearAlbumValues)
        wx.EVT_MENU(self, ctrlmID, self.MiniMode)
        
        
        # menu items -----------
        # file menu
        self.parent.Bind(wx.EVT_MENU, self.OnLoadPlaylistClick, id=xrc.XRCID("m_mi_open"))
        self.parent.Bind(wx.EVT_MENU, self.OnSavePlaylistClick, id=xrc.XRCID("m_mi_save_playlist_as"))
        self.parent.Bind(wx.EVT_MENU, self.OnExit, id=xrc.XRCID("m_mi_exit"))
        
        # edit menu
        self.parent.Bind(wx.EVT_MENU, self.OnDeleteClick, id=xrc.XRCID("m_mi_delete"))
        self.parent.Bind(wx.EVT_MENU, self.OnCopyClick, id=xrc.XRCID("m_mi_copy"))
        self.parent.Bind(wx.EVT_MENU, self.OnPasteClick, id=xrc.XRCID("m_mi_paste"))
        self.parent.Bind(wx.EVT_MENU, self.OnCutClick, id=xrc.XRCID("m_mi_cut"))
        self.parent.Bind(wx.EVT_MENU, self.OnUndoClick, id=xrc.XRCID("m_mi_undo"))
        self.undo_toggle = 0
        self.undo_toggle_faves = 0
        self.copy_array = []
        
        # view menu
        self.parent.Bind(wx.EVT_MENU, self.OnAlbumCoverClick, id=xrc.XRCID("m_mi_album_cover"))
        
        # playback menu
        self.parent.Bind(wx.EVT_MENU, self.OnPlayClick, id=xrc.XRCID("m_mi_play"))
        self.parent.Bind(wx.EVT_MENU, self.OnStopClick, id=xrc.XRCID("m_mi_stop"))
        self.parent.Bind(wx.EVT_MENU, self.OnBackwardClick, id=xrc.XRCID("m_mi_previous"))
        self.parent.Bind(wx.EVT_MENU, self.OnForwardClick, id=xrc.XRCID("m_mi_next"))
        self.parent.Bind(wx.EVT_MENU, self.OnRandomClick, id=xrc.XRCID("m_mi_shuffle"))
        self.parent.Bind(wx.EVT_MENU, self.OnRepeatClick, id=xrc.XRCID("m_mi_repeat"))
        self.parent.Bind(wx.EVT_MENU, self.OnMuteClick, id=xrc.XRCID("m_mi_volume_mute"))
        self.parent.Bind(wx.EVT_MENU, self.OnVolumeUp, id=xrc.XRCID("m_mi_volume_up"))
        self.parent.Bind(wx.EVT_MENU, self.OnVolumeDown, id=xrc.XRCID("m_mi_volume_down"))
        
        # tools menu        
        self.parent.Bind(wx.EVT_MENU, self.OnUpdateClick, id=xrc.XRCID("m_mi_version_update"))
        self.parent.Bind(wx.EVT_MENU, self.OnSColAddClick, id=xrc.XRCID("m_mi_song_collection"))
        #
        self.lastfm_toggle = self.parent.menu_tools.Append(7666, "Last.fm Scrobbling", kind=wx.ITEM_CHECK)
        self.parent.Bind(wx.EVT_MENU, self.OnToggleScrobble, id=7666)        
        
        # help menu
        self.parent.Bind(wx.EVT_MENU, self.OnGSVersionClick, id=xrc.XRCID("m_mi_gs_version"))
        self.parent.Bind(wx.EVT_MENU, self.OnAboutClick, id=xrc.XRCID("m_mi_about"))
        self.parent.Bind(wx.EVT_MENU, self.OpenWebsite, id=xrc.XRCID("m_mi_website"))        
        
        
        #-------------
        #plugins
        a = plugin_loader.PluginLoader(self)
        
        # options ---------------
        # load options from settings.xml
        options_window.Options(self).LoadOptions()
        if self.cb_options_tray.GetValue() == 1:
            self.parent.UseTrayIcon()
        
        # clean cache dir -------
        temp_dir = system_files.GetDirectories(self).TempDirectory()
        file_cache.CheckCache(temp_dir)
        
        # load rss feeds --------
        list_sifter.LoadRSSFeeds()
        
        # load favorites --------
        self.favorites.ReadFaves() #self.faves_playlist_location)
                
        # background image --------------------
#        background = system_files.GetDirectories(self).DataDirectory() + os.sep + 'background.png'
#        self.panel = panel
#        if os.path.isfile(background): 
#            img = wx.Image(background, wx.BITMAP_TYPE_ANY)
#            self.pbuffer = wx.BitmapFromImage(img)
#            dc = wx.BufferedDC(wx.ClientDC(self.panel), self.pbuffer)           
#            self.panel.Bind(wx.EVT_PAINT, self.OnPaint)

# ---------------------------------------------------------
#-----------------------------------------------------------

    def RandomBackgroundColour(self, event):        
        #colour_array = ('#ced1ff', '#f7b3f5', '#ff95ae', '#ffd074', '#e6ff3a', '#aaff99', '#e4e4e4')
        #rand_col = random.randint(0, (len(colour_array) - 1))
        
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            rand_col = data.GetColour().Get()
            
        
            self.panel.SetBackgroundColour(rand_col)#colour_array[rand_col])
            self.parent.SetBackgroundColour(rand_col)#colour_array[rand_col])
            self.sl_volume.SetBackgroundColour(rand_col)#colour_array[rand_col])                    
            # for updating slider background to:
            event = wx.SysColourChangedEvent()
            self.ProcessEvent(event)
            #refresh it
            self.parent.Refresh()
            
        dlg.Destroy()
        
    def OpenWebsite(self, event):        
        default_app_open.dopen('http://groove-walrus.turnip-town.net')
        
    def RateImageList(self):
        # song rating imagelist
        rate_images = wx.ImageList(16, 16, True)        
        image_files = [
            GRAPHICS_LOCATION + 'weather-clear-night.png', 
            GRAPHICS_LOCATION + 'weather-storm.png', 
            GRAPHICS_LOCATION + 'weather-overcast.png', 
            GRAPHICS_LOCATION + 'weather-few-clouds.png', 
            GRAPHICS_LOCATION + 'weather-clear.png'
            ]
        for file_name in image_files:
            bmp = wx.Bitmap(file_name, wx.BITMAP_TYPE_PNG)
            rate_images.Add(bmp)
        return rate_images
        
    def SetScrobb(self):
        # set up scrobbing
        # should only be called on loading or if you change your setttings
        self.scrobbed_track = 0
        self.scrobbed_active = 0
        username = self.tc_options_username.GetValue()
        password = self.tc_options_password.GetValue()
        if (len(username) > 0) & (len(password) > 0):
            md5_password = pylast.md5(password)
            client_id = LASTFM_CLIENT_ID
            client_version = PROGRAM_VERSION
            try:
                self.song_scrobb = pylast.Scrobbler(client_id, client_version, username, md5_password)                
                self.session_key = self.song_scrobb._get_session_id()
                self.st_options_auth.SetLabel('Authorized: ' + time.asctime())  
                self.scrobbed_active = 1
            except:
                self.st_options_auth.SetLabel('Status: something failed. User/password?')
                self.st_options_auth.SetBackgroundColour('Yellow')
                #self.nb_main.SetSelection(NB_OPTIONS)
         
    def GenerateSessionKey2(self, regenerate=False):
        # generate a non-song scrobbling seesion key
        self.session_key2 = None
        #check if scrobbling is enabled, yes: get key, no: return None
        if self.cb_options_scrobble.IsChecked():        
            username = self.tc_options_username.GetValue()
            password = self.tc_options_password.GetValue()
            if (password != '') & (username !='' ):        
                if (self.session_key2 == None) or (regenerate == True):
                    last_sess = pylast.SessionKeyGenerator(API_KEY, '6a2eb503cff117001fac5d1b8e230211')
        
                    md5_password = pylast.md5(password)
                    self.session_key2 = last_sess.get_session_key(username, md5_password)
        return self.session_key2            
                
    def OnToggleScrobble(self, event):        
        if self.cb_options_scrobble.IsChecked():
            self.lastfm_toggle.Check(False)
            self.cb_options_scrobble.SetValue(False)
            self.SaveOptions(None)
        else:
            self.lastfm_toggle.Check(True)
            self.cb_options_scrobble.SetValue(True)
            self.SaveOptions(None)
        
    def OnTimer(self, event):
        # the heartbeat of the evil machine
        #if (self.current_track >= 0) & (self.lc_playlist.GetItemCount() > 0) & (self.time_count < 2):            
        #    self.ptrack = self.lc_playlist.GetItem(self.current_track, 1).GetText()
        #    self.partist = self.lc_playlist.GetItem(self.current_track, 0).GetText()            
        
        self.pa_playback.Refresh()
        
        if self.pstatus != 'paused':
            self.time_count = self.time_count + 1
        
        # set time labels
        #if (self.st_status.GetLabelText() == 'playing'):
        #    self.st_time.SetLabel(self.ConvertTimeFormated(self.current_play_time) + ' ' + self.ConvertTimeFormated(self.time_count))
        #else:
        #    self.st_time.SetLabel(self.ConvertTimeFormated(self.current_play_time))
            
        if self.time_count >= 12000:
            self.time_count = 0
            
            
            
        # check if we should scrobb this track
        # play time around 70%
        # don't try to autherize until you've started playing a track
            
        if self.current_play_time != 0:
        
            if (self.auth_attempts == 0) & (self.scrobbed_active == 0) & (float(self.time_count) / float(self.current_play_time) > .4):
                self.auth_attempts = 1
                self.SetScrobb()
                
            if (float(self.time_count) / float(self.current_play_time) > .7) & (self.gobbled_track != 1) & (self.pstatus != "stopped"):
                #save stats for local db
                self.gobbled_track = 1
                #THREAD
                #print song_id
                ti = WebFetchThread(self, self.partist, self.ptrack, self.palbum, 'SONGINFO')
                #THREAD
                ti.start()
        
            if (float(self.time_count) / float(self.current_play_time) > .6) & (self.scrobbed_track != 1) & (self.scrobbed_active == 1) & (self.pstatus != "stopped"):
                time_started = str(int(time.time()))
                self.scrobbed_track = 1
                port = self.rx_options_scrobble_port.GetSelection()
                s_album=''
                if self.cb_options_scrobble_album.GetValue() == 1:
                    s_album=self.palbum
                #check checkbox to see if we should scrobble
                if self.cb_options_scrobble.GetValue() == 1:
                    try:
                        self.song_scrobb.scrobble(self.partist, self.ptrack, time_started, 'P', 'L', self.current_play_time, s_album, "", "", port)
                        print 'scobbled'
                        #album=""
                    except pylast.BadSession:
                        self.SetScrobb()
                        self.song_scrobb.scrobble(self.partist, self.ptrack, time_started, 'P', 'L', self.current_play_time, s_album, "", "", port)
                        #pylast.BadSession:
                        
            if self.cb_options_prefetch.GetValue() == False:
                self.prefetch = False
            if (float(self.time_count) / float(self.current_play_time) > .5) & (self.prefetch == True):
                #let's fetch the next track if possible
                self.prefetch = False                
                pf_artistsong =  prefetch.PreFetch(self).GetNextSong()
                if pf_artistsong != None:
                    pf_artist = pf_artistsong[0]
                    pf_song = pf_artistsong[1]
                    pf_cached_file_name = pf_artistsong[2]
                    print 'pre-fetching: ' + pf_song + ' ' + pf_cached_file_name
                    pf_song_id = prefetch.PreFetch(self).GetSongId(pf_artist, pf_song)
                    #print pf_song_id
                    #download file
                    if pf_song_id != None:
                        #THREAD
                        current2 = FileThread(self, pf_cached_file_name, pf_song_id, pf_song, pf_artist, album='', prefetch=True)                    
                        #THREAD
                        current2.start()
            
        # check if we should go to the next track   
        if (self.current_play_time > 0) & (self.time_count > self.current_play_time) & (self.pstatus != "stopped"):
            #print 'next-track'
            if self.current_local != None:
                self.current_local.stop()
            # stop recording if it's reecording
            #if self.recording_status == True:
                #self.recorder.stop()
                #self.recording_status = False
            playlist_total = self.lc_playlist.GetItemCount()
            if (self.repeat_toggle == True) & (self.repeat_toggle_type == 'One'):
                self.PlaySong(self.current_track)
            elif  (playlist_total - 1) > self.current_track:
                # play next track
                self.PlaySong(self.current_track + 1)
            else:
                # go back to the start, if repeat is set
                if (self.repeat_toggle) | (self.random_toggle) == True:
                    self.PlaySong(0)
                else:
                #we've reached teh end, the end my friend
                    self.pstatus = 'stopped'
                    self.SetPlayButtonGraphic('play')
        # check if we should start recording
        #print self.st_status.GetLabelText()
        #print self.cb_record.GetValue()
        #print self.time_count
        #print self.recording_status
        #if (self.st_status.GetLabelText() == 'playing') & (self.record_toggle == True) & (self.time_count > -3) & (self.time_count < 4) & (self.recording_status == False):
            #grab the bitrate we wnat to record at
            #80, 128, 192, 256, 320
            #bitrate = 1000 * int(self.ch_options_bitrate.GetStringSelection())
            #record_dir = self.bu_options_record_dir.GetLabel()
            #self.recorder.record(self.partist, self.ptrack, record_dir, bitrate)
            #self.recording_status = True
        
            
# ---------------------------------------------------------             
    def OnSearchClick(self, event):
        # search field, then search
        query_string = self.tc_search.GetValue()        
        self.SearchIt(query_string)
        
    def SearchIt(self, query_string):
        # check if we add to playlist, or open the search form
        if len(query_string) > 0:
            self.nb_main.SetSelection(NB_PLAYLIST)
            self.search_window.SetValue(query_string)
            self.search_window.SearchIt(query_string)
            self.search_window.show_me()
            self.search_window.lc_search.Select(0)
        else:
            self.search_window.show_me()
            
    def SearchAgain(self, event):
        # get currently selected playlist item, and search for it
        val = self.lc_playlist.GetFirstSelected()
        if val >= 0:
            track = self.lc_playlist.GetItem(val, 1).GetText()
            artist = self.lc_playlist.GetItem(val, 0).GetText()
            self.SearchIt(artist + ' ' + track)

            
    def ShowTab(self, location):
        # display a notebook tab or the search form
        #NB_PLAYLIST = 0
        #NB_LAST = 1
        #NB_ALBUM = 2
        #NB_FAVES = 3
        #NB_SIFT = 4
        #NB_ABOUT = 5
        #WN_SEARCH = 99
        if location < 99:
            self.nb_main.SetSelection(location)
        else:
            self.nb_main.SetSelection(NB_PLAYLIST)
            self.search_window.show_me()
        
    def OnRandomClick(self, event):
        if self.random_toggle == True:
            self.random_toggle = False
            hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'media-random.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
            self.bb_random.SetBitmapLabel(hover_bmp)
            #self.bb_random.SetWindowStyle(wx.BU_AUTODRAW)
        else:
            self.random_toggle = True
            hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'media-random-selected.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
            self.bb_random.SetBitmapLabel(hover_bmp)
            #self.bb_random.SetWindowStyle(wx.DOUBLE_BORDER)
            
    def OnRepeatClick(self, event):
        if self.repeat_toggle == True:            
            if self.repeat_toggle_type == 'One':
                self.repeat_toggle_type = 'All'
                hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'media-repeat-selected-all.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
                self.bb_repeat.SetBitmapLabel(hover_bmp)
                #self.bb_repeat.SetWindowStyle(wx.DOUBLE_BORDER)
                self.bb_repeat.SetToolTipString('Repeat: All')
            else:
                self.repeat_toggle_type = 'One'
                self.repeat_toggle = False
                hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'media-repeat.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
                self.bb_repeat.SetBitmapLabel(hover_bmp)
                #self.bb_repeat.SetWindowStyle(wx.BU_AUTODRAW)
                self.bb_repeat.SetToolTipString('Repeat')
        else:
            self.repeat_toggle = True
            hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'media-repeat-selected-one.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
            self.bb_repeat.SetBitmapLabel(hover_bmp)
            #self.bb_repeat.SetWindowStyle(wx.DOUBLE_BORDER)
            self.bb_repeat.SetToolTipString('Repeat: One')
        #print self.repeat_toggle
        #print self.repeat_toggle_type
        
    def OnRecordClick(self, event):
        if self.record_toggle == True:
            self.record_toggle = False
            hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'drive-harddisk.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
            self.bb_record.SetBitmapLabel(hover_bmp)
            #self.bb_record.SetWindowStyle(wx.BU_AUTODRAW)
        else:
            self.record_toggle = True
            hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'drive-harddisk-selected.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
            self.bb_record.SetBitmapLabel(hover_bmp)
            #self.bb_record.SetWindowStyle(wx.DOUBLE_BORDER)            
        
    def SaveOptions(self, event):
        # hide the notebook, or show it        
        options_window.Options(self).SaveOptions()
        if self.cb_options_tray.IsChecked():
            self.parent.UseTrayIcon()
        else:
            if self.parent.tray_icon != None:
                self.parent.tray_icon.Destroy
                self.parent.tray_icon = None
        
    def OnSetRecordDirClick(self, event):
        dialog = wx.DirDialog(None, "Choose a directory:")
        if dialog.ShowModal() == wx.ID_OK:
            #print dialog.GetPath()
            self.bu_options_record_dir.SetLabel(dialog.GetPath())
            self.SaveOptions(None)
        dialog.Destroy()
        #pass

    def OnExit(self, event):
        self.SavePlaylist(self.main_playlist_location)
        self.SaveOptions(event)
        self.parent.Destroy()
        
    def OnSaveOptionsClick(self, event):
        # hide the notebook, or show it
        self.SaveOptions(None)
        self.SetScrobb()
            
    def SearchOrPlaylist(self, artist, song, album='', url='', duration=''):
        # determine if we should add to playlist of search for it
        if self.rx_options_double_click.GetSelection():
            # search
            self.SearchIt(artist + " " + song)
        else:
            # add to playlist
            current_count = self.lc_playlist.GetItemCount()
            self.SetPlaylistItem(current_count, artist, song, album, url, duration)

    def CheckClear(self):
        # determine if we should clear the playlist before adding
        self.BackupList()
        if self.cb_options_list_clear.GetValue():
            self.lc_playlist.DeleteAllItems()
            self.current_track = -1
            
    def OnAboutClick(self, event):
        options_window.Options(self).ShowAbout(PROGRAM_NAME, PROGRAM_VERSION)

    def MiniMode(self, event):
        if self.nb_main.IsShown():
            self.nb_main.Show(False)
            self.parent.SetSize((690, 165))
        else:
            self.nb_main.Show(True)
            self.parent.SetSize((690, 530))
            #self.Refresh()
        #self.parent.GetMenuBar()
        #self.parent.SetMenuBar(None)
        #self.parent.Layout()
        #self.parent.SetAutoLayout(True)
        #background = 'f:/temp/a.bmp'        
        #img = wx.Image(background, wx.BITMAP_TYPE_ANY)
        #self.buffer = wx.BitmapFromImage(img)
        #dc = wx.BufferedDC(wx.ClientDC(self.panel), self.buffer)           
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    #def OnPaint(self, evt):
        #dc = wx.BufferedPaintDC(self.panel, self.buffer)
        
    def OnGSVersionClick(self, event):
        #show a dialog tat let's you change the GS Version
        dlg = wx.TextEntryDialog(self, 'Grooveshark version:', 'Grooveshark Version')
        data_dir = system_files.GetDirectories(self).DataDirectory() + os.sep
        g_version = GetLocalGroovesharkVersion(data_dir)
        if g_version == None:
            g_version = ''
        dlg.SetValue(g_version)

        if dlg.ShowModal() == wx.ID_OK:
            if g_version != dlg.GetValue():
                #save xml file
                file_name = 'grooveshark.xml'    
                if dlg.GetValue() !='':
                    #get the version number from the file
                    print 'asfasfasf'
                    data_dict = {'version':dlg.GetValue()}                    
                    read_write_xml.xml_utils().save_generic_settings(data_dir, file_name, data_dict)
        dlg.Destroy()
        
           
    def SetVolume(self, volume):
        soundmixer.SetMasterVolume(volume)
        #print self.cslid
        self.sl_volume.SetValue(volume)
        
    def OnVolumeClick(self, event):
        volume = self.sl_volume.GetValue()
        self.SetVolume(volume)
        
    def GetVolume(self):
        gvol = soundmixer.GetMasterVolume()
        if gvol == None:
            got_vol = 50
        else:
            got_vol = int(gvol)
        return got_vol
        
    def OnVolumeDown(self, event):
        cur_vol = self.GetVolume()
        if cur_vol > 10:
            volume = cur_vol - 10
        else:
            volume = 0
        self.SetVolume(volume)

    def OnVolumeUp(self, event):
        cur_vol = self.GetVolume()
        if cur_vol < 90:
            volume = cur_vol + 10
        else:
            volume = 100
        self.SetVolume(volume)
        
    def OnMuteClick(self, event):
        #just mute for now
        if self.GetVolume() == 0:
            if self.muted_volume:
                self.SetVolume(self.muted_volume)
        else:
            self.muted_volume = self.GetVolume()
            self.SetVolume(0)
        
    def OnPreviousTab(self, event):
        cur_tab = self.nb_main.GetSelection()
        if cur_tab == 0:
            new_tab = self.nb_main.GetPageCount() - 1
        else:
            new_tab = cur_tab - 1
        self.nb_main.SetSelection(new_tab)

    def OnNextTab(self, event):
        cur_tab = self.nb_main.GetSelection()
        if cur_tab == self.nb_main.GetPageCount() - 1:
            new_tab = 0
        else:
            new_tab = cur_tab + 1
        self.nb_main.SetSelection(new_tab)
        
    def ResetPosition(self, event):
        # reset the frame position to something sane
        self.parent.SetPosition((20,20))
        
    def OnAlbumCoverClick(self, event):
        is_shown = self.album_viewer.ToggleShow()
        # set check mark on main menu item
        #if is_shown:
        #    check_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'checkmark.png', wx.BITMAP_TYPE_ANY)
        #    self.parent.mi_album_cover.SetBitmap(check_bmp)
        #else:
        #    xrc.XRCCTRL(self.parent, 'm_mi_album_cover').SetBitmap(None)

    def OnUpdateClick(self, event):
        # open website
        version_check.VersionCheck(self, PROGRAM_VERSION).DisplayNewVersionMessage()

# --------------------------------------------------------- 
# play click events---------------------------------------- 
    def OnPlayClick(self, event):
        #handles playing and pausing        

        if self.pstatus == 'paused':
            self.TogglePause()
            self.pstatus = 'playing'
            self.SetPlayButtonGraphic('pause')            
        elif (self.pstatus == 'playing'):
            self.TogglePause()
            self.pstatus = 'paused'
            self.SetPlayButtonGraphic('play')
        else:
            val = self.lc_playlist.GetFirstSelected()
            if val >= 0:
                #print val
                self.PlaySong(val)
                self.SetPlayButtonGraphic('pause')
            elif self.lc_playlist.GetItemCount() >=1:
                self.PlaySong(0)
                self.SetPlayButtonGraphic('pause')
                
    def SetPlayButtonGraphic(self, playorpause):
        
        play_button = xrc.XRCCTRL(self, 'm_bb_play')
        pause_bmp = wx.Bitmap(GRAPHICS_LOCATION + "media-playback-pause.png", wx.BITMAP_TYPE_ANY)
        play_bmp = wx.Bitmap(GRAPHICS_LOCATION + "media-playback-start.png", wx.BITMAP_TYPE_ANY)
        bmp = pause_bmp
        if playorpause == 'play':
            bmp = play_bmp        
        play_button.SetBitmapLabel(bmp)
            
    def TogglePause(self):
        if self.current_local != None:
            self.current_local.pause()
            
    def OnPlayListPlayClick(self, event):
        # get selected search relsult list item and add to playlist
        val = self.lc_playlist.GetFirstSelected()
        if val >= 0:
            self.PlaySong(val, True)
            self.SetPlayButtonGraphic('pause')
            
    def OnStopClick(self, event):
        # stop local thread
        if self.current_local != None:
            self.current_local.stop()
            
        self.StopFlashSong()
        # destory the flash window and rebuild it
        #try:
        #    self.flash.Destroy()
        #except wx._core.PyDeadObjectError:
        #    pass        
        #self.flash = FlashWindow(self.pa_player, style=wx.NO_BORDER)#, size=(20, 20))
        
        self.pstatus = 'stopped'
        self.download_percent = 0
        
        self.SetPlayButtonGraphic('play')
        #try:
        #    self.recorder.stop()
        #except AttributeError:
        #    pass
        #self.recording_status = False
        
    def LoadFlashSong(self, url, artist, track):
        #
        #print url
        #print self.web_music_type
        if self.web_music_type != "GrooveShark":
            #print self.web_music_url + artist + '-' + track
            self.flash.movie = self.web_music_url + artist + '-' + track
        else:
            self.flash.movie = url

    def StopFlashSong(self):
        #
        if self.use_web_music == True:
            self.flash.movie = 'temp.swf'
        #pass
            
    def OnForwardClick(self, event):
        # skip to the next rack on the playlist
        val = self.lc_playlist.GetFirstSelected()
        if (val >= 0) & (val < (self.lc_playlist.GetItemCount() - 1)):
            # print val
            self.PlaySong(val + 1)
        elif val >= 0:
            self.PlaySong(0)
        else:
            #nothing is slected
            self.PlaySong(0)
            
    def OnBackwardClick(self, event):
        # skip to the next rack on the playlist
        val = self.lc_playlist.GetFirstSelected()
        if (val > 0):
            # print val
            self.PlaySong(val - 1)
        elif val == 0:          
            self.PlaySong(self.lc_playlist.GetItemCount() - 1)
        else:
            #nothing is slected
            self.PlaySong(0)
            
# --------------------------------------------------------- 
# play functions------------------------------------------- 
    def PlaySong(self, playlist_number, clicked=False):
        # play passed song, clicked = True if user clicked to play
        if self.current_local != None:
            self.current_local.stop()
        if self.use_web_music == True:
            self.StopFlashSong()
        
        self.gobbled_track = 0
        #self.ga_download.SetValue(0)
        self.download_percent = 0
        self.prefetch = True

                                 
        # check for random
        if (self.random_toggle == True) & (clicked == False):
            playlist_number = random.randint(0, (self.lc_playlist.GetItemCount() - 1))
            # picks the same song again doesn't reload the flash file

        # verfiy that playlist number is valid:
        if playlist_number > (self.lc_playlist.GetItemCount() -1):
            playlist_number = 0
        self.lc_playlist.Focus(playlist_number)
        
        # lets check to see if there's a song id
        # if not, search, and then play -> play on demand
        # otherwise lets just play the song
                
        track = self.lc_playlist.GetItem(playlist_number, 1).GetText()
        artist = self.lc_playlist.GetItem(playlist_number, 0).GetText()
        album = self.lc_playlist.GetItem(playlist_number, 2).GetText()
        duration = self.lc_playlist.GetItem(playlist_number, 4).GetText()
        lolight = (110, 207, 106, 255)
        medlight = (200, 100, 150, 255)        
        song_id = str(self.lc_playlist.GetItem(playlist_number, 3).GetText())
        #print song_id
        #old_groove_id = ''
        if os.path.isfile(song_id) == False:            
            if song_id.isdigit() == True:
                pass
            #    old_groove_id = song_id
            #check whether to keep the existing groveshark id
            else:
                song_id = ''
        else:
            query_string = artist + ' ' + track
            query_results = local_songs.DbFuncs().GetResultsArray(query_string, 1, True)
            if len(query_results) == 1:
                self.pmusic_id = query_results[0][0]
                self.pgroove_id = 0
        
        
        
        if album=='':            
            album_array = musicbrainz.Brainz().get_song_info(artist, track)
            album = album_array[1]
            self.lc_playlist.SetStringItem(playlist_number, 2, album)
            self.SavePlaylist(self.main_playlist_location)
        
        if (song_id =='') & (len(artist) > 0) & (len(track) > 0):
            # query for song id, so we can play the file
            #print "no song id"
            query_string = artist + ' ' + track
            
            # check locally for song
            #query_results = local_songs.GetResults(query_string, 1)
            query_results = local_songs.DbFuncs().GetResultsArray(query_string, 1, True)
            #GetResultsArray(query, qlimit, with_count=False, folder_query=1)
            if len(query_results) == 1:
                #song_id = str(query_results[0])
                song_id = str(query_results[0][4])
                self.pmusic_id = query_results[0][0]
                self.pgroove_id = 0
            #check if file exists
            if os.path.isfile(song_id):
                self.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                loc_album = local_songs.GetMp3Album(song_id)
                if len(loc_album) >= 1:
                    album = loc_album
                    self.lc_playlist.SetStringItem(playlist_number, 2, album)
                self.SavePlaylist(self.main_playlist_location)
            # try grooveshark
            else:
                query_results = tinysong.Tsong().get_search_results(query_string, 32)
                split_array = query_results[0].split('; ')
                if len(split_array) >= 2:                
                    # song id is at [1] - 4,2,6,1
                    song_id = split_array[1]
                    # let's check for album and update that too
                    if (album =='') & (split_array[6] != ''):
                        album = split_array[6]
                        self.lc_playlist.SetStringItem(playlist_number, 2, album)
                    #print artist
                    #print split_array[4]
                    
                    # check for song match
                    if track.upper() != split_array[2].upper():
                        #cylce through results to see if we can get and exact match
                        #otherwise use the first result
                        found_it = False
                        for x in range(1, len(query_results) - 1):
                            y = query_results[x].split('; ')
                            #print y
                            if (y[2].upper() == track.upper()) & (found_it != True):
                                song_id = y[1]
                                self.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                                self.SavePlaylist(self.main_playlist_location)
                                found_it = True                           
                    
                    # check for artist match
                    if artist.upper() != split_array[4].upper():
                        # cycle through till will hit the right artist
                        found_it = False
                        for x in range(1, len(query_results) - 1):
                            y = query_results[x].split('; ')
                            #print y
                            if (y[4].upper() == artist.upper()) & (found_it != True):
                                song_id = y[1]
                                self.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                                self.SavePlaylist(self.main_playlist_location)
                                found_it = True
                        if found_it == False:
                            self.lc_playlist.SetItemBackgroundColour(playlist_number, lolight)                    
                            # don't scrobb the wrong song
                            self.scrobbed_track = 1
                            self.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                    #update playlist
                    else:
                        self.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                        self.SavePlaylist(self.main_playlist_location)
                else:
                    # we fucked
                    #print "no search results -- fucked"
                    self.lc_playlist.SetItemBackgroundColour(playlist_number, medlight)
                    self.pstatus = 'stopped'
                    
                    # *** skip to next track
                    
                # set negative so it has time to load
        
        # throw together a url      
        url = PLAY_SONG_URL + song_id
        ###if self.cb_options_alternate.GetValue():
        ### disabled, no real need for this, i think?
            #use the main page instead of the widget
            # http://listen.grooveshark.com/#/song/One/21880276            
            ###url = PLAY_SONG_ALTERNATE_URL + song_id
        #print url    
        
        #get song time
        if (duration =='') or (duration == '0:00'):
            if (song_id.endswith('.mp3') == True):
                track_time = local_songs.GetMp3Length(song_id)
            else:
                track_time = musicbrainz.Brainz().get_song_time(artist, track)
                #print track_time
                #print artist
                #print track
            self.lc_playlist.SetStringItem(playlist_number, 4, self.ConvertTimeFormated(track_time))
            self.SavePlaylist(self.main_playlist_location)
        else:           
            track_time = self.ConvertTimeSeconds(duration)
            
        
        self.current_play_time = track_time
        if track_time == 0:
            #guess that the song is about 200 seconds
            #self.current_play_time = 200
            wminutes = self.sc_options_song_minutes.GetValue()
            wseconds = self.sc_options_song_seconds.GetValue()
            wformated_time = str(wminutes) + ':' + str(wseconds)            
            self.current_play_time = self.ConvertTimeSeconds(wformated_time)
            #track_time = 200
            # change the list item colour, so user can go fix the details later
            ##highlight = (255, 210, 0, 255)            
            ##self.lc_playlist.SetItemBackgroundColour(playlist_number, highlight)
            
        # unselect last played 
        self.lc_playlist.Select(self.current_track, 0)
        
        self.current_track = playlist_number
        #print track_time
        if (self.use_web_music == True) & ((len(song_id) >= 1) & (len(song_id.split('/')) < 2)):
            print 'webmusic'
            self.time_count = self.sc_options_gs_wait.GetValue() * -1
            
            self.LoadFlashSong(url, artist, track)            

            #self.st_track_info.SetLabel(artist + ' - ' + track)
            self.pstatus = 'playing'
            self.pgroove_id = song_id
            self.pmusic_id = 0
            
        elif (len(song_id) >= 1) & (len(song_id.split('/')) < 2):
        #grooveshark song
            self.time_count = -1            
            
            temp_dir = system_files.GetDirectories(self).TempDirectory()
            file_name_plain = artist + '-' + track + '.mp3'
            # clean cache dir
            file_cache.CheckCache(temp_dir)
            # check if file previously cached
            cached_file = file_cache.CreateCachedFilename(temp_dir, file_name_plain)
            cached_file_name = cached_file[0]
            if cached_file[1] == False:
                # download it                 
                
                # file size
                ##g_session = jsonrpcSession()
                ##g_session.startSession()
                ##g_data = {'SongID': song_id, 'Name': track, 'ArtistName': artist, 'AlbumName': album, 'AlbumID': '', 'ArtistID': ''}
                ##g_song = song.songFromData(g_session, g_data)
                ##g_song.getStreamDetails()                
                ##file_size = grooveshark_old.Grooveshark(self).GetFileSize(g_song._lastStreamKey, g_song._lastStreamServer)
                
                
                #streamkey/stream server
                ###x,y = self.groove_session.songKeyfromID(song_id)
                ##g_session = jsonrpcSession()
                ##g_session.startSession()    
                #g_data = {'SongID': song_id, 'Name': track, 'ArtistName': artist, 'AlbumName': album, 'AlbumID': '', 'ArtistID': ''}
                ##g_song = song.songFromData(g_session, g_data)
                #getStreamDetails(song_id)
                ##g_song.getStreamDetails()
                #print g_song._lastStreamServer            
                
                #download file
                #THREAD
                current = FileThread(self, cached_file_name, song_id, track, artist, album)
                ##current = FileThread(self, g_song._lastStreamKey, g_song._lastStreamServer, cached_file_name, file_size)
                #THREAD
                current.start()
            else:
                self.current_play_time = local_songs.GetMp3Length(cached_file_name)
                                
            #play song
            #THREAD
            #print song_id
            self.current_local = WebFetchThread(self, '', cached_file_name, '', 'PLAYLOCAL')
            #THREAD
            self.current_local.start()            

            #self.st_track_info.SetLabel(artist + ' - ' + track)
            self.pstatus ='playing'
            self.pgroove_id = song_id
            self.pmusic_id = 0
        elif os.path.isfile(song_id): #len(song_id) > 2 & (len(song_id.split('/')) > 1):
        # local file
            self.time_count = -2            
            #THREAD
            #print song_id
            self.current_local = WebFetchThread(self, '', song_id, '', 'PLAYLOCAL')
            #THREAD
            self.current_local.start()
            #print self.current_local
            #self.st_track_info.SetLabel(artist + ' - ' + track)
            self.pstatus = 'playing'

        else:
             self.scrobbed_track = 1
             self.pstatus = 'stopped'
             
        if self.pstatus == 'playing':
            self.parent.SetTitle(artist + '-' + track + ' - ' + PROGRAM_NAME + ' ' + PROGRAM_VERSION)
            self.lc_playlist.Select(playlist_number)
            if os.name == 'nt':
                self.GetSongArt(artist, album)
                self.GetArtistBio(artist)
            self.ptrack = track
            self.partist = artist
            self.palbum = album
            self.scrobbed_track = 0
             

        
    def ConvertTimeFormated(self, seconds):
        # convert seconds to mm:ss
        return str(float(seconds) / float(60)).split('.')[0] + ':' + str(abs(seconds) % 60).zfill(2)
        
    def ConvertMilliTimeFormated(self, milliseconds):
        seconds = int(milliseconds) / 1000
        return self.ConvertTimeFormated(seconds)
        
    def ConvertTimeSeconds(self, formated_time):
        # convert mm:ss to seconds
        return (int(formated_time.split(':')[0]) * 60) + (int(formated_time.split(':')[1]))

    def ConvertTimeMilliSeconds(self, formated_time):
        # convert mm:ss to seconds
        return self.ConvertTimeSeconds(formated_time) * 1000
        
# ---------------------------------------------------------  
# playlist-------------------------------------------------          
    def SavePlaylist(self, filename='MAIN'):
        if filename == 'MAIN':
            filename = self.main_playlist_location
        # take current playlist and save to xml file
        track_dict = []
        #print self.lc_playlist.GetItemCount()
        for x in range(0, self.lc_playlist.GetItemCount()):
            #print x
            artist = self.lc_playlist.GetItem(x, 0).GetText()
            title = self.lc_playlist.GetItem(x, 1).GetText()
            album = self.lc_playlist.GetItem(x, 2).GetText()
            song_id = self.lc_playlist.GetItem(x, 3).GetText()
            if len(song_id.split('/')) > 1:
                song_id = "file:///" + song_id
                song_id = song_id.replace(' ', '%20')
            elif len(song_id) > 1:
                song_id = "http://grooveshark.com/" + song_id
            song_time = ''
            if len(self.lc_playlist.GetItem(x, 4).GetText()) > 0:
                song_time = str(self.ConvertTimeMilliSeconds(self.lc_playlist.GetItem(x, 4).GetText()))
            track_dict.append({'creator': artist, 'title': title, 'album': album, 'location': song_id, 'duration': song_time})
            
        read_write_xml.xml_utils().save_tracks(filename, track_dict)        
        
    def OnClearPlaylistClick(self, event):
        # clear playlist
        self.BackupList()
        self.lc_playlist.DeleteAllItems()
        self.nb_main.SetPageText(NB_PLAYLIST, 'Playlist (0)')
                
    def OnLoadPlaylistClick(self, evt):
        wildcard = "Music Files (*.xspf;*.m3u;*.mp3)|*.xspf;*.m3u;*.mp3|"   \
            "Playlist (*.xspf)|*.xspf|"     \
            "Winamp Playlist (*.m3u)|*.m3u|"     \
            "MP3 (*.mp3)|*.mp3"
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.playlist_save_location, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )# wx.MULTIPLE | 

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            print paths
            self.BackupList()
            self.lc_playlist.DeleteAllItems()
            for path in paths:                
                if path.endswith('.xspf'):
                    self.ReadPlaylist(path)
                elif path.endswith('.m3u'):
                    self.ReadWinampPlaylist(path)
                elif path.endswith('.mp3'):                  
                    self.ScolFileAdd(path)
                else:
                    pass
        dlg.Destroy()
        
    #def list_dir(self, directory):
        # grab file list
        #pathlist = os.listdir(directory)
        # Now filter out all but py and pyw
        #filterlist = [x for x in pathlist if x.endswith('.xspf')]
        #return filterlist
        
    def OnSavePlaylistClick(self, event):
        wildcard = "Playlist (*.xspf)|*.xspf|"
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=self.playlist_save_location, 
            defaultFile="", wildcard=wildcard, style=wx.SAVE
            )

        # This sets the default filter that the user will initially see. Otherwise,
        # the first filter in the list will be used by default.
        dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            #print path
            self.SavePlaylist(path) 
        dlg.Destroy()
                
    def ReadWinampPlaylist(self, filename):
        # take current playlist and write to listcontrol        
        f = open(filename)
        #print filename
        clean_path = filename.replace(os.sep, '/').rsplit('/', 1)[0]
        counter = 0
        try:
            for line in f:
                if line[0] != '#':
                    filen = clean_path + '/' + line.strip()
                    self.lc_playlist.InsertStringItem(counter, local_songs.GetMp3Artist(filen))
                    self.lc_playlist.SetStringItem(counter, 1, local_songs.GetMp3Title(filen))
                    self.lc_playlist.SetStringItem(counter, 2, local_songs.GetMp3Album(filen))
                    self.lc_playlist.SetStringItem(counter, 3, filen)
                    counter = counter + 1
        finally:
            f.close()
        self.SavePlaylist(self.main_playlist_location)
        self.ResizePlaylist()
        
    def ReadPlaylist(self, filename):
        # take current playlist and write to listcontrol
        track_dict = read_write_xml.xml_utils().get_tracks(filename)
        counter = 0
        #print track_dict
        for x in track_dict:
            #print x
            #set value
            try:
                index = self.lc_playlist.InsertStringItem(counter, x['creator'])
                self.lc_playlist.SetStringItem(counter, 1, x['title'])
                album = x['album']
                if album == None:
                    album = ''
                self.lc_playlist.SetStringItem(counter, 2, album)
                
                song_id = x['location']
                if song_id == None:
                    song_id = ''
                # *** this should be case insensitive File: <> file:
                song_id = song_id.split('file:///')[-1]
                song_id = song_id.split('http://grooveshark.com/')[-1]
                song_id = song_id.replace('%20', ' ')
                self.lc_playlist.SetStringItem(counter, 3, song_id)
                
                song_time = x['duration']
                if song_time == None:
                    song_time = ''
                if song_time.isdigit():
                    # convert milliseconds to formated time mm:ss
                    song_time = self.ConvertMilliTimeFormated(song_time)
                self.lc_playlist.SetStringItem(counter, 4, song_time)
                counter = counter + 1
            except TypeError:
                print 'error:ReadPlaylist'
                #pass
        self.ResizePlaylist()
        
    def OnPlaylistRightClick(self, event):        
        # make a menu
        ID_DELETE = 1
        ID_SEARCH = 2
        ID_FAVES = 3
        ID_FIX = 4
        ID_FIX_ALBUM = 5
        ID_CLEAR = 6
        ID_SHARE = 7
        
        menu = wx.Menu()
        menu.Append(ID_FAVES, "Add to Favorites")
        menu.Append(ID_SHARE, "Clipboard Share Link")
        menu.AppendSeparator()
        menu.Append(ID_SEARCH, "Find Better Version")        
        menu.Append(ID_FIX, "Song Details")
        menu.Append(ID_FIX_ALBUM, "Auto-Fix Album")
        menu.AppendSeparator()
        menu.Append(ID_CLEAR, "Clear Id")
        menu.Append(ID_DELETE, "Delete")
        
        wx.EVT_MENU(self, ID_DELETE, self.RemovePlaylistItem)
        wx.EVT_MENU(self, ID_SEARCH, self.SearchAgain)
        wx.EVT_MENU(self, ID_FAVES, self.favorites.OnPlaylistFavesClick)
        wx.EVT_MENU(self, ID_FIX, self.FixPlaylistItem)
        wx.EVT_MENU(self, ID_FIX_ALBUM, self.FixAlbumName)
        wx.EVT_MENU(self, ID_CLEAR, self.ClearId)
        wx.EVT_MENU(self, ID_SHARE, self.MakeShareLink)
        
        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()
        
    def RemovePlaylistItem(self, event=None):
        self.BackupList()
        # remove slected list item
        val = self.lc_playlist.GetFirstSelected()
        # iterate over all selected items and delete
        #print self.lc_playlist.GetSelectedItemCount()
        for x in range(val, val + self.lc_playlist.GetSelectedItemCount()):
            #print 'dete - ' + str(val)
            #self.lc_playlist.DeleteItem(val)
            self.lc_playlist.DeleteItem(self.lc_playlist.GetFirstSelected())
        # save default playlist
        self.SavePlaylist(self.main_playlist_location)
        self.ResizePlaylist()
                
    def FixPlaylistItem(self, event):
        # display the song steails window
        if self.lc_playlist.GetFirstSelected() >= 0:
            details_window.DetailsWindow(self).show_me()
            
    def ClearId(self, event):
        # display the song steails window
        val = self.lc_playlist.GetFirstSelected()
        self.lc_playlist.SetStringItem(val, 3, '')
        
    def FixAlbumName(self, event):
        # *** should be moved work when checking for cover art
        val = self.lc_playlist.GetFirstSelected()
        artist = self.lc_playlist.GetItem(val, 0).GetText()
        song = self.lc_playlist.GetItem(val, 1).GetText()
        album_array = self.GetSongAlbumInfo(artist, song)
        #album_array[1] is album name
        self.lc_playlist.SetStringItem(val, 2, album_array[1])
        #save playlist
        self.SavePlaylist(self.main_playlist_location)
        self.ResizePlaylist()
        
    def UpdatePlaylistItem(self, current_count, artist, song, album, url, duration=''):
        #set value
        self.lc_playlist.SetStringItem(current_count, 0, artist)
        self.lc_playlist.SetStringItem(current_count, 1, song)
        self.lc_playlist.SetStringItem(current_count, 2, album)
        self.lc_playlist.SetStringItem(current_count, 3, url)
        self.lc_playlist.SetStringItem(current_count, 4, duration)
        self.ResizePlaylist()
        self.SavePlaylist(self.main_playlist_location)
        
    def SetPlaylistItem(self, current_count, artist, song, album='', url='', duration=''):
        #set value
        index = self.lc_playlist.InsertStringItem(current_count, artist)
        self.lc_playlist.SetStringItem(current_count, 1, song)
        self.lc_playlist.SetStringItem(current_count, 2, album)
        self.lc_playlist.SetStringItem(current_count, 3, url)
        self.lc_playlist.SetStringItem(current_count, 4, duration)
        self.ResizePlaylist()
        
    def ResizePlaylist(self, event=None):
        #x_size = self.lc_playlist.GetSize()[0] - 50
        self.lc_playlist.SetColumnWidth(0, 160)#x_size*.29)
        self.lc_playlist.SetColumnWidth(1, 210)#x_size*.40)
        self.lc_playlist.SetColumnWidth(2, 145)#x_size*.29)
        self.lc_playlist.SetColumnWidth(3, 0)
        self.lc_playlist.SetColumnWidth(4, 50)#wx.LIST_AUTOSIZE_USEHEADER)
        self.nb_main.SetPageText(NB_PLAYLIST, 'Playlist (' + str(self.lc_playlist.GetItemCount()) + ')')
        #if event:
        #    event.Skip()
        
    def MakeShareLink(self, event):
        # make link for current song/artist, copy to clippboard
        val = self.lc_playlist.GetFirstSelected()
        artist = "a=" + self.lc_playlist.GetItem(val, 0).GetText().replace(' ', '%20')
        song = "&s=" + self.lc_playlist.GetItem(val, 1).GetText().replace(' ', '%20')
        song_link = SONG_SENDER_URL + artist + song
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(song_link))
        wx.TheClipboard.Close()
        
    def ClearAlbumValues(self, event):
        # clear all the album values on the playlist
        for x in range(0, self.lc_playlist.GetItemCount()):
            self.lc_playlist.SetStringItem(x, 2, '')
        
# --------------------------------------------------------- 
# edit menu  ----------------------------------------------

    def GetSelectedList(self):
        #figure out which list is selected, playslist or favourites
        if self.lc_playlist.IsShownOnScreen():
            return self.lc_playlist
        if self.lc_faves.IsShownOnScreen():
            return self.lc_faves

    def OnDeletePress(self, event=None):
        #check which listctrl is visable
        #save list for undo
        #delete items(s)
        #check if it's the delete key
         if event.GetKeyCode() == wx.WXK_DELETE:
            if self.lc_playlist.IsShownOnScreen():
                self.RemovePlaylistItem()
            #if self.lc_faves.IsShownOnScreen():
                #self.RemoveFavesItem()
                
    def OnDeleteClick(self, event=None):
        #check which listctrl is visable
        #save list for undo
        #delete items(s)
        #check if it's the delete key
        if self.lc_playlist.IsShownOnScreen():
            self.RemovePlaylistItem()
            #if self.lc_faves.IsShownOnScreen():
                #self.RemoveFavesItem()
            
    def OnKeyUp(self, event):
        print 'key'
            
    def OnCopyClick(self, event=None):
        # copy list items
        sel_list = self.GetSelectedList()
        if sel_list != None:
            val = sel_list.GetFirstSelected()
            next_val = val
            # iterate over all selected items and copy
            self.copy_array = []
            for x in range(val, val + sel_list.GetSelectedItemCount()):
                list_arr = []
                for y in range(0, sel_list.GetColumnCount()):
                    list_arr.append(sel_list.GetItem(next_val, y).GetText())
                next_val = sel_list.GetNextSelected(next_val)
                self.copy_array.append(list_arr)
            #print self.copy_array
        
    def OnCutClick(self, event):
        self.OnCopyClick()
        self.OnDeleteClick()        

    def OnPasteClick(self, event):
        #get the list to paste to
        self.BackupList()
        sel_list = self.GetSelectedList()
        if sel_list == self.lc_playlist:
            #cycle through copied items and paste
            for x in range(0, len(self.copy_array)):
                cur_item = sel_list.GetItemCount()
                index = sel_list.InsertStringItem(cur_item, self.copy_array[x][0])
                for y in range(1, len(self.copy_array[0])):                
                    sel_list.SetStringItem(cur_item, y, self.copy_array[x][y])

    def OnUndoClick(self, event):
        #toggle between loading default playlist and backup playlist
        #load playlist backup file        
        if self.lc_playlist.IsShownOnScreen():
            self.lc_playlist.DeleteAllItems()
            if self.undo_toggle == 0:
                self.ReadPlaylist(self.main_playlist_location_bak)
                self.undo_toggle = 1
            else:
                self.ReadPlaylist(self.main_playlist_location)
                self.undo_toggle = 0
        #if self.lc_faves.IsShownOnScreen():
        #    self.lc_faves.DeleteAllItems()
        #    if self.undo_toggle_faves == 0:
        #        self.ReadFaves(self.faves_playlist_location_bak)
        #        self.undo_toggle_faves = 1
        #    else:
        #        self.ReadFaves(self.faves_playlist_location)
        #        self.undo_toggle_faves = 0        
        
    def BackupList(self):
        #if self.lc_faves.IsShownOnScreen():
         #   self.SaveFaves(self.faves_playlist_location_bak)
        #    self.undo_toggle_faves = 0
        #else: # self.lc_playlist.IsShownOnScreen():
        self.SavePlaylist(self.main_playlist_location_bak)
        self.undo_toggle = 0
        
# --------------------------------------------------------- 
# My last.fm ----------------------------------------------
    def OnMyLastClearClick(self, event):
        # clear lastfm search field
        self.tc_mylast_search_user.Clear()

    def OnMyLastSearchClick(self, event):
        # search for user
        user = self.tc_mylast_search_user.GetValue()
        tperiod = self.rx_mylast_period.GetSelection()
        if user != '':
            top_tracks_list = audioscrobbler_lite.Scrobb().make_user_top_songs(user, tperiod)
            self.GenerateScrobbList2(top_tracks_list)
            
    def OnMyLastMeClick(self, event):
        # search for user
        user = self.tc_options_username.GetValue()
        tperiod = self.rx_mylast_period.GetSelection() 
        if user != '':
            top_tracks_list = audioscrobbler_lite.Scrobb().make_user_top_songs(user, tperiod)
            self.GenerateScrobbList2(top_tracks_list)
            
    def OnMyLastFriendsClick(self, event):
        # search for user
        user = self.tc_options_username.GetValue()
        if user != '':
            top_tracks_list = audioscrobbler_lite.Scrobb().get_friends(user)
            self.GenerateScrobbList2(top_tracks_list)
            
    def OnMyLastNeighClick(self, event):
        # search for user
        user = self.tc_options_username.GetValue()
        if user != '':
            top_tracks_list = audioscrobbler_lite.Scrobb().get_neighbours(user)
            self.GenerateScrobbList2(top_tracks_list)
            
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
                       
    def GenerateScrobbList2(self, top_list, albums=False, artists=False):
        # put some data in a list control
        counter = 0
        self.lc_mylast.DeleteAllItems()
        for x in top_list:
            if len(x) == 3:
                # just printing artist/song
                self.lc_mylast.InsertStringItem(counter, x[1])
                self.lc_mylast.SetStringItem(counter, 1, x[0])
                self.lc_mylast.SetStringItem(counter, 2, '')
                self.lc_mylast.SetStringItem(counter, 3, x[2])
            if len(x) == 2:
                self.lc_mylast.InsertStringItem(counter, '')
                self.lc_mylast.SetStringItem(counter, 1, '')
                self.lc_mylast.SetStringItem(counter, 2, x[0])
                self.lc_mylast.SetStringItem(counter, 3, x[1])
            #self.lc_lastfm.SetItemData(counter, x[1] + ':' + x[0])
            counter = counter + 1
               
        self.lc_mylast.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lc_mylast.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.lc_mylast.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.lc_mylast.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        #self.nb_main.SetPageText(2, 'last.fm (' + str(counter) + ')')
            
        
    def OnMyLastListClick(self, event):
        # past the artist + track in the search field
        val = self.lc_mylast.GetFirstSelected()
        user = self.lc_mylast.GetItem(val, 2).GetText()
        #set new value        
        self.tc_mylast_search_user.SetValue(user)
        
    def OnMyLastListDoubleClick(self, event):
        # past the artist + track in the search field
        val = self.lc_mylast.GetFirstSelected()
        artist = self.lc_mylast.GetItem(val, 0).GetText()
        song = self.lc_mylast.GetItem(val, 1).GetText()
        user = self.lc_mylast.GetItem(val, 2).GetText()
        #search for selected song, or album if song is empty
        if song != '':
            # search for db-clicked song
            self.SearchOrPlaylist(artist, song)            
        if len(user) > 0:
            # display the details for the clicked user
            self.OnMyLastSearchClick(None)
        if (len(song) == 0) & (len(artist) > 0):
            # get the top songs for the selected artist
            self.nb_main.SetSelection(NB_LAST)            
            top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_song_list(artist)
            self.GenerateScrobbList(top_tracks_list)
            
    def OnAutoGenerateMyLastPlayist(self, event):
        # lets just add all the items to your playlist
        # search for song from groove shark on demand, ie, when you go to play it?
        self.CheckClear()       
        insert_at = self.lc_playlist.GetItemCount()
        for x in range(self.lc_mylast.GetItemCount(), 0, -1):
            artist = self.lc_mylast.GetItem(x-1, 0).GetText()
            song = self.lc_mylast.GetItem(x-1, 1).GetText()
            # skip if there's no song title
            if song != '':
                self.SetPlaylistItem(insert_at, artist, song, '', '')
        #save the playlist
        self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        self.nb_main.SetSelection(NB_PLAYLIST)
        
    def OnMyLastWebClick(self, event):
        # open website
        lw = 'http://www.last.fm/user/'        
        if len(self.tc_mylast_search_user.GetValue()) > 0:
            address = lw + self.tc_mylast_search_user.GetValue()
        elif len(self.tc_options_username.GetValue()) > 0:
            address = lw + self.tc_options_username.GetValue()
        else:
            address = lw
        default_app_open.dopen(address)
        
    def OnMyLastRightClick(self, event):
        val = self.lc_mylast.GetFirstSelected()
        if val != -1:
            if (self.lc_mylast.GetItem(val, 0).GetText() != '') & (self.lc_mylast.GetItem(val, 1).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 1
                ID_CLEAR = 2
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")
                menu.AppendSeparator()
                menu.Append(ID_CLEAR, "Clear Playlist")
                wx.EVT_MENU(self, ID_PLAYLIST, self.MyLastAddPlaylist)
                wx.EVT_MENU(self, ID_CLEAR, self.OnClearPlaylistClick)       
                self.PopupMenu(menu)
                menu.Destroy()
  
    def MyLastAddPlaylist(self, event):
        self.BackupList()
        val = self.lc_mylast.GetFirstSelected()
        total = self.lc_mylast.GetSelectedItemCount()
        current_count = self.lc_playlist.GetItemCount()
        #print val
        if (val >= 0):            
            artist =    self.lc_mylast.GetItem(val, 0).GetText()
            song =      self.lc_mylast.GetItem(val, 1).GetText()
            self.SetPlaylistItem(current_count, artist, song, '', '')
            current_select = val
            if total > 1:
                for x in range(1, self.lc_mylast.GetSelectedItemCount()):
                    current_select =    self.lc_mylast.GetNextSelected(current_select)
                    artist =            self.lc_mylast.GetItem(current_select, 0).GetText()
                    song =              self.lc_mylast.GetItem(current_select, 1).GetText()                    
                    self.SetPlaylistItem(current_count + x, artist, song, '', '')

        #save the playlist
        self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        #self.nb_main.SetSelection(NB_PLAYLIST)
        
# --------------------------------------------------------- 
# last.fm ------------------------------------------------- 

    def GetLastThree(self):
        # figure out where we should get the artist/song/ablum info to search on
        artist = self.tc_last_search_artist.GetValue()        
        if len(artist) == 0:
            artist = self.partist #st_track_info.GetLabel().split(' - ', 1)[0]
            
        song = self.tc_last_search_song.GetValue()        
        if len(song) == 0:
            song = self.ptrack #st_track_info.GetLabel().split(' - ', 1)
                
        album = self.tc_last_search_album.GetValue()
        return artist, song, album

    def OnClearLastSearchClick(self, event):
        # clear lastfm search field
        self.tc_last_search_artist.Clear()
        self.tc_last_search_album.Clear()
        self.tc_last_search_song.Clear()

    def OnLastfmListClick(self, event):
        # past the artist + track in the search field
        val = self.lc_lastfm.GetFirstSelected()
        artist = self.lc_lastfm.GetItem(val, 0).GetText()
        song = self.lc_lastfm.GetItem(val, 1).GetText()
        album = self.lc_lastfm.GetItem(val, 2).GetText()
        tag = self.lc_lastfm.GetItem(val, 4).GetText()
        #set new value        
        self.tc_last_search_artist.SetValue(artist)
        self.tc_last_search_song.SetValue(song)
        self.tc_last_search_album.SetValue(album)
        self.co_last_tag.SetValue(tag)
        
    def OnLastfmListDoubleClick(self, event):
        # past the artist + track in the search field
        val = self.lc_lastfm.GetFirstSelected()
        artist = self.lc_lastfm.GetItem(val, 0).GetText()
        song = self.lc_lastfm.GetItem(val, 1).GetText()
        album = self.lc_lastfm.GetItem(val, 2).GetText()
        tag = self.lc_lastfm.GetItem(val, 4).GetText()
        #search for selected song, or album if song is empty
        if song != '':
            # search for db-clicked song
            #self.tc_search.SetValue(artist + ' ' + song)
            #self.SearchIt(artist + ' ' + song)
            self.SearchOrPlaylist(artist, song)
            # display search page
            #self.nb_main.SetSelection(NB_PLAYLIST)
            #self.lc_search.SetFocus()
            #self.search_window.lc_search.Select(0)
        elif (len(song) == 0) & (len(album) != 0):
            # display the details for the clicked album
            # get all the tracks in teh album and display on the album page
            track_stuff = self.GetAlbumAlbumInfo(artist, album)
            #print track_stuff
            self.tc_album_search_album.SetValue(track_stuff[1])
            self.tc_album_search_artist.SetValue(artist)
            self.tc_album_search_song.SetValue('')
            if len(track_stuff) > 0:
                track_list = self.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.FillAlbumList(track_list, artist, track_stuff[1])
                # display album page
                self.nb_main.SetSelection(NB_ALBUM)
        elif (len(song) == 0) & (len(album) == 0) & (len(tag) == 0):
            # get the top songs for the selected artist            
            if len(artist) > 0:
                top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_song_list(artist)
                self.GenerateScrobbList(top_tracks_list)
        elif (len(tag) != 0):
            #doble-clik on a tag, get list of top songs for tag            
            top_tracks_list = audioscrobbler_lite.Scrobb().make_genre_top_song_list(tag)
            self.GenerateScrobbList(top_tracks_list)
    
    def OnLastTSSimilarClick(self, event):
        # grab similar tracks from last fm
        artist, song, album = self.GetLastThree()        
        
        if len(song) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_similar_song_list(artist, song)
            self.GenerateScrobbList(top_tracks_list)
        else:    
            dlg = wx.MessageDialog(self, 'Song not entered / playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastArtistSimilarClick(self, event):
        # grab similar tracks from last fm
        # get artist from artist search box, if blank get from current playing song
        artist, song, album = self.GetLastThree()        
        if len(artist) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_similar_artist_list(artist)
            #print top_tracks_list
            self.GenerateScrobbList(top_tracks_list, False, True)
        else:    
            dlg = wx.MessageDialog(self, 'Artist not entered / song not playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastTSAlbumClick(self, event):
        # get top tracks for a given album
        artist, song, album = self.GetLastThree()
        if (album == '') & (len(song) > 0):
            # check for album of playing song
            track_stuff = self.GetSongAlbumInfo(artist, song)
            album = track_stuff[1]        
        # get album id
        # get top tracks
        if len(album) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_album_top_song_list(artist, album)
            #print top_tracks_list
            # trhread the queries to get the plays for each song in teh album
            # THREAD
            current = WebFetchThread(self, '', '', top_tracks_list, 'PLAYCOUNT')
            #THREAD
            current.start()            
            self.GenerateScrobbList(top_tracks_list, False, False)
        else:
            dlg = wx.MessageDialog(self, 'Artist not entered / album not entered.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastTSArtistClick(self, event):
        # grab top tracks from last fm
        artist, song, album = self.GetLastThree()
        if len(artist) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_song_list(artist)
            self.GenerateScrobbList(top_tracks_list)
        else:    
            dlg = wx.MessageDialog(self, 'Artist not entered / song not playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastTAArtistClick(self, event):
        # grab top albums from last fm
        artist, song, album = self.GetLastThree()
        if len(artist) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_artist_top_album_list(artist)
            self.GenerateScrobbList(top_tracks_list, True)
        else:    
            dlg = wx.MessageDialog(self, 'Artist not entered / song not playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        
    def OnLastTSGeoClick(self, event):
        # grab top tracks from last fm per country
        country = self.ch_last_country.GetStringSelection()
        if len(country) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_geo_top_song_list(country)
            self.GenerateScrobbList(top_tracks_list)
        #print country
        
    def OnLastTSGenreClick(self, event):
        # grab top tracks from last fm per country
        genre = self.co_last_tag.GetValue() #(0)#Selection()
        if len(genre) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_genre_top_song_list(genre)
            self.GenerateScrobbList(top_tracks_list)
        #print genre
        
    def OnLastTTSongClick(self, event):
        # grab top tags per song
        artist, song, album = self.GetLastThree()

        if len(song) > 0:
            top_tracks_list = audioscrobbler_lite.Scrobb().make_song_top_tags_list(artist, song)
            self.GenerateScrobbList(top_tracks_list, False, False, True)
        else:    
            dlg = wx.MessageDialog(self, 'Song not entered / playing.', 'Problems...', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()

    def GenerateScrobbList(self, top_list, albums=False, artists=False, tags=False):
        # put some data in a list control
        counter = 0
        self.lc_lastfm.DeleteAllItems()
        for x in top_list:            
            if albums == True:
                # just printing artist/album
                self.lc_lastfm.InsertStringItem(counter, x[1])
                self.lc_lastfm.SetStringItem(counter, 1, '')
                self.lc_lastfm.SetStringItem(counter, 2, x[0])
                self.lc_lastfm.SetStringItem(counter, 3, x[2])
                self.lc_lastfm.SetStringItem(counter, 4, '')
            elif artists == True:
                # just printing artist
                self.lc_lastfm.InsertStringItem(counter, x[0])
                self.lc_lastfm.SetStringItem(counter, 1, '')
                self.lc_lastfm.SetStringItem(counter, 2, '')
                self.lc_lastfm.SetStringItem(counter, 3, x[1])
                self.lc_lastfm.SetStringItem(counter, 4, '')
            elif tags == True:
                # just printing artist
                self.lc_lastfm.InsertStringItem(counter, '')
                self.lc_lastfm.SetStringItem(counter, 1, '')
                self.lc_lastfm.SetStringItem(counter, 2, '')
                self.lc_lastfm.SetStringItem(counter, 3, x[1])
                self.lc_lastfm.SetStringItem(counter, 4, x[0])
            else:
                # just printing artist/song
                self.lc_lastfm.InsertStringItem(counter, x[1])
                self.lc_lastfm.SetStringItem(counter, 1, x[0])
                self.lc_lastfm.SetStringItem(counter, 2, '')
                self.lc_lastfm.SetStringItem(counter, 3, x[2])
                self.lc_lastfm.SetStringItem(counter, 4, '')

            #self.lc_lastfm.SetItemData(counter, x[1] + ':' + x[0])
            counter = counter + 1
               
        self.lc_lastfm.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lc_lastfm.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.lc_lastfm.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.lc_lastfm.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        self.lc_lastfm.SetColumnWidth(4, wx.LIST_AUTOSIZE)
        #self.nb_main.SetPageText(2, 'last.fm (' + str(counter) + ')')  
        
    def OnAutoGenerateLastfmPlayist(self, event):
        # lets just add all the items to your playlist
        # search for song from groove shark on demand, ie, when you go to play it?
        self.CheckClear()
        insert_at = self.lc_playlist.GetItemCount()
        
        for x in range(self.lc_lastfm.GetItemCount(), 0, -1):
            artist = self.lc_lastfm.GetItem(x-1, 0).GetText()
            song = self.lc_lastfm.GetItem(x-1, 1).GetText()
            # skip if there's no song title
            if song != '':
                self.SetPlaylistItem(insert_at, artist, song)
        #save the playlist
        self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        self.nb_main.SetSelection(NB_PLAYLIST)
        
    def OnLastfmRightClick(self, event):
        val = self.lc_lastfm.GetFirstSelected()
        if val != -1:
            if (self.lc_lastfm.GetItem(val, 0).GetText() != '') & (self.lc_lastfm.GetItem(val, 1).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 1
                ID_CLEAR = 2
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")
                menu.AppendSeparator()
                menu.Append(ID_CLEAR, "Clear Playlist")
                wx.EVT_MENU(self, ID_PLAYLIST, self.LastfmAddPlaylist)
                wx.EVT_MENU(self, ID_CLEAR, self.OnClearPlaylistClick)       
                self.PopupMenu(menu)
                menu.Destroy()
  
    def LastfmAddPlaylist(self, event):
        self.BackupList()
        val = self.lc_lastfm.GetFirstSelected()
        total = self.lc_lastfm.GetSelectedItemCount()
        current_count = self.lc_playlist.GetItemCount()
        #print val
        if (val >= 0):            
            artist =    self.lc_lastfm.GetItem(val, 0).GetText()
            song =      self.lc_lastfm.GetItem(val, 1).GetText()
            self.SetPlaylistItem(current_count, artist, song, '', '')
            current_select = val
            if total > 1:
                for x in range(1, self.lc_lastfm.GetSelectedItemCount()):
                    current_select =    self.lc_lastfm.GetNextSelected(current_select)
                    artist =            self.lc_lastfm.GetItem(current_select, 0).GetText()
                    song =              self.lc_lastfm.GetItem(current_select, 1).GetText()                    
                    self.SetPlaylistItem(current_count + x, artist, song, '', '')

        #save the playlist
        self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        #self.nb_main.SetSelection(NB_PLAYLIST)
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
            track_stuff = self.GetAlbumAlbumInfo(artist, album)
            self.tc_album_search_album.SetValue(track_stuff[1])
            self.tc_album_search_artist.SetValue(artist)
            if len(track_stuff) > 0:
                track_list = self.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.FillAlbumList(track_list, artist, track_stuff[1])
        elif (len(artist) != 0) & (len(song) != 0) & (len(album) == 0):            
            track_stuff = self.GetSongAlbumInfo(artist, song)
            self.tc_album_search_album.SetValue(track_stuff[1])
            self.tc_album_search_artist.SetValue(artist)
            if len(track_stuff) > 0:
                track_list = self.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.FillAlbumList(track_list, artist, track_stuff[1])
        elif (len(artist) != 0) & (len(song) == 0) & (len(album) == 0):
            # change to last.fm and display albums for artist
            self.tc_last_search_artist.SetValue(artist)
            self.OnLastTAArtistClick(None)
            self.nb_main.SetSelection(NB_LAST)
        else:            
            dlg = wx.MessageDialog(self, 'Artist or Artist/Song or Artist/Album not entered.', 'Problems...', wx.OK | wx.ICON_WARNING)
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
        self.tc_search.SetValue(artist + ' ' + song)        
        
    def OnAlbumDoubleClick(self, event):
        # past the artist + track in the search field
        val = self.lc_album.GetFirstSelected()
        artist = self.lc_album.GetItem(val, 0).GetText()
        song = self.lc_album.GetItem(val, 1).GetText()
        #search for selected song
        #self.SearchIt(artist + ' ' + song)
        self.SearchOrPlaylist(artist, song)
        # display search page
        #self.nb_main.SetSelection(NB_PLAYLIST)
        #self.lc_search.SetFocus()
        #self.lc_search.Select(0)
        
    def OnAlbumGetTracks(self, event):
        # get album info from musicbrainz        
        #self.nb_main.SetSelection(NB_ALBUM)
        track_list = []
        # just get the current track playing, use artist/song to get album info
        
        artist = self.partist
        song = self.ptrack
        self.tc_album_search_artist.SetValue(artist)
        self.tc_album_search_song.SetValue(song)
        
        if len(artist) > 0:
            #print 'boo'
            track_stuff = self.GetSongAlbumInfo(artist, song)
            #print track_stuff
            self.tc_album_search_album.SetValue(track_stuff[1])
            if len(track_stuff) > 0:
                track_list = self.GetAlbumInfo(track_stuff[0])
                #print track_list
                self.FillAlbumList(track_list, artist, track_stuff[1])        
                
    def FillAlbumList(self, track_list, artist, album):
        # fill list        
        self.lc_album.DeleteAllItems()
        counter = 0;
        for x in track_list:
            self.lc_album.InsertStringItem(counter, artist)
            self.lc_album.SetStringItem(counter, 1, x)
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
        self.CheckClear()
        insert_at = self.lc_playlist.GetItemCount()
        for x in range(self.lc_album.GetItemCount(), 0, -1):
            artist = self.lc_album.GetItem(x-1, 0).GetText()
            song = self.lc_album.GetItem(x-1, 1).GetText()
            album = self.lc_album.GetItem(x-1, 2).GetText()
            self.SetPlaylistItem(insert_at, artist, song, album)
        #save the playlist
        self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        self.nb_main.SetSelection(NB_PLAYLIST) 
        
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
                wx.EVT_MENU(self, ID_PLAYLIST, self.AlbumAddPlaylist)
                wx.EVT_MENU(self, ID_CLEAR, self.OnClearPlaylistClick)       
                self.PopupMenu(menu)
                menu.Destroy()
  
    def AlbumAddPlaylist(self, event):
        self.BackupList()
        val = self.lc_album.GetFirstSelected()
        total = self.lc_album.GetSelectedItemCount()
        current_count = self.lc_playlist.GetItemCount()
        #print val
        if (val >= 0):            
            artist =    self.lc_album.GetItem(val, 0).GetText()
            song =      self.lc_album.GetItem(val, 1).GetText()
            album =      self.lc_album.GetItem(val, 2).GetText()
            self.SetPlaylistItem(current_count, artist, song, album, '')
            current_select = val
            if total > 1:
                for x in range(1, self.lc_album.GetSelectedItemCount()):
                    current_select =    self.lc_album.GetNextSelected(current_select)
                    artist =            self.lc_album.GetItem(current_select, 0).GetText()
                    song =              self.lc_album.GetItem(current_select, 1).GetText()
                    album =             self.lc_album.GetItem(current_select, 2).GetText()
                    self.SetPlaylistItem(current_count + x, artist, song, album, '')

        #save the playlist
        self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        #self.nb_main.SetSelection(NB_PLAYLIST)
                
        
# ---------------------------------------------------------
# biography  ----------------------------------------------
    def GetArtistBio(self, artist):
        # get song's album from musicbrainz
        # THREAD
        current = WebFetchThread(self, artist, 'song', 'album', 'BIO')
        #THREAD
        current.start()
        
    def SetBioImage(self, file_name):
        # get albumcover for artist/song from last.fm
        bio_bmp = wx.Bitmap(self.image_save_location + file_name, wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        #self.bm_bio_pic.SetSize(bio_bmp.GetSize())
        #self.bm_bio_pic.SetBitmap(bio_bmp)
        bb = bio_bmp.GetSize()        
        hr = float(bb[0]) / 250
        hs = float(bb[1]) / hr
        # rescale it so it's x= 250 y =? to keep aspect
        hoo = wx.Bitmap.ConvertToImage(bio_bmp)
        hoo.Rescale(250, hs) #, wx.IMAGE_QUALITY_HIGH)
        ioo = wx.BitmapFromImage(hoo)
        self.bm_bio_pic.SetBitmap(ioo)

    def SetBioText(self, bio_text, artist):
        # get albumcover for artist/song from last.fm
        bio_text_str = self.StripTags(bio_text)
        page_contents = '<p><FONT SIZE=3><b>' + unicode(artist) + '</b></FONT><br><br><FONT SIZE=-1>' + unicode(bio_text_str) + '</FONT></p>'
        self.hm_bio_text.SetPage(page_contents)
        
    def StripTags(self, text):
        finished = 0
        if (text != None):
            if (len(text) > 0):
                while not finished:
                    finished = 1
                    # check if there is an open tag left
                    start = text.find("<")
                    if start >= 0:
                        # if there is, check if the tag gets closed
                        stop = text[start:].find(">")
                        if stop >= 0:
                            # if it does, strip it, and continue loop
                            text = text[:start] + text[start+stop+1:]
                            finished = 0
        return text

        
# --------------------------------------------------------- 
# musicbrainz----------------------------------------------  
            
    def GetSongAlbumInfo(self, artist, track):
        # get song's album from musicbrainz
        track_stuff = musicbrainz.Brainz().get_song_info(artist, track)
        # musicbrainz album id
        #album_mid = track_stuff[0]
        #album_title = track_stuff[1]
        return track_stuff
        
    def GetAlbumAlbumInfo(self, artist, album):
        # get song's album from musicbrainz
        track_stuff = musicbrainz.Brainz().get_album_info(artist, album)
        # musicbrainz album id
        #album_mid = track_stuff[0]
        #album_title = track_stuff[1]
        return track_stuff
        
    def GetAlbumInfo(self, mid):
        # get album info from musicbrainz
        track_list = musicbrainz.Brainz().get_track_list(mid)
        return track_list
        
       
# --------------------------------------------------------- 
# covers --------------------------------------------------  
    def GetSongArt(self, artist, album):
        # get albumcover for artist/song from last.fm
        
        # THREAD
        current = WebFetchThread(self, artist, 'song', album, 'COVERS')
        #THREAD
        current.start()
        
            
    def SaveSongArt(self, art_url, file_name):
        # get albumcover for artist/song from last.fm
        # check that file doesn't exist
        if os.path.exists(self.image_save_location + file_name) == False:
            urllib.urlretrieve(art_url, self.image_save_location + file_name)            
            urllib.urlcleanup()
            #print 'getting new'
        
    def SetImage(self, file_name, dir_name):
        # get albumcover for artist/song from last.fm
        cover_bmp = wx.Bitmap(dir_name + file_name, wx.BITMAP_TYPE_ANY)
        
        foo = wx.Bitmap.ConvertToImage(cover_bmp)
        sma_bm = self.bm_cover.GetSize()
        foo.Rescale(sma_bm[0], sma_bm[1])
        goo = wx.BitmapFromImage(foo)
        self.bm_cover.SetBitmap(goo)
        
        # now the large one
        hoo = wx.Bitmap.ConvertToImage(cover_bmp)
        lar_bm = self.bm_cover_large.GetSize()
        hoo.Rescale(lar_bm[0], lar_bm[1])
        ioo = wx.BitmapFromImage(hoo)
        self.bm_cover_large.SetBitmap(ioo)
        #self.bm_cover.Refresh()
        
        self.album_viewer.SetImage(file_name, dir_name)
        
# --------------------------------------------------------- 
# song collection -----------------------------------------  
    def OnSColAddClick(self, event):
        # show song db window
        #song_db_window = local_songs.SongDBWindow(self)
        song_db_window = song_collection.SongDBWindow(self)
        song_db_window.show_me()
        
    def OnSColDeleteClick(self, event):
        # show song db window        
        # remove slected list item
        val = self.lc_scol_col.GetFirstSelected()
        # iterate over all selected items and delete
        for x in range(val, val + self.lc_scol_col.GetSelectedItemCount()):
            #print 'dete - ' + str(val)
            #self.lc_playlist.DeleteItem(val)
            #get the id and remove from db
            row_id = self.lc_scol_col.GetItem(x, 0).GetText()
            local_songs.DbFuncs().RemoveRow(row_id)
            #self.lc_scol_col.DeleteItem(self.lc_scol_col.GetFirstSelected())
        self.RefreshSCol()
        
    def RefreshSCol(self, event=None):
        # refresh the song collection list control        
        self.lc_scol_col.DeleteAllItems()
        self.lc_scol_col.SetItemCount(local_songs.DbFuncs().GetCountAndLast()[0])
        
    def OnScolRightClick(self, event):        
        # make a menu
        ID_PLAYLIST = 1
        ID_CLEAR = 2
        #ID_FAVES = 3
        
        menu = wx.Menu()
        menu.Append(ID_PLAYLIST, "Add to Playlist")
        menu.AppendSeparator()
        menu.Append(ID_CLEAR, "Clear Playlist")
        #menu.Append(ID_SHARE, "Clipboard Share Link")
        #menu.AppendSeparator()
       # menu.Append(ID_SEARCH, "Find Better Version")        
        
        wx.EVT_MENU(self, ID_PLAYLIST, self.ScolAddPlaylist)
        wx.EVT_MENU(self, ID_CLEAR, self.OnClearPlaylistClick)
        #wx.EVT_MENU(self, ID_FAVES, self.OnFavesClick)        
        
        self.PopupMenu(menu)
        menu.Destroy()
        
    def ScolAddPlaylist(self, event):
        self.BackupList()
        # cycle through selected
        val = self.lc_scol_col.GetFirstSelected()
        # iterate over all selected items and delete
        #self.CheckClear()
        #check for file or folder
        if val != -1:
            if self.lc_scol_col.GetItem(val, 0).GetText() == ' ':
                #it's just a folder, first item is ' '  not ''
                #pen folder, cycle through mp3 file adding to playlist
                folder = self.lc_scol_col.GetItem(val, 2).GetText()
                folder_arr = local_songs.DbFuncs().GetResultsArray(folder, 100, True, 2)
                for x in range(0, len(folder_arr)):
                    self.ScolFileAdd(folder_arr[x][4])
            else:
                # it's a file
                for x in range(val, val + self.lc_scol_col.GetSelectedItemCount()):
                    mfile = self.lc_scol_col.GetItem(x, 1).GetText()
                    mfolder = self.lc_scol_col.GetItem(x, 2).GetText()
                    mpath = self.lc_scol_col.GetItem(x, 3).GetText()
                    if mfolder == ' ':
                        self.ScolFileAdd(mpath + '/' + mfile)
                    else:
                        self.ScolFileAdd(mpath + '/' + mfolder + '/' + mfile)

            
    def ScolFileAdd(self, file_name):
        # copy the faves list to the playlist        
        insert_at = self.lc_playlist.GetItemCount()
        
        artist = local_songs.GetMp3Artist(file_name)
        song = local_songs.GetMp3Title(file_name)
        album = local_songs.GetMp3Album(file_name)
        song_id = file_name.replace(os.sep, '/')
        duration = self.ConvertTimeFormated(local_songs.GetMp3Length(file_name))
        self.SetPlaylistItem(insert_at, artist, song, album, song_id, duration)
        #save the playlist
        self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        #self.nb_main.SetSelection(NB_PLAYLIST)
        
    def OnSColClearClick(self, event):
        # clear album search field
        self.tc_scol_song.Clear()
        #self.tc_scol_folder.Clear()
      
    def OnSColSongText(self, event):
        # search local db for matches
        if self.rb_scol_file.GetValue() == True:
            qtype = 'file'
            self.SCAdjustColumns('files')
        else:
            qtype = 'folder'
            self.SCAdjustColumns('folders')
        query = self.tc_scol_song.GetValue()
        self.lc_scol_col.SetQuery(query, qtype)
        
    def OnSColRadio(self, event):
        self.OnSColSongText(None)
        
    def SCAdjustColumns(self, col_type):
        if col_type == 'files':        
            self.lc_scol_col.SetColumnWidth(0, 50)
            self.lc_scol_col.SetColumnWidth(1, 175)
            self.lc_scol_col.SetColumnWidth(2, 150)
            self.lc_scol_col.SetColumnWidth(3, 190)            
        else:
            self.lc_scol_col.SetColumnWidth(0, 0)
            self.lc_scol_col.SetColumnWidth(1, 0)
            self.lc_scol_col.SetColumnWidth(2, 520)
            self.lc_scol_col.SetColumnWidth(3, 0)
# --------------------------------------------------------- 
        
#---------------------------------------------------------------------------
# ####################################
class WebFetchThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, panel, artist, song, album, webfetchtype):
        Thread.__init__(self)
        self.panel = panel
        self.artist = artist
        self.song = song
        self.album = album
        self.webfetchtype = webfetchtype
        self.lsp = local_songs.Player()
               
    def stop(self):
        self.lsp.stop_play()
        #self.lsp.stop()
        
    def pause(self):
        self.lsp.toggle_pause()
         
    def run(self):
        if self.webfetchtype == 'COVERS':
            #for covers
            song_art_url =''
            
            if len(self.album) == 0:
                album_array = musicbrainz.Brainz().get_song_info(self.artist, self.song)
                self.album = album_array[1]
            
            if len(self.album) > 0:
                # try album art if nothing is listed for the song
                song_art_url = audioscrobbler_lite.Scrobb().get_album_art(self.artist, self.album)
            if len(str(song_art_url)) > 8:
                file_name = song_art_url.rsplit('/', 1)[1]
                self.panel.SaveSongArt(song_art_url, file_name)
                self.panel.SetImage(file_name, self.panel.image_save_location)
                self.panel.palbum_art_file = file_name
            else:
                self.panel.SetImage('no_cover.png', GRAPHICS_LOCATION)
                self.panel.palbum_art_file =''
                #print 'no-cover'
                
        if self.webfetchtype == 'BIO':
            #for covers
            bio_url =''
            if len(self.artist) > 0:
                # try album art if nothing is listed for the song
                bio_url = audioscrobbler_lite.Scrobb().get_artist_bio(self.artist)
                #print bio_url[0]
            if len(str(bio_url[0])) > 8:
                file_name = bio_url[0].rsplit('/', 1)[1]
                self.panel.SaveSongArt(bio_url[0], file_name)
                self.panel.SetBioImage(file_name)            
            self.panel.SetBioText(bio_url[1], self.artist)
            
        if self.webfetchtype == 'PLAYLOCAL':
            #local mp3 playback 
            print 'local: ' + self.song
            self.panel.pstatus = 'loading'
            while os.path.isfile(self.song) != True:
                time.sleep(1)               
            while os.path.getsize(self.song) < BUFFER_SIZE:
                time.sleep(2)
                #print os.path.getsize(file_name)
            self.panel.time_count = -1
            self.panel.pstatus = 'playing'    
            self.lsp.play(self.song)
            
        if self.webfetchtype == 'VERSION':
            version_check.VersionCheck(self.panel, self.album).CheckVersion()
            
            exe_name_arr = sys.argv[0].rsplit(os.sep, 1)
            exe_name = ''
            if len(exe_name_arr) > 1:
                exe_name = exe_name_arr[1]
            if exe_name == 'gw_upd.exe':
                #wx.Log.EnableLogging(False)
                try:
                    shutil.copyfile(SYSLOC + os.sep + 'gw_upd.exe', SYSLOC + os.sep + 'gw.exe')
                except IOError:
                    dlg = wx.MessageDialog(frame, "Can't copy gw_upd.exe to gw.exe\r\nNeed administrator privileges(?).", 'Alert', wx.OK | wx.ICON_WARNING)
                    if (dlg.ShowModal() == wx.ID_OK):
                        dlg.Destroy()
                #wx.Log.EnableLogging(True)
         
        if self.webfetchtype == 'SEARCH':
            #for searching
            query_string = self.artist + ' ' + self.song
            query_results = tinysong.Tsong().get_search_results(query_string, 1)
            #print query_results
            if len(query_results) == 1:
                #add to playlist
                #self.panel.SetPlaylistItem(0, artist, song, album, url)                
                split_array = query_results[0].split('; ')
                play_url = split_array[1]
                # added a delay, seems to fuck up otherwise
                #time.sleep(1.5)
                self.panel.SetPlaylistItem(0, split_array[4], split_array[2], split_array[6], play_url)
                
        if self.webfetchtype == 'PLAYCOUNT':
            #for grabbing playcounts
            #self.album is a ararray of arrays [song, artist, '']
            counter = 0
            for x in self.album:
                playcount = audioscrobbler_lite.Scrobb().get_play_count(x[1], x[0])
                #print playcount
                self.panel.lc_lastfm.SetStringItem(counter, 3, playcount)
                if counter == 0:
                    self.panel.lc_lastfm.SetColumnWidth(3, wx.LIST_AUTOSIZE)
                counter = counter + 1
        
        if self.webfetchtype == 'SONGINFO':
            #grab song info
            print 'gobble'
            res = audioscrobbler_lite.Scrobb().get_song_info(self.artist, self.song)
            tag_id = ''
            #print res
            if len(res[2]) >=1:
                tag_id = local_songs.DbFuncs().InsertTagData(res[2])
            #print tag_id
            grooveshark_id = self.panel.pgroove_id
            music_id = self.panel.pmusic_id
            track_time = self.panel.current_play_time
            #tag_id = ''            
            album_art_file = self.panel.palbum_art_file
            track_id = local_songs.DbFuncs().InsertTrackData(grooveshark_id, music_id, track_time, tag_id, self.artist, self.song, self.album, album_art_file)#p_grooveshark_id, p_music_id, p_track_time, p_tag_id, p_artist, p_song, p_album, p_album_art_file)
            local_songs.DbFuncs().InsertPlaycountData(track_id)#p_track_id)
            if (res[1] != '') & (res[0] !=''):
                local_songs.DbFuncs().InsertPopData(track_id, res[1], res[0])#p_track_id, p_listeners, p_playcount)

            
#---------------------------------------------------------------------------
# ####################################
class FileThread(Thread): 
    # grab file
    def __init__(self, parent, temp_file, song_id, track, artist, album, prefetch=False):
        Thread.__init__(self)
        self.parent = parent
        self.temp_file = temp_file
        self.song_id = song_id
        self.track = track
        self.artist = artist
        self.album = album
        self.prefetch = prefetch
        
    def GetFileSize(self):
        # file size
        keyandserver = self.GetStreamKeyAndServer()
        file_size = grooveshark_old.Grooveshark(self).GetFileSize(keyandserver[0], keyandserver[1])
        return file_size        
        
    def GetStreamKeyAndServer(self):
        data_dir = system_files.GetDirectories(self).DataDirectory() + os.sep
        g_version = GetLocalGroovesharkVersion(data_dir)
        g_session = jsonrpcSession(None, g_version)
        g_session.startSession()
        g_data = {'SongID': self.song_id, 'Name': self.track, 'ArtistName': self.artist, 'AlbumName': self.album, 'AlbumID': '', 'ArtistID': ''}
        g_song = song.songFromData(g_session, g_data)
        g_song.getStreamDetails()
        return (g_song._lastStreamKey, g_song._lastStreamServer)
                        
    def run(self):
        
        ##self.parent.pstatus ='buffering'
        #progress thread
        #THREAD
        current = ProgressThread(self.parent, self.temp_file, self.GetFileSize())
        #THREAD
        current.start()
        
        keyandserver = self.GetStreamKeyAndServer()                
        grooveshark_old.Grooveshark(self.parent).download(keyandserver[0], keyandserver[1], self.temp_file)
        
        if self.prefetch == False:
            track_time = local_songs.GetMp3Length(self.temp_file)
            self.parent.current_play_time = track_time
            
        # check if recording or the save all new checkbox is checked
        if (self.parent.record_toggle == True) or (self.parent.cb_options_autosave.GetValue() == True):
            #copy and rname the file to teh record dir
            record_dir = self.parent.bu_options_record_dir.GetLabel()
            if (record_dir == None) | (record_dir == ''):
                record_dir = system_files.GetDirectories(self.parent).Mp3DataDirectory()
                self.parent.bu_options_record_dir.SetLabel(record_dir)            
            complete_filename = system_files.GetDirectories(self.parent).CopyFile(self.temp_file, record_dir, self.artist + '-' + self.track + '.mp3')
            # add file to database
            if complete_filename != None:
                #print complete_filename
                song_collection.AddSingleFile(complete_filename)
                self.parent.lc_scol_col.SetItemCount(song_collection.GetCount())
                # clear id for this song on the playlist
                # ASSUME that it's the current selection
                val = self.parent.lc_playlist.GetFirstSelected()
                self.parent.lc_playlist.SetStringItem(val, 3, '')
          
                
def GetLocalGroovesharkVersion(data_dir):
    #gets the grooveshark version from the local grooveshark.xml file
    #check if file exists
    file_name = 'grooveshark.xml'
    g_version = None
    if os.path.isfile(file_name):
        #get the version number from the file
        xml_dict = read_write_xml.xml_utils().get_generic_settings(data_dir + file_name)
        if xml_dict.has_key('version'):
            if len(xml_dict['version']) > 0:
                g_version = xml_dict['version']
    return g_version     
            
# ####################################
class ProgressThread(Thread): 
    # another thread to update download progress
    def __init__(self, parent, temp_file, file_size):
        Thread.__init__(self)
        self.temp_file = temp_file
        self.file_size = file_size
        self.parent = parent        
                        
    def run(self):        
        while os.path.isfile(self.temp_file) != True:
            time.sleep(1)
        while self.file_size > os.path.getsize(self.temp_file):
            per_val = int(((os.path.getsize(self.temp_file) / float(self.file_size)) * 100))            
            #self.parent.ga_download.SetValue(per_val)
            self.parent.download_percent = per_val
            if per_val == 100:
                break
            time.sleep(1)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

        
if __name__ == '__main__':

    ###app = MyApp(0)
    ###app.MainLoop()

    app = wx.PySimpleApp()
    #app = wx.App()
    frame = MainFrame()
    #popup = TestPopup(frame, wx.SIMPLE_BORDER)    
    panel = MainPanel(frame)    
    #panel.MakeModal(True)
    #panel.Show(True)
    #frame.SetTransparent(180)
    frame.Show(True)
    app.MainLoop()   

