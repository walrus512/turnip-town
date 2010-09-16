# -*- coding: utf-8 -*-
"""
GrooveWalrus: GrooveWalrus
Copyright (C) 2009, 2010
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
from wx.lib.pubsub import Publisher as pub

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
import subprocess

from main_utils import musicbrainz
from main_utils import tinysong
#from main_utils import jiwa
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
from main_utils import pyro_server

#---
from main_utils import player_wx
from main_utils import player_pyglet
from main_utils import player_pymedia

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
from main_windows import advanced_options

from main_tabs import list_sifter_tab
from main_tabs import favorites_tab
from main_tabs import song_collection_tab
from main_tabs import biography_tab
from main_tabs import album_tab
from main_tabs import my_lastfm_tab
from main_tabs import lastfm_tab

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
#from plugins.minimode import minimode
#from plugins.lyrics import lyrics
#from plugins.sync import sync
#from plugins.zongdora import zongdora
#from plugins.web_remote import web_remote

PROGRAM_VERSION = "0.322"
PROGRAM_NAME = "GrooveWalrus"

#PLAY_SONG_URL ="http://listen.grooveshark.com/songWidget.swf?hostname=cowbell.grooveshark.com&style=metal&p=1&songID="
#PLAY_SONG_ALTERNATE_URL ="http://listen.grooveshark.com/main.swf?hostname=cowbell.grooveshark.com&p=1&songID="
SONG_SENDER_URL = "http://gwp.turnip-town.net/?"

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())
# set the working dir too
os.chdir(SYSLOC)
    
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

#columns
C_RATING = 0
C_ARTIST = 1
C_SONG = 2
C_ALBUM = 3
C_ID = 4
C_TIME = 5

PLAYLIST_COLUMNS = {'artist': C_ARTIST, 'rating': C_RATING, 'song': C_SONG, 'album': C_ALBUM, 'id': C_ID, 'time': C_TIME}

HICOLOR_1 = (110, 207, 106, 255)
HICOLOR_2 = (200, 100, 150, 255)

API_KEY = "13eceb51a4c2e0f825c492f04bf693c8"
SECRET = ""
LASTFM_CLIENT_ID = 'gws'

CHARSET = 'utf-8'
FRAME_WIDTH = 695

class GWApp(wx.App):
    def OnInit(self):
        self.name = "%s-%s" % (PROGRAM_NAME, wx.GetUserId())
        self.instance = wx.SingleInstanceChecker(self.name)
        if self.instance.IsAnotherRunning():
            #wx.MessageBox("Another instance is running", "ERROR")
            # send command line args to existing app
            try:
                pyro_server.SendPyro(sys.argv)
            except Exception, expt:
                print "GWApp: " + str(Exception)+str(expt)
            #wx.Log.EnableLogging(False)
            sys.exit()
            #return False
        else:
            frame = MainFrame()
            panel = MainPanel(frame)    
            frame.Show(True)
            pyro_server.StartPyro()        
            return True

class MainFrame(wx.Frame): 
    def __init__(self): 
        wx.Frame.__init__(self, None, -1, PROGRAM_NAME + ' ' + PROGRAM_VERSION, size=(FRAME_WIDTH, 530), pos=(200,200), style=wx.DEFAULT_FRAME_STYLE|wx.WANTS_CHARS) #^(wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)) #, style=wx.STAY_ON_TOP) 
        
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
        self.tray_icon = wx.TaskBarIcon()
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
            self.BringUpTop()
            
    def BringUpTop(self):
        """ hacky way of bring the frame to the foreground """
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
        self.FILEDB = system_files.GetDirectories(self).DatabaseLocation()
        ignore_locale = options_window.GetSetting('locale-ignore', self.FILEDB)
        if (ignore_locale == False) | (ignore_locale != "1"):
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
        self.working_directory = SYSLOC
        self.FILEDB = system_files.GetDirectories(self).DatabaseLocation()
        
        # create/update database ----------
        local_songs.DbFuncs().create_tables() 
        
        # xrc gui layout ------------------
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)
        # custom widget handler
        #get_resources().AddHandler(TreeListCtrlXmlHandler())
        #res.InsertHandler(TreeListCtrlXmlHandler())
        ##res.InsertHandler(custom_slider.MyCustomSliderXmlHandler(self))
        # Now create a panel from the resource data
        self.panel = res.LoadPanel(self, "m_pa_main")        
        
        xrc.XRCCTRL(self, 'm_pa_options_plugins').SetVirtualSize((1000, 1000))
        xrc.XRCCTRL(self, 'm_pa_options_plugins').SetScrollRate(20,20)
        
        # tabs -----------------------------
        #list sifter tab        
        self.list_sifter = list_sifter_tab.ListSifterTab(self)        
        #favorites tab        
        self.favorites = favorites_tab.FavoritesTab(self)        
        #song collection tab        
        self.tab_song_collection = song_collection_tab.SongCollectionTab(self)        
        #biography tab        
        self.tab_biography = biography_tab.BiographyTab(self)
        #biography tab        
        self.tab_album = album_tab.AlbumTab(self)
        #my_lastfm tab        
        self.tab_my_lastfm = my_lastfm_tab.MyLastfmTab(self)
        #lastfm tab        
        self.tab_lastfm = lastfm_tab.LastfmTab(self)
               
        # control references ---------------
        # playback        
        self.bb_random = xrc.XRCCTRL(self, 'm_bb_random')
        self.bb_repeat = xrc.XRCCTRL(self, 'm_bb_repeat')
        self.bb_record = xrc.XRCCTRL(self, 'm_bb_record')
        self.tc_search = xrc.XRCCTRL(self, 'm_tc_search')        
        self.sl_volume = xrc.XRCCTRL(self, 'm_sl_volume')
        self.pa_playback = xrc.XRCCTRL(self, 'm_pa_playback')
        self.bu_status_lf = xrc.XRCCTRL(self, 'm_bu_status_lf')
        self.bu_status_gs = xrc.XRCCTRL(self, 'm_bu_status_gs')
        
        self.bb_playlist_options = xrc.XRCCTRL(self, 'm_bb_playlist_options')
        self.sp_playlist = xrc.XRCCTRL(self, 'm_sp_playlist')
        self.tr_playlist_history = xrc.XRCCTRL(self, 'm_tr_playlist_history')
        self.tr_playlist_history_root = self.tr_playlist_history.AddRoot("rootie")
        
        ##self.sl_volume = res.LoadObject(self, "m_cc_volume_slider", "CustomSlider")
        ##self.sl_volume2 = xrc.XRCCTRL(self, 'm_cc_volume_slider')
        ##self.sl_volume = self.cslid        
        ##self.sl_volume3 = self.FindWindowById( xrc.XRCID('m_cc_volume_slider' ))         
        
        self.bb_update = xrc.XRCCTRL(self, 'm_bb_update')
             
        self.nb_main = xrc.XRCCTRL(self, 'm_nb_main')
        self.pa_options_plugins = xrc.XRCCTRL(self, "m_pa_options_plugins")
        
        self.bm_cover = xrc.XRCCTRL(self, 'm_bm_cover_small')
        self.bm_cover.Bind(wx.EVT_LEFT_UP, self.OnAlbumCoverClick)       
        
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
        self.rx_options_backend =  xrc.XRCCTRL(self, 'm_rx_options_backend')
        self.ch_options_wxbackend =  xrc.XRCCTRL(self, 'm_ch_options_wxbackend')
        self.st_options_cache_location = xrc.XRCCTRL(self, 'm_st_options_cache_location')
        self.sl_options_cache_size = xrc.XRCCTRL(self, 'm_sl_options_cache_size')
        
        self.st_options_i18n_default = xrc.XRCCTRL(self, 'm_st_options_i18n_default')
        self.st_options_i18n_default.SetLabel('Locale: ' + wx.Locale(wx.LANGUAGE_DEFAULT).GetCanonicalName())
              
        # list controls ------------
                
        # playlist
        # playlist is subclassed to draglist in the xrc
        self.lc_playlist = xrc.XRCCTRL(self,'m_lc_playlist')
        self.lc_playlist.InsertColumn(C_RATING," ")
        self.lc_playlist.InsertColumn(C_ARTIST,"Artist")
        self.lc_playlist.InsertColumn(C_SONG,"Song")
        self.lc_playlist.InsertColumn(C_ALBUM,"Album")
        self.lc_playlist.InsertColumn(C_ID,"Id")
        self.lc_playlist.InsertColumn(C_TIME,"Time")
        
        self.lc_playlist.AssignImageList(self.RateImageList(), wx.IMAGE_LIST_SMALL)        
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPlayListPlayClick, self.lc_playlist)
        # wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnPlaylistRightClick, self.lc_playlist)
        # wxGTK
        self.lc_playlist.Bind(wx.EVT_RIGHT_UP, self.OnPlaylistRightClick)
        ##self.lc_playlist.Bind(wx.EVT_CHAR, self.OnPlaylistKeyPress)
        self.lc_playlist.Bind(wx.EVT_KEY_UP, self.OnKeyPress)
        self.lc_playlist.Bind(wx.EVT_CHAR, self.OnChar)
        
        #playlist history
        self.lc_playlist_history = xrc.XRCCTRL(self, 'm_lc_playlist_history')
        self.lc_playlist_history.InsertColumn(0,"Rating")
        self.lc_playlist_history.InsertColumn(1,"Artist")
        self.lc_playlist_history.InsertColumn(2,"Song")
        self.lc_playlist_history.SetColumnWidth(C_RATING, 0)
        
        self.tr_playlist_history.Bind(wx.EVT_RIGHT_DOWN, self.OnPlaylistTreeRightClick)
        self.tr_playlist_history.Bind(wx.EVT_RIGHT_UP, self.OnPlaylistTreeRightClick)
        self.tr_playlist_history.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnPlaylistTreeActivate)
        
        ##dynamic listctrl resize
        wx.EVT_SIZE(self.parent, self.DynamicResizePlaylist)
        wx.EVT_MAXIMIZE(self.parent, self.DynamicResizePlaylist)
        
        # background image --------------------
        use_background = options_window.GetSetting('background-use-graphic', self.FILEDB)
        self.background_file = options_window.GetSetting('background-graphic', self.FILEDB)
        if self.background_file != False:
            if (use_background == '1') & (os.path.isfile(self.background_file)):            
                self.panel.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
                self.panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        #self.sl_volume.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        
        #self.panel.Bind(wx.EVT_SIZE, self.OnResize)
                        

        # and do the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL, 0)        
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
        self.Bind(wx.EVT_BUTTON, self.SavePlaylistToDatabase, id=xrc.XRCID('m_bb_save_playlist'))
        self.Bind(wx.EVT_BUTTON, self.FixPlaylistItem, id=xrc.XRCID('m_bb_fix_song'))
        self.Bind(wx.EVT_BUTTON, self.OnClearPlaylistClick, id=xrc.XRCID('m_bb_clear_playlist'))
        self.Bind(wx.EVT_BUTTON, self.RemovePlaylistItem, id=xrc.XRCID('m_bb_remove_playlist_item'))
        self.Bind(wx.EVT_BUTTON, self.OnLoadPlaylistClick, id=xrc.XRCID('m_bb_load_playlist'))
        self.Bind(wx.EVT_BUTTON, self.OnPlaylistHistoryClick, id=xrc.XRCID('m_bb_playlist_options'))
        
        #playlist history     
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChange, self.tr_playlist_history)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnTreeBeginEdit, self.tr_playlist_history)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnTreeEndEdit, self.tr_playlist_history) 
                        
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
        self.Bind(wx.EVT_BUTTON, self.SaveOptions, id=xrc.XRCID('m_bu_options_set_cache'))
        self.Bind(wx.EVT_RADIOBOX, self.SetBackend, id=xrc.XRCID('m_rx_options_backend'))
        self.Bind(wx.EVT_CHOICE, self.SetBackend, id=xrc.XRCID('m_ch_options_wxbackend'))
        
        self.Bind(wx.EVT_BUTTON, self.OnClearCacheClick, id=xrc.XRCID('m_bu_options_cache_clear'))
        
        self.Bind(wx.EVT_BUTTON, self.OnUpdateClick, self.bb_update)
        wx.EVT_CLOSE(self.parent, self.OnExit)
           
        # --------------------------------------------------------- 
        #vars
        
        self.flash = None
        # ***self.flash.LoadMovie(0, 'http://listen.grooveshark.com/songWidget.swf?hostname=cowbell.grooveshark.com&songID=13721223&style=metal&p=0')
        self.autoplay = False
        
        #check for playlist and sysargs
        self.CheckSysArgs(sys.argv)        

        # load playlist history
        self.FillPlaylistTree()
        
        #initalize song class
        self.current_song = CurrentSong(self)
        #self.current_song.song_time_seconds = 0
        #self.current_song.playlist_position = -1
        
        # thread for playing a local track
        self.current_local = None
        
        #self.current_song.artist = ''
        #self.current_song.song = ''
        #self.current_song.album = ''
        self.palbum_art_file =''
        #self.current_song.track_id = 0
        #self.current_song.groove_id = 0
        
        self.download_percent = 0
        #self.current_song.status = 'stopped'
        
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
        self.update_event = False

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
        self.current_song.scrobble_song = 0
        self.session_key2 = None
        #self.SetScrobb()
        self.db_submit_complete = False
        
        # album cover
        self.album_viewer = album_viewer.AlbumViewer(self, GRAPHICS_LOCATION)
        #cover_bmp = wx.Bitmap(self.image_save_location + 'no_cover.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.SetImage('no_cover.png', GRAPHICS_LOCATION)
                       
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
        ctrl8ID = 911
        ctrlfID = 804
        ctrlmID = 805        
        ctrlgID = 806
        ctrlperiodID = 807
        
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
                                   (wx.ACCEL_CTRL, ord('8'), ctrl8ID),
                                   (wx.ACCEL_CTRL, ord('F'), ctrlfID),
                                   (wx.ACCEL_CTRL, ord('G'), ctrlgID),
                                   (wx.ACCEL_CTRL, ord('M'), ctrlmID),
                                   (wx.ACCEL_CTRL, ord('.'), ctrlperiodID)
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
        wx.EVT_MENU(self, ctrl8ID, self.ClearIdValues)
        wx.EVT_MENU(self, ctrlmID, self.MiniMode)
        wx.EVT_MENU(self, ctrlgID, self.OnLoadBackgroundImage)
        wx.EVT_MENU(self, ctrlperiodID, self.OnLoadAdvancedOptions)
        
        
        # menu items -----------
        # file menu
        self.parent.Bind(wx.EVT_MENU, self.OnLoadPlaylistClick, id=xrc.XRCID("m_mi_open"))
        self.parent.Bind(wx.EVT_MENU, self.SavePlaylistToDatabase, id=xrc.XRCID("m_mi_save_playlist"))
        self.parent.Bind(wx.EVT_MENU, self.QuickSavePlaylist, id=xrc.XRCID("m_mi_quick_save"))
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
        self.parent.Bind(wx.EVT_MENU, self.tab_song_collection.OnSColAddClick, id=xrc.XRCID("m_mi_song_collection"))
        self.parent.Bind(wx.EVT_MENU, self.ImportGroovesharkPlaylist, id=xrc.XRCID("m_mi_import_grooveshark"))
        #
        self.lastfm_toggle = self.parent.menu_tools.Append(7666, "Last.fm Scrobbling", kind=wx.ITEM_CHECK)
        self.parent.Bind(wx.EVT_MENU, self.OnToggleScrobble, id=7666)        
        
        # help menu
        self.parent.Bind(wx.EVT_MENU, self.OnGSVersionClick, id=xrc.XRCID("m_mi_gs_version"))
        self.parent.Bind(wx.EVT_MENU, self.OnAboutClick, id=xrc.XRCID("m_mi_about"))
        self.parent.Bind(wx.EVT_MENU, self.OpenWebsite, id=xrc.XRCID("m_mi_website"))        
        
        #-------------
        #set ratings for playlist items
        self.GetAllSongRatings()
        
        #-------------
        #plugins
        a = plugin_loader.PluginLoader(self)
                
        # options ---------------
        # load options from settings.xml
        options_window.Options(self).LoadOptions()
        if self.cb_options_tray.GetValue() == 1:
            self.parent.UseTrayIcon()
            
        # ---------------------------------------------------------------
        ##setup wxmedia backend
        ##backend = eval('wx.media.MEDIABACKEND_' + self.ch_options_wxbackend.GetStringSelection())
        ##self.mediaPlayer = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER, szBackend=backend) #wx.media.MEDIABACKEND_WMP10)
        ##self.Bind(wx.media.EVT_MEDIA_LOADED, self.PlayWxMedia)        
        #set backend
        self.SetBackend(None)
        #backend_types = ['pymedia', 'wx.media', 'pyglet']
        #self.use_backend = backend_types[self.rx_options_backend.GetSelection()]
        # ---------------------------------------------------------------
        
        #pubsub receivers --------
        self.LocalReceivers()
        
        # volume control
        #check for txt, don't adjust volume if present
        if os.path.isfile('disable_set_volume.txt'):
            pass
        else:
            setting_volume = options_window.GetSetting('main-volume', self.FILEDB)
            if setting_volume != False:
                self.SetVolume(int(setting_volume))
            else:
                self.SetVolume(50)
        
        # clean cache dir -------
        temp_dir = system_files.GetDirectories(self).TempDirectory()
        file_cache.CheckCache(temp_dir, self.sl_options_cache_size.GetValue())
        
        self.st_options_cache_location.SetLabel('Location: ' + temp_dir)
        
        # load rss feeds --------
        self.list_sifter.LoadRSSFeeds()
        
        # load favorites --------
        # might not need this try:
        try:
            self.favorites.ReadFaves() #self.faves_playlist_location)
        except:
            print "Faves load error"
                
        #autoplay ---------------
        # should be one of the last things loaded
        if self.autoplay == True:
            self.OnPlayClick(event=None)

# ---------------------------------------------------------
#-----------------------------------------------------------
    def CheckSysArgs(self, passed_sysarg, on_load=True):
        if len(passed_sysarg) == 2:
            file_name = unicode(passed_sysarg[1], CHARSET)            
            if file_name.endswith('.xspf'):
                self.ReadPlaylist(file_name)
                #self.SavePlaylist(self.main_playlist_location)
                self.autoplay = True
            elif file_name.endswith('.m3u'):
                self.ReadWinampPlaylist(file_name)
                #self.SavePlaylist(self.main_playlist_location)
                self.autoplay = True
            elif file_name.endswith('.mp3'):                
                self.tab_song_collection.ScolFileAdd([file_name])
                #self.SavePlaylist(self.main_playlist_location)
                self.autoplay = True
            else:
                if on_load == True:
                    self.ReadPlaylist(self.main_playlist_location)
                    #self.GetPlaylistFromDatabase()
                
        elif len(passed_sysarg) == 3:
            #::C:\Users\[username]\Desktop\GrooveWalrus\gw.exe
            #::-url
            #::gwp://u2:rattle%20and%20hum/
            meat = passed_sysarg[2].split('gwp://')
            if len(meat) == 2:                
                if len(meat[1].split(':')) == 2:
                    song = meat[1].split(':')[1].replace('%20', ' ').replace('/', '')
                    artist = meat[1].split(':')[0].replace('%20', ' ')
                    self.SetPlaylistItem(self.lc_playlist.GetItemCount(), artist, song)
                    self.autoplay = True
            else:
                if on_load == True:
                    self.ReadPlaylist(self.main_playlist_location)
                    #self.GetPlaylistFromDatabase()
        else:
            if on_load == True:
                self.ReadPlaylist(self.main_playlist_location)
                #self.GetPlaylistFromDatabase()
            
#-----------------------------------------------------------            

    # pubsub receivers-----------------
    def SetReceiver(self, target, topic):
        #set up a reciever for pub sub, work around for plugins
        listener = pub.subscribe(target.GenericReceiverAction, topic)        
        return listener
        
    def KillReceiver(self, target):
        pub.unsubscribe(target)
        
    def LocalReceivers(self):
        pub.subscribe(self.AlbumReceiverAction, 'main.album')
        pub.subscribe(self.SongIdReceiverAction, 'main.song_id')
        pub.subscribe(self.TimeReceiverAction, 'main.song_time.text')
        pub.subscribe(self.TimeSecondsReceiverAction, 'main.song_time.seconds')
        pub.subscribe(self.SetCachedTimeReceiverAction, 'main.playback.45_seconds')
        pub.subscribe(self.UpdateMessengerStatus, 'main.playback.new')
        pub.subscribe(self.PyroMessage, 'main.pyro')
        
    def PyroMessage(self, message):
        #pub.sendMessage('main.playback.45_seconds', {'artist':self.current_song.artist, 'song':self.current_song.song})
        passed = False
        playback = False
        if 'sysarg' in message.data:
            passed = message.data['sysarg']
        if 'playback' in message.data:
            playback = message.data['playback']           

        if passed:
            #print passed
            self.CheckSysArgs(passed, on_load=False)
            #bring existing player into focus
            self.parent.BringUpTop()
        if playback == 'play':
            self.OnPlayClick(event=None)            
        elif playback == 'stop':
            self.OnStopClick(event=None)
        elif playback == 'previous':
            self.OnBackwardClick(event=None)
        elif playback == 'next':
            self.OnForwardClick(event=None)
        elif playback == 'mute':
            self.OnMuteClick(event=None)
        elif playback == 'volume_up':
            self.OnVolumeUp(event=None)
        elif playback == 'volume_down':
            self.OnVolumeDown(event=None)
        elif playback == 'random':
            self.OnRandomClick(event=None)
        elif playback == 'repeat':
            self.OnRepeatClick(event=None)
        elif playback.isdigit() == True:
            self.PlaySong(int(playback))
        else:
            self.NiceOut()
        
    def AlbumReceiverAction(self, message):
        # {'album':album, 'playlist_number':self.playlist_number}
        # update playlist
        self.lc_playlist.SetStringItem(message.data['playlist_number'], C_ALBUM, message.data['album'])
        self.current_song.album = message.data['album']
        
    def SetCachedTimeReceiverAction(self, message):
        # check if file previously cached
        #print '45 seconds'
        temp_dir = system_files.GetDirectories(self).TempDirectory()
        file_name_plain = self.current_song.artist + '-' + self.current_song.song + '.mp3'
        cached_file = file_cache.CreateCachedFilename(temp_dir, file_name_plain)
        cached_file_name = cached_file[0]
        if cached_file[1] == True:            
            self.current_song.SetSongTimeSeconds(local_songs.GetMp3Length(cached_file_name))            
            self.current_song.SetSongTime(self.ConvertTimeFormated(self.current_song.song_time_seconds))
            try:
                self.lc_playlist.SetStringItem(self.current_song.playlist_position, C_TIME, self.ConvertTimeFormated(self.current_song.song_time_seconds))
            except Exception, expt:
                print "SetCachedTimeReceiverAction: " + str(Exception) + str(expt)
        
    def SongIdReceiverAction(self, message):        
        # update playlist
        #print message.data
        self.lc_playlist.SetStringItem(message.data['playlist_number'], C_ID, message.data['song_id'])
        self.SavePlaylist(self.main_playlist_location)
        
    def TimeReceiverAction(self, message):        
        # update playlist
        t = message.data['time']
        i = message.data['playlist_number']
        #print message
        #print message.data
        if (t != '') & (i != -1):
            try:
                self.lc_playlist.SetStringItem(i, C_TIME, t)
            except Exception, expt:
                print "TimeReceiverAction: " + str(Exception) + str(expt)
        #self.SavePlaylist(self.main_playlist_location)
        
    def TimeSecondsReceiverAction(self, message):        
        # update playlist
        self.lc_playlist.SetStringItem(message.data['playlist_number'], C_TIME, self.ConvertTimeFormated(message.data['time_seconds']))
        self.current_song.SetSongTimeSeconds(message.data['time_seconds'])
        #self.SavePlaylist(self.main_playlist_location)

    def UpdateMessengerStatus(self, message):        
        # update xfire status
        messenger_enabled = options_window.GetSetting('messenger-enabled', self.FILEDB)
        messenger_path = options_window.GetSetting('messenger-path', self.FILEDB)
        
        if (messenger_enabled != False) & (messenger_path != False):
            if (messenger_enabled == '1'):
                song_link = self.GenerateShareLink(self.current_song.artist, self.current_song.song)
                status_text = self.current_song.artist + " - " + self.current_song.song + " : " + PROGRAM_NAME
                #print status_text
                #"c:\\Progra~2\\xfire\\xfire.exe /url xfire:status?text="
                filename= messenger_path + status_text
                fs=os.popen3(filename,'b')
        
    # ---------------------------------
    def NiceOut(self):
        t_time = '0:00'
        blk = 0
        if self.current_song.status == 'playing':
            t_time = self.ConvertTimeFormated(self.time_count)
            percent = float(self.time_count) / float(self.current_song.song_time_seconds)
            blk = int(percent * 40)
        blk_s = ''
        for x in range (0, 39):
            if x < blk:
                blk_s = blk_s + 'X'
            else:
                blk_s = blk_s + '_'
                
        print '<pre>     artist:   ' + self.current_song.artist
        print '       song:   ' + self.current_song.song
        print '      album:   ' + self.current_song.album        
        print '       time:   ' + t_time + " / " + self.ConvertTimeFormated(self.current_song.song_time_seconds)        
        print '               [' + blk_s + ']'
        print '     status:   ' + self.current_song.status + '     rdm: ' + str(self.random_toggle) + '     rpt: ' + str(self.repeat_toggle) + ' ' + self.repeat_toggle_type
        print ' '
        print ' '
        for x in range(0, self.lc_playlist.GetItemCount()):
            if x == self.current_song.playlist_position:
                print '   <span class="current">' + str(x).zfill(3) + '. ' + self.lc_playlist.GetItem(x, C_ARTIST).GetText() + ' - <a class="list_item" href="/' + str(x) + '">' + self.lc_playlist.GetItem(x, C_SONG).GetText() + '</a></span>'
            else:            
                print '   ' + str(x).zfill(3) + '. ' + self.lc_playlist.GetItem(x, C_ARTIST).GetText() + ' - <a class="list_item" href="/' + str(x) + '">' + self.lc_playlist.GetItem(x, C_SONG).GetText() + '</a>'
            
        print '</pre>'
        
    # background colours / pictures --------------------
    def RandomBackgroundColour(self, event):        
        #colour_array = ('#ced1ff', '#f7b3f5', '#ff95ae', '#ffd074', '#e6ff3a', '#aaff99', '#e4e4e4')
        #rand_col = random.randint(0, (len(colour_array) - 1))
        self.panel.SetBackgroundStyle(wx.NORMAL)
        
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            rand_col = data.GetColour().Get()
        
            self.panel.SetBackgroundColour(rand_col)#colour_array[rand_col])
            #self.parent.SetBackgroundColour(rand_col)#colour_array[rand_col])
            self.sl_volume.SetBackgroundColour(rand_col)#colour_array[rand_col])                    
            # for updating slider background to:
            event = wx.SysColourChangedEvent()
            self.ProcessEvent(event)
            #refresh it
            self.parent.Refresh()
            options_window.SetSetting('background-color', str(rand_col), self.FILEDB)
            options_window.SetSetting('background-use-graphic', '0', self.FILEDB)
        dlg.Destroy()
        
    def OnResize(self, event):
        #dc = wx.PaintDC(self.panel)
        #self.panel.Refresh()
        event.Skip()
        #pass
            
    def OnEraseBackground(self, event):
        """ Add a picture to the background """             
        if (os.path.isfile(self.background_file)) & (options_window.GetSetting('background-use-graphic', self.FILEDB) == '1'):
            # yanked from ColourDB.py
            dc = event.GetDC()
        
            if not dc:
                dc = wx.ClientDC(self)
                rect = self.GetUpdateRegion().GetBox()
                dc.SetClippingRect(rect)
            dc.Clear()        
            #bmp = wx.Bitmap(background)
            #dc.DrawBitmap(bmp, 0, 0)
            w, h = self.panel.GetClientSize()
            dc.SetBrush(wx.BrushFromBitmap(wx.Bitmap(self.background_file)))
            dc.DrawRectangle(0, 0, w, h)
        event.Skip()
            
    def OnLoadBackgroundImage(self, event):
        wildcard = "Graphic Files (*.png;*.jpg;*.gif;*.bmp)|*.png;*.jpg;*.gif;*.bmp|"   \
            "PNG (*.png)|*.png|"     \
            "JPG (*.jpg)|*.jpg|"
            
        dlg = wx.FileDialog(
            self, message="Choose a background image",
            defaultDir=system_files.GetDirectories(self).DataDirectory(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )# wx.MULTIPLE | 

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            #print paths
            #self.BackupList()
            #self.lc_playlist.DeleteAllItems()
            for path in paths:
                self.background_file = path
                options_window.SetSetting('background-use-graphic', '1', self.FILEDB)
                self.panel.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
                self.panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
                self.Refresh()                
                options_window.SetSetting('background-graphic', path, self.FILEDB)
        dlg.Destroy()
    
    # ---------------------------------
    
    def SetBackend(self, event):
        #sets backend type, pymedia, wx.media, pyglet
        if event != None:
            self.SaveOptions(None)
            self.OnStopClick(None)
        
        backend_types = ['pymedia', 'wx.media', 'pyglet']
        self.use_backend = backend_types[self.rx_options_backend.GetSelection()]
        
        if self.use_backend == 'pymedia':
            self.player = player_pymedia.Player(self)
        elif self.use_backend == 'wx.media':
            self.player = player_wx.Player(self)
        else:
            self.player = player_pyglet.Player(self)
            
    def OnClearCacheClick(self, event):
        #clear the cache
        temp_dir = system_files.GetDirectories(self).TempDirectory()
        file_cache.CheckCache(temp_dir, 0)
        
    def OpenWebsite(self, event):        
        default_app_open.dopen('http://groove-walrus.turnip-town.net')
        
    def OnLoadAdvancedOptions(self, event):
        # show options window
        song_db_window = advanced_options.AdvancedOptionsWindow(self.parent)
        song_db_window.ShowMe()
        
    def SetNetworkStatus(self, site, status):
        """ sets the color of the status buttons """
        colors = [(0,192,0), (255,255,0), (255,0,0)]
        if site=='lastfm':
            self.bu_status_lf.SetBackgroundColour(colors[status])
            pass
        else:
            self.bu_status_gs.SetBackgroundColour(colors[status])
            pass
#    def LoadingWindow(self):
 #       """ puts a window over the control that's loading something """
  #      dlg = wx.Dialog(self, -1, "Details", size=(100, 55), style=wx.FRAME_SHAPED)
   #     dlg.SetBackgroundColour(wx.WHITE)
    #    file_name = GRAPHICS_LOCATION + 'loading.gif'
     #   ani = wx.animate.Animation(file_name)
#        ctrl = wx.animate.AnimationCtrl(dlg, -1, ani)
 #       #ctrl.SetUseWindowBackgroundColour()
  #      ctrl.Play()
   #     sizer = wx.BoxSizer(wx.VERTICAL)
    #    sizer.Add(ctrl, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
#        dlg.SetSizer(sizer)
 #       dlg.SetAutoLayout(True)
  #      return dlg
    def GetSongRating(self, track_id, playlist_number):
        query = "SELECT rating_type_id FROM m_rating WHERE track_id = " + str(track_id)
        results = local_songs.DbFuncs().GetGenericResults(query)
        if len(results) == 1:
            rating = results[0][0]
            self.lc_playlist.SetItemImage(int(playlist_number), rating)            
            #self.lc_playlist.SetStringItem(int(playlist_number), 5, str(rating))
  
    def GetAllSongRatings(self, start_from=0):
        #check all song on the playlist for ratings
        #county = 25
        #if self.lc_playlist.GetItemCount() < 25:
        #    county = self.lc_playlist.GetItemCount()
        for x in range(start_from, self.lc_playlist.GetItemCount()):#county):
            artist = self.lc_playlist.GetItem(x, C_ARTIST).GetText()
            song = self.lc_playlist.GetItem(x, C_SONG).GetText()
            try:
                q_track_id = local_songs.DbFuncs().GetOnlyTrackId(artist, song)
            except Exception, expt:
                print str(Exception)+str(expt)
                q_track_id = False
            if q_track_id != False:
                self.GetSongRating(q_track_id, x)
                
    def ImportGroovesharkPlaylist(self, event):
        """ Javi S. 2010/08/29 imports GrooveShark playist"""
        dlg = wx.TextEntryDialog(self, 'Insert the playlist URL or ID', 'Import GrooveShark Playlist')
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            playlist_string = dlg.GetValue()
            if (playlist_string != None) & (playlist_string != ""):
                playlist_parts = playlist_string.split('/')
                try:
                    playlist_id = int(playlist_parts[len(playlist_parts)-1])
                except:
                    dlg = wx.MessageDialog(self.parent, "Invalid playlist URL or ID", 'Alert', wx.OK | wx.ICON_WARNING)
                    if (dlg.ShowModal() == wx.ID_OK):
                        dlg.Destroy()
                    return
                data_dir = system_files.GetDirectories(self).DataDirectory() + os.sep
                g_version = GetLocalGroovesharkVersion(data_dir)
                g_session = jsonrpcSession(None, g_version)
                g_session.startSession()
                mylist = playlist.playlistFromId(g_session, playlist_id)
                               
                add_arr = []
                for x in range(0, len(mylist.songs)-1):
                    add_dict = {}
                    add_dict['artist'] = mylist.songs[x].artistName
                    add_dict['song'] = mylist.songs[x].name
                    add_dict['album'] = mylist.songs[x].albumName
                    add_dict['id'] = mylist.songs[x].id
                    add_arr.append(add_dict)
                self.SuperAddToPlaylist(add_arr, plize=True)
        dlg.Destroy()
                
    # image lists -----------------------------------
    def RateImageList(self):
        # song rating imagelist
        rate_images = wx.ImageList(16, 16, True)        
        image_files = [
            GRAPHICS_LOCATION + 'weather-clear-night.png', 
            GRAPHICS_LOCATION + 'weather-storm.png', 
            GRAPHICS_LOCATION + 'weather-overcast.png', 
            GRAPHICS_LOCATION + 'weather-few-clouds.png', 
            GRAPHICS_LOCATION + 'weather-clear.png',
            GRAPHICS_LOCATION + 'arrow-down-table.png', 
            GRAPHICS_LOCATION + 'arrow-up-table.png', 
            GRAPHICS_LOCATION + 'arrow-right-table.png',
            GRAPHICS_LOCATION + 'arrow-left-table.png',
            GRAPHICS_LOCATION + 'arrow-empty-table.png'
            ]
        for file_name in image_files:
            bmp = wx.Bitmap(file_name, wx.BITMAP_TYPE_PNG)
            rate_images.Add(bmp)
        return rate_images
        
    def PlaylistImageList(self):
        # song rating imagelist
        rate_images = wx.ImageList(16, 16, True)        
        image_files = [
            GRAPHICS_LOCATION + 'format-indent-more.png', 
            GRAPHICS_LOCATION + 'format-justify-fill.png', 
            GRAPHICS_LOCATION + 'format-justify-left.png'
            ]
        for file_name in image_files:
            bmp = wx.Bitmap(file_name, wx.BITMAP_TYPE_PNG)
            rate_images.Add(bmp)
        return rate_images
        
    def ColumnImageList(self):
        # song rating imagelist
        rate_images = wx.ImageList(16, 16, True)        
        image_files = [
            GRAPHICS_LOCATION + 'arrow-down-table.png', 
            GRAPHICS_LOCATION + 'arrow-up-table.png', 
            GRAPHICS_LOCATION + 'arrow-right-table.png',
            GRAPHICS_LOCATION + 'arrow-left-table.png',
            GRAPHICS_LOCATION + 'arrow-empty-table.png'
            ]
        for file_name in image_files:
            bmp = wx.Bitmap(file_name, wx.BITMAP_TYPE_PNG)
            rate_images.Add(bmp)
        return rate_images
        
    # scobble --------------------------
    def SetScrobb(self):
        # set up scrobbing
        # should only be called on loading or if you change your setttings
        # *** thread this sucka sometime
        self.current_song.scrobble_song = 0
        self.scrobbed_active = 0
        username = self.tc_options_username.GetValue()
        password = self.tc_options_password.GetValue()        
        if (len(username) > 0) & (len(password) > 0):
            self.SetNetworkStatus('lastfm', 1)
            md5_password = pylast.md5(password)
            client_id = LASTFM_CLIENT_ID
            client_version = PROGRAM_VERSION
            try:
                self.song_scrobb = pylast.Scrobbler(client_id, client_version, username, md5_password)                
                self.session_key = self.song_scrobb._get_session_id()
                self.st_options_auth.SetLabel('Authorized: ' + time.asctime())  
                self.scrobbed_active = 1
                self.SetNetworkStatus('lastfm', 0)
            except Exception, expt:
                print str(Exception) + str(expt)
                self.st_options_auth.SetLabel('Status: something failed. User/password?')
                self.st_options_auth.SetBackgroundColour('Yellow')
                self.SetNetworkStatus('lastfm', 2)
                #self.nb_main.SetSelection(NB_OPTIONS)
        
    def GenerateSessionKey2(self, regenerate=False):
        # generate a non-song scrobbling seesion key
        self.session_key2 = None        
        #check if scrobbling is enabled, yes: get key, no: return None
        if self.cb_options_scrobble.IsChecked():        
            username = self.tc_options_username.GetValue()
            password = self.tc_options_password.GetValue()
            if (password != '') & (username !='' ):
                self.SetNetworkStatus('lastfm', 1)
                if (self.session_key2 == None) or (regenerate == True):
                    last_sess = pylast.SessionKeyGenerator(API_KEY, '6a2eb503cff117001fac5d1b8e230211')
        
                    md5_password = pylast.md5(password)
                    self.session_key2 = last_sess.get_session_key(username, md5_password)
                    if self.session_key2 != None:
                        self.SetNetworkStatus('lastfm', 0)
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
            
            
    #-------------------------------------
    def OnTimer(self, event):
        # the heartbeat of the evil machine
        
        #update the playback panel
        self.pa_playback.Refresh()
        
        if self.current_song.status != 'paused':
            self.time_count = self.time_count + 1
           
        if self.time_count >= 12000:
            self.time_count = 0
            
        # check if we should scrobb this track
        # play time around 70%
        # don't try to autherize until you've started playing a track
            
        if self.current_song.song_time_seconds != 0:
        
            if self.time_count == 45:
                #send a pubsub event at 45 seconds
                pub.sendMessage('main.playback.45_seconds', {'artist':self.current_song.artist, 'song':self.current_song.song})
        
            if (self.scrobbed_active == 0) & (float(self.time_count) / float(self.current_song.song_time_seconds) > .4) & (self.auth_attempts == 0):
                self.auth_attempts = 1
                self.SetScrobb()
                
            if (float(self.time_count) / float(self.current_song.song_time_seconds) > .7) & (self.gobbled_track != 1) & (self.current_song.status != "stopped"):
                #save stats for local db
                self.gobbled_track = 1                
                #THREAD
                #print song_id
                ti = WebFetchThread(self, self.current_song.artist, self.current_song.song, self.current_song.album, 'SONGINFO')
                #THREAD
                ti.start()
                
            if (self.db_submit_complete == False) & (float(self.time_count) / float(self.current_song.song_time_seconds) > .95):
                # add 'complete' to played table ==
                q_track_id = local_songs.DbFuncs().GetTrackId(self.current_song.groove_id, self.current_song.music_id, self.current_song.artist, self.current_song.song)
                local_songs.DbFuncs().InsertPlayedData(q_track_id, played_type_id=1)
                self.db_submit_complete = True
                #==================================
        
            if (float(self.time_count) / float(self.current_song.song_time_seconds) > .6) & (self.current_song.scrobble_song != 1) & (self.scrobbed_active == 1) & (self.current_song.status != "stopped"):
            
                time_started = str(int(time.time()))
                self.current_song.scrobble_song = 1
                port = self.rx_options_scrobble_port.GetSelection()
                s_album=''
                if self.cb_options_scrobble_album.GetValue() == 1:
                    s_album=self.current_song.album
                #check checkbox to see if we should scrobble
                if self.cb_options_scrobble.GetValue() == 1:
                    try:
                        self.SetNetworkStatus('lastfm', 1)
                        self.song_scrobb.scrobble(self.current_song.artist, self.current_song.song, time_started, 'P', 'L', self.current_song.song_time_seconds, s_album, "", "", port)
                        print 'scobbled'
                        self.SetNetworkStatus('lastfm', 0)
                        #album=""
                    except pylast.BadSession:
                        self.SetNetworkStatus('lastfm', 2)
                        self.SetScrobb()
                        self.song_scrobb.scrobble(self.current_song.artist, self.current_song.song, time_started, 'P', 'L', self.current_song.song_time_seconds, s_album, "", "", port)
                        #pylast.BadSession:
                        
            if self.cb_options_prefetch.GetValue() == False:
                self.prefetch = False

            if (float(self.time_count) / float(self.current_song.song_time_seconds) > .5) & (self.prefetch == True):
                #let's fetch the next track if possible
                print 'pre-fetching...'
                self.prefetch = False                
                pf_artistsong =  prefetch.PreFetch(self).GetNextSong()
                print pf_artistsong
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
        if (self.current_song.song_time_seconds > 0) & (self.time_count > self.current_song.song_time_seconds) & (self.current_song.status != "stopped"):
            #print 'next-track'
            if self.current_local != None:
                self.current_local.stop()
            # stop recording if it's reecording
            #if self.recording_status == True:
                #self.recorder.stop()
                #self.recording_status = False
            playlist_total = self.lc_playlist.GetItemCount()
            if (self.repeat_toggle == True) & (self.repeat_toggle_type == 'One'):
                self.PlaySong(self.current_song.playlist_position)
            elif  (playlist_total - 1) > self.current_song.playlist_position:
                # play next track
                self.PlaySong(self.current_song.playlist_position + 1)
            else:
                # go back to the start, if repeat is set
                if (self.repeat_toggle) | (self.random_toggle) == True:
                    self.PlaySong(0)
                else:
                #we've reached teh end, the end my friend
                    self.current_song.status = 'stopped'
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
            #self.recorder.record(self.current_song.artist, self.current_song.song, record_dir, bitrate)
            #self.recording_status = True
        
            
# --------------------------------------------------------- 
    # search----------------------------            
    def OnSearchClick(self, event):
        # search field, then search
        query_string = self.tc_search.GetValue()        
        self.SearchIt(query_string)
        
    def SearchIt(self, query_string):
        # check if we add to playlist, or open the search form
        if len(query_string) > 0:
            self.nb_main.SetSelection(NB_PLAYLIST)
            self.search_window.SetValue(query_string)
            self.search_window.show_me()
            self.search_window.SearchIt(query_string)            
            self.search_window.lc_search.Select(0)
        else:
            self.search_window.show_me()
            
    def SearchAgain(self, event):
        # get currently selected playlist item, and search for it
        val = self.lc_playlist.GetFirstSelected()
        if val >= 0:
            track = self.lc_playlist.GetItem(val, C_SONG).GetText()
            artist = self.lc_playlist.GetItem(val, C_ARTIST).GetText()
            self.SearchIt(artist + ' ' + track)
            
    #-------------------------------------        
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
        if self.update_event == False:
            self.SavePlaylist(self.main_playlist_location)
            self.SaveOptions(event)
            options_window.SetSetting('main-volume', self.sl_volume.GetValue(), self.FILEDB)
        self.parent.Destroy()
        #sys.exit()#1
        #os._exit()#2
        
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
        #self.BackupList()
        if self.cb_options_list_clear.GetValue():
            self.lc_playlist.DeleteAllItems()
            self.current_song.playlist_position = -1
            
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
                if dlg.GetValue() =='':                    
                    data_dict = {'version':' '}
                else:
                    #get the version number from the file                    
                    data_dict = {'version':dlg.GetValue()}                    
                read_write_xml.xml_utils().save_generic_settings(data_dir, file_name, data_dict)
        dlg.Destroy()
        
    # volume ----------------------------
    def SetVolume(self, volume):
        soundmixer.SetMasterVolume(volume)
        #wx.media too
        self.player.SetVolume(volume)
        #print volume
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
            
    # tabs ------------------------
    def ShowTab(self, location):
        # display a notebook tab or the search form
        #NB_PLAYLIST = 0  #NB_LAST = 1  #NB_ALBUM = 2  #NB_FAVES = 3
        #NB_SIFT = 4  #NB_ABOUT = 5  #WN_SEARCH = 99
        if location < 99:
            self.nb_main.SetSelection(location)
        else:
            self.nb_main.SetSelection(NB_PLAYLIST)
            self.search_window.show_me()
        
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

    def OnUpdateClick(self, event):
        # open website
        #version_check.VersionCheck(self, PROGRAM_VERSION).DisplayNewVersionMessage()
        self.update_event = True
        dlg = wx.MessageDialog(self, 'Launch Version Update?',
                               'Launcher', wx.YES_NO | wx.ICON_INFORMATION )
        if (dlg.ShowModal() == wx.ID_YES):        
            sys.stdout.flush()
            if os.path.isfile (SYSLOC + os.sep + "version_update.exe"):
                #program = "version_update.exe"
                program = SYSLOC + os.sep + "version_update.exe"
                arguments = ["v=" + PROGRAM_VERSION]
                os.execvp(program, (program,) +  tuple(arguments))

                #os.execvp("version_update.exe", ['v='+PROGRAM_VERSION])
                #self.parent.Destroy()
                self.KillCurrent()
            elif os.path.isfile (SYSLOC + os.sep + "version_update.py"):            
                child = subprocess.Popen("python version_update.py v=" + PROGRAM_VERSION)
                #self.parent.Destroy()
                self.KillCurrent()
                #if os.name == 'nt':
                #    os.execvp("gw.py", [])
                #else:
                #    os.execvp("python", ['gw.py'])
            else:
                dlg = wx.MessageDialog(self.parent, "Can't find version_update.exe/version_update.py\r\nThis is not good.", 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        dlg.Destroy()
        
    def KillCurrent(self):
        #sys.exit()#1
        #os._exit()#2
        pass
        
# --------------------------------------------------------- 
# play click events---------------------------------------- 
    def OnPlayClick(self, event):
        #handles playing and pausing                

        if self.current_song.status == 'paused':
            self.TogglePause()
            self.current_song.status = 'playing'
            self.SetPlayButtonGraphic('pause')            
        elif (self.current_song.status == 'playing'):
            self.TogglePause()
            self.current_song.status = 'paused'
            self.SetPlayButtonGraphic('play')
        else:
            val = self.current_song.playlist_position #self.lc_playlist.GetFirstSelected()
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
        """ toggles between pausing and playing """
        self.player.TogglePause(self.current_song.status)
            
    def OnPlayListPlayClick(self, event):
        # get selected search relsult list item and add to playlist
        val = self.lc_playlist.GetFirstSelected()
        if val >= 0:
            self.PlaySong(val, True)
            self.SetPlayButtonGraphic('pause')
            
    def OnStopClick(self, event):
        # pymedia stop local thread
        self.StopAll()
        
        # add 'stopped' to played table ==
        if self.current_song.status == 'playing':
            q_track_id = local_songs.DbFuncs().GetTrackId(self.current_song.groove_id, self.current_song.music_id, self.current_song.artist, self.current_song.song)
            local_songs.DbFuncs().InsertPlayedData(q_track_id, played_type_id=2)
        #=================================        
        self.current_song.status = 'stopped'
        self.download_percent = 0        
        self.SetPlayButtonGraphic('play')
            
    def OnForwardClick(self, event):    
        # add 'skipped' to played table ==
        if self.current_song.status == 'playing':
            q_track_id = local_songs.DbFuncs().GetTrackId(self.current_song.groove_id, self.current_song.music_id, self.current_song.artist, self.current_song.song)
            local_songs.DbFuncs().InsertPlayedData(q_track_id, played_type_id=3)
        #=================================
    
        # skip to the next rack on the playlist
        val = self.current_song.playlist_position #self.lc_playlist.GetFirstSelected()
        if (val >= 0) & (val < (self.lc_playlist.GetItemCount() - 1)):
            # print val
            self.PlaySong(val + 1)
        elif val >= 0:
            self.PlaySong(0)
        else:
            #nothing is slected
            self.PlaySong(0)
            
    def OnBackwardClick(self, event):    
        #== add 'skipped' to played table ==
        if self.current_song.status == 'playing':
            q_track_id = local_songs.DbFuncs().GetTrackId(self.current_song.groove_id, self.current_song.music_id, self.current_song.artist, self.current_song.song)
            local_songs.DbFuncs().InsertPlayedData(q_track_id, played_type_id=4)
        #===================================
    
        # skip to the next rack on the playlist
        val = self.current_song.playlist_position #self.lc_playlist.GetFirstSelected()
        if (val > 0):
            # print val
            self.PlaySong(val - 1)
        elif val == 0:          
            self.PlaySong(self.lc_playlist.GetItemCount() - 1)
        else:
            #nothing is slected
            self.PlaySong(0)
            
    def StopAll(self):
        """ stop all playback """
        self.player.Stop()
            
# --------------------------------------------------------- 
# play functions------------------------------------------- 
    def PlaySong(self, playlist_number, clicked=False):
        # play passed song, clicked = True if user clicked to play
        
        # stop current song --------
        self.StopAll()
        
        if self.lc_playlist.GetItemCount() != 0:
    
            #---------------------------------------
            self.gobbled_track = 0
            self.download_percent = 0
            self.prefetch = True
            self.current_song.status = 'loading'
            
            # reset last.fm auth attmpts, to try and autherize each time
            # a new song is played, if it hasn't successfully been autherized before
            self.auth_attempts = 0
            
            #---------------------------------------                         
            # check for random
            if (self.random_toggle == True) & (clicked == False):
                playlist_number = random.randint(0, (self.lc_playlist.GetItemCount() - 1))
                # picks the same song again doesn't reload the flash file
    
            # verify that playlist number is valid:
            if playlist_number > (self.lc_playlist.GetItemCount() -1):
                playlist_number = 0
                
            #--------------------------------------- 
            cs = self.current_song
            #reset things that need to be reset
            cs.SetDefaultValues()
            cs.playlist_position = playlist_number
            cs.artist = self.lc_playlist.GetItem(playlist_number, C_ARTIST).GetText()
            cs.song = self.lc_playlist.GetItem(playlist_number, C_SONG).GetText()
            cs.album = self.lc_playlist.GetItem(playlist_number, C_ALBUM).GetText()
            cs.song_id = self.lc_playlist.GetItem(playlist_number, C_ID).GetText() #str(self.lc_playlist.GetItem(playlist_number, 3).GetText())
            cs.song_time = self.lc_playlist.GetItem(playlist_number, C_TIME).GetText()
            #cs.track_id = 0
            #cs.song_time_seconds = 0
                   
            #cs = CurrentSong(self, playlist_number, self.current_song.artist, self.current_song.song, self.current_song.album, song_id, duration)
    
            # check the file cache
            cached_file = file_cache.CreateCachedFilename(system_files.GetDirectories(self).TempDirectory(),  cs.artist + '-' + cs.song + '.mp3')
            if cached_file[1] == True:
                if cs.song_id.isdigit():
                    cs.groove_id = cs.song_id
                cs.song_id = cached_file[0]
                #cs.groove_id = cs.song_id
                #cs.music_id = 0
                #self.use_web_music = False
            
            
            #check the id
            cs.CheckId(cs.song_id)
            #check the album
            cs.CheckAlbum(cs.album)
            
            #focus on the current song
            self.lc_playlist.Focus(playlist_number)
            # unselect last played 
            self.lc_playlist.Select(cs.last_played, 0)
            cs.last_played = playlist_number
            # select current
            self.lc_playlist.Select(playlist_number)
            
            #-----------------------------------
            if (cs.song_id.endswith('.mp3') == True):
                sts = local_songs.GetMp3Length(cs.song_id)
                cs.SetSongTimeSeconds(sts)
                cs.SetSongTime(self.ConvertTimeFormated(sts))            
            else:
                if cs.song_time != '':                
                    cs.SetSongTimeSeconds(self.ConvertTimeSeconds(cs.song_time))
                
            #print cs.song_time_seconds
            if cs.song_time_seconds == 0:
                #set a default time
                wminutes = self.sc_options_song_minutes.GetValue()
                wseconds = self.sc_options_song_seconds.GetValue()
                wformated_time = str(wminutes) + ':' + str(wseconds).zfill(2)
                cs.SetSongTime(wformated_time)            
                cs.song_time_seconds = self.ConvertTimeSeconds(wformated_time)
                
                #check the internet
                tx = FetchTimeThread(cs.playlist_position, cs.artist, cs.song)
                tx.start()
    
            #-----------------------------------
            if (self.use_web_music == True) & ((len(cs.song_id) >= 1) & (len(cs.song_id.split('/')) < 2)):
                #use flash webmusic
                print 'webmusic'
                #add delay
                self.time_count = self.sc_options_gs_wait.GetValue() * -1
                
                # publish to pubsub
                pub.sendMessage('main.playback.load', {'artist':cs.artist, 'song':cs.song})
         
                if self.use_backend != 'flash':
                    self.player = self.flash
                    self.use_backend = 'flash'
                
                #self.LoadFlashSong()#cs.song_url, cs.artist, cs.song)
                self.player.Play(self.current_song.song_url)
                #print cs.song_url
                cs.status = 'playing'            
                cs.groove_id = cs.song_id
                cs.music_id = 0
                
            elif (len(cs.song_id) >= 1) & (len(cs.song_id.split('/')) < 2) & (cs.song_id.isdigit()):
                #grooveshark song
                temp_dir = system_files.GetDirectories(self).TempDirectory()
                file_name_plain = cs.artist + '-' + cs.song + '.mp3'
                
                if self.use_backend == 'flash':
                    self.SetBackend(None)
                
                # clean cache dir
                file_cache.CheckCache(temp_dir, self.sl_options_cache_size.GetValue())
                
                # check if file previously cached
                cached_file = file_cache.CreateCachedFilename(temp_dir, file_name_plain)
                cached_file_name = cached_file[0]
                if cached_file[1] == False:                
                    #download file
                    #THREAD
                    current = FileThread(self, cached_file_name, cs.song_id, cs.song, cs.artist, cs.album)                
                    current.start()
                    
                #play song
                self.time_count = -1
                self.player.Play(cached_file_name)
                cs.status = 'playing'
                
                if cs.song_id.isdigit():
                    cs.groove_id = cs.song_id
                cs.music_id = 0
                
            elif os.path.isfile(cs.song_id):
            # local file
                if self.use_backend == 'flash':
                    self.SetBackend(None)
                self.time_count = -1
                self.player.Play(cs.song_id)
                cs.status = 'playing'
                
            else:
                 cs.scrobble_song = 1
                 cs.status = 'stopped'
                 #skip to next song
                 #***self.OnForwardClick(None)
                 
            if cs.status == 'playing':
                print self.use_backend
                self.parent.SetTitle(cs.artist + '-' + cs.song + ' - ' + PROGRAM_NAME + ' ' + PROGRAM_VERSION)
                #self.lc_playlist.Select(playlist_number)
                if os.name == 'nt':
                    self.GetSongArt(cs.artist, cs.album)
                    self.tab_biography.GetArtistBio(cs.artist)
                    
                cs.scrobble_song = 0            
                self.db_submit_complete = False
                
                # add 'start' to played table ==
                q_track_id = local_songs.DbFuncs().GetTrackId(cs.groove_id, cs.music_id, cs.artist, cs.song)
                local_songs.DbFuncs().InsertPlayedData(q_track_id, played_type_id=0)
                #===============================
                cs.track_id = q_track_id
    
                # publish to pubsub
                pub.sendMessage('main.playback.new', {'artist':cs.artist, 'song':cs.song})
                self.SavePlaylist(self.main_playlist_location)
                #print cs
                
            self.GetSongRating(cs.track_id, cs.playlist_position)
# ---------------------------------------------------------  
    # time functions
    def ConvertTimeFormated(self, seconds):
        # convert seconds to mm:ss
        return str(float(seconds) / float(60)).split('.')[0] + ':' + str(abs(seconds) % 60).zfill(2)
        
    def ConvertMilliTimeFormated(self, milliseconds):
        seconds = int(milliseconds) / 1000
        return self.ConvertTimeFormated(seconds)
        
    def ConvertTimeSeconds(self, formated_time):
        # convert mm:ss to seconds
        if len(formated_time.split(':')) >= 2:
            seconds = (int(formated_time.split(':')[0]) * 60) + (int(formated_time.split(':')[1]))
            return seconds
        else:
            return 240

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
            artist = self.lc_playlist.GetItem(x, C_ARTIST).GetText()
            title = self.lc_playlist.GetItem(x, C_SONG).GetText()
            album = self.lc_playlist.GetItem(x, C_ALBUM).GetText()
            song_id = self.lc_playlist.GetItem(x, C_ID).GetText()
            if len(song_id.split('/')) > 1:
                song_id = "file:///" + song_id
                song_id = song_id.replace(' ', '%20')
            elif len(song_id) > 1:
                song_id = "http://grooveshark.com/" + song_id
            song_time = ''
            if len(self.lc_playlist.GetItem(x, C_TIME).GetText()) > 0:
                song_time = str(self.ConvertTimeMilliSeconds(self.lc_playlist.GetItem(x, C_TIME).GetText()))
            track_dict.append({'creator': artist, 'title': title, 'album': album, 'location': song_id, 'duration': song_time})
            
        read_write_xml.xml_utils().save_tracks(filename, track_dict)
        print 'save playlist'
        #self.GetAllSongRatings()
        
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
                    self.tab_song_collection.ScolFileAdd(path)
                else:
                    pass
        dlg.Destroy()
        
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
        if os.path.isfile(filename):        
            f = open(filename)
            #print filename
            clean_path = filename.replace(os.sep, '/').rsplit('/', 1)[0]
            counter = 0
            try:
                self.CheckClear()
                for line in f:
                    if line[0] != '#':
                        filen = clean_path + '/' + line.strip()
                        if os.path.isfile(filen):
                            self.lc_playlist.InsertStringItem(counter, '')
                            self.lc_playlist.SetStringItem(counter, C_ARTIST, local_songs.GetMp3Artist(filen))
                            self.lc_playlist.SetStringItem(counter, C_SONG, local_songs.GetMp3Title(filen))
                            self.lc_playlist.SetStringItem(counter, C_ALBUM, local_songs.GetMp3Album(filen))
                            self.lc_playlist.SetStringItem(counter, C_ID, filen)
                            counter = counter + 1
            finally:
                f.close()
            #self.SavePlaylist(self.main_playlist_location)
            self.ResizePlaylist()
            self.GetAllSongRatings()
        
    def ReadPlaylist(self, filename):
        # take current playlist and write to listcontrol
        #track_dict = read_write_xml.xml_utils().get_tracks(filename)
        if os.path.isfile(filename):
            track_dict = read_write_xml.xml_utils().GetTracksSoup(filename)
                    
            counter = 0
            #print track_dict
            for x in track_dict:
                #print x
                #set value
                try:
                    index = self.lc_playlist.InsertStringItem(counter, '')
                    self.lc_playlist.SetStringItem(counter, C_ARTIST, x['creator'])
                    self.lc_playlist.SetStringItem(counter, C_SONG, x['title'])
                    album = x['album']
                    if album == None:
                        album = ''
                    self.lc_playlist.SetStringItem(counter, C_ALBUM, album)
                    
                    song_id = x['location']
                    if song_id == None:
                        song_id = ''
                    # *** this should be case insensitive File: <> file:
                    song_id = song_id.split('file:///')[-1]
                    song_id = song_id.split('http://grooveshark.com/')[-1]
                    song_id = song_id.replace('%20', ' ')
                    self.lc_playlist.SetStringItem(counter, C_ID, song_id)
                    
                    song_time = x['duration']
                    if song_time == None:
                        song_time = ''
                    if song_time.isdigit():
                        # convert milliseconds to formated time mm:ss
                        song_time = self.ConvertMilliTimeFormated(song_time)
                    self.lc_playlist.SetStringItem(counter, C_TIME, song_time)
                    counter = counter + 1
                except TypeError:
                    print 'error:ReadPlaylist'
                    #pass
            self.ResizePlaylist()
        
    def OnPlaylistRightClick(self, event):        
        # make a menu
        ID_DELETE = 11
        ID_SEARCH = 21
        ID_FAVES = 31
        ID_FIX = 41
        ID_FIX_ALBUM = 51
        ID_CLEAR = 61
        ID_SHARE = 71
        
        menu = wx.Menu()
        
        # make a submenu
        sm = wx.Menu()        
        re = self.SongRate
        ratings_button.MenuAppend(sm, self, re)
        menu.AppendMenu(ID_FAVES, "Rate Song", sm)        
        
        #menu.Append(ID_FAVES, "Rate Song")
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
        wx.EVT_MENU(self, ID_FAVES, self.SongRate)
        wx.EVT_MENU(self, ID_FIX, self.FixPlaylistItem)
        wx.EVT_MENU(self, ID_FIX_ALBUM, self.FixAlbumName)
        wx.EVT_MENU(self, ID_CLEAR, self.ClearId)
        wx.EVT_MENU(self, ID_SHARE, self.MakeShareLink)
        
        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()
        
    def SongRate(self, event):
        #re-rate selected favourite list item
        event_id = event.GetId()
        print event_id
        val = self.lc_playlist.GetFirstSelected()
        music_id = ''
        grooveshark_id = ''
        artist = self.lc_playlist.GetItem(val, C_ARTIST).GetText()
        song = self.lc_playlist.GetItem(val, C_SONG).GetText()
        track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
        ratings_button.AddRating(self, track_id, event_id)
        if event_id == 4:
            sk = self.GenerateSessionKey2()
            ratings_button.LoveTrack(artist, song, sk)
        self.GetSongRating(track_id, val)
        
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
        #self.SavePlaylist(self.main_playlist_location)
        ##self.ResizePlaylist()
                
    def FixPlaylistItem(self, event):
        # display the song steails window
        if self.lc_playlist.GetFirstSelected() >= 0:
            details_window.DetailsWindow(self).show_me()
            
    def ClearId(self, event):
        # display the song steails window
        val = self.lc_playlist.GetFirstSelected()
        self.lc_playlist.SetStringItem(val, C_ID, '')
        
    def FixAlbumName(self, event):
        # *** should be moved work when checking for cover art
        val = self.lc_playlist.GetFirstSelected()
        artist = self.lc_playlist.GetItem(val, C_ARTIST).GetText()
        song = self.lc_playlist.GetItem(val, C_SONG).GetText()
        album_array = self.GetSongAlbumInfo(artist, song)
        #album_array[1] is album name
        self.lc_playlist.SetStringItem(val, C_ALBUM, album_array[1])
        #save playlist
        self.SavePlaylist(self.main_playlist_location)
        ##self.ResizePlaylist()
        
    def UpdatePlaylistItem(self, current_count, artist, song, album, url, duration=''):
        #set value
        self.lc_playlist.SetStringItem(current_count, C_ARTIST, artist)
        self.lc_playlist.SetStringItem(current_count, C_SONG, song)
        self.lc_playlist.SetStringItem(current_count, C_ALBUM, album)
        self.lc_playlist.SetStringItem(current_count, C_ID, url)
        self.lc_playlist.SetStringItem(current_count, C_TIME, duration)
        ##self.ResizePlaylist()
        ##self.SavePlaylist(self.main_playlist_location)
        
    def SetPlaylistItem(self, current_count, artist, song, album='', url='', duration=''):
        #set value
        index = self.lc_playlist.InsertStringItem(current_count, '')
        self.lc_playlist.SetStringItem(current_count, C_ARTIST, artist)
        self.lc_playlist.SetStringItem(current_count, C_SONG, song)
        self.lc_playlist.SetStringItem(current_count, C_ALBUM, album)
        self.lc_playlist.SetStringItem(current_count, C_ID, url)
        self.lc_playlist.SetStringItem(current_count, C_TIME, duration)
        ##self.ResizePlaylist()
        
    def ResizePlaylist(self, event=None):
        #x_size = self.lc_playlist.GetSize()[0] - 50
        self.lc_playlist.SetColumnWidth(C_RATING, 25)
        self.lc_playlist.SetColumnWidth(C_ARTIST, 150)#x_size*.29)
        self.lc_playlist.SetColumnWidth(C_SONG, 200)#x_size*.40)
        self.lc_playlist.SetColumnWidth(C_ALBUM, 135)#x_size*.29)
        self.lc_playlist.SetColumnWidth(C_ID, 0)
        self.lc_playlist.SetColumnWidth(C_TIME, 50)#wx.LIST_AUTOSIZE_USEHEADER)
        self.nb_main.SetPageText(NB_PLAYLIST, 'Playlist (' + str(self.lc_playlist.GetItemCount()) + ')')
        #if event:
        #    event.Skip()
        
    def DynamicResizePlaylist(self, event=None):
        #get frame size, if > minimum size, set default
        #larger than, set dynamic
        #print event.GetEventType()
        # maximize event gets current size, not size after it's been maximized
        # so we need to call after
        wx.CallAfter(self.DyRes)
        event.Skip()
            
    def DyRes(self):
        if self.parent.GetSize()[0] > (FRAME_WIDTH + 100):
            flex_max = self.lc_playlist.GetSize()[0] - (25 + 50)
            #print self.lc_playlist.GetSize()[0]
            self.lc_playlist.SetColumnWidth(C_RATING, 25)
            self.lc_playlist.SetColumnWidth(C_ARTIST, flex_max*.28)
            self.lc_playlist.SetColumnWidth(C_SONG, flex_max*.38)
            self.lc_playlist.SetColumnWidth(C_ALBUM, flex_max*.28)
            self.lc_playlist.SetColumnWidth(C_ID, 0)
            self.lc_playlist.SetColumnWidth(C_TIME, 50)#wx.LIST_AUTOSIZE_USEHEADER)
            #print 'resizer'
        else:
            self.ResizePlaylist()        
        
    def MakeShareLink(self, event):
        # make link for current song/artist, copy to clippboard
        val = self.lc_playlist.GetFirstSelected()
        artist = self.lc_playlist.GetItem(val, C_ARTIST).GetText()
        song = self.lc_playlist.GetItem(val, C_SONG).GetText()
        song_link = self.GenerateShareLink(artist, song)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(song_link))
        wx.TheClipboard.Close()
        
    def GenerateShareLink(self, artist, song):
        artist = "a=" + artist.replace(' ', '_')
        song = "&s=" + song.replace(' ', '_')
        song_link = SONG_SENDER_URL + artist + song
        return song_link
        
    def ClearAlbumValues(self, event):
        # clear all the album values on the playlist
        for x in range(0, self.lc_playlist.GetItemCount()):
            self.lc_playlist.SetStringItem(x, C_ALBUM, '')
            
    def ClearIdValues(self, event):
        # clear all the album values on the playlist
        for x in range(0, self.lc_playlist.GetItemCount()):
            self.lc_playlist.SetStringItem(x, C_ID, '')
            
    def GenericAddToPlaylist(self, from_list_control, add_album=False):
        #adds selected list items from one list control to another
        
        #backup playlist
        self.BackupList()
        
        val = from_list_control.GetFirstSelected()
        total = from_list_control.GetSelectedItemCount()
        current_count = self.lc_playlist.GetItemCount()
        #print val
        if (val >= 0):            
            artist =    from_list_control.GetItem(val, 0).GetText()
            song =      from_list_control.GetItem(val, 1).GetText()
            if add_album == True:
                album = from_list_control.GetItem(val, 2).GetText()
                self.SetPlaylistItem(current_count, artist, song, album, '')
            else:
                self.SetPlaylistItem(current_count, artist, song, '', '')
            current_select = val
            if total > 1:
                for x in range(1, from_list_control.GetSelectedItemCount()):
                    current_select =    from_list_control.GetNextSelected(current_select)
                    artist =            from_list_control.GetItem(current_select, 0).GetText()
                    song =              from_list_control.GetItem(current_select, 1).GetText()
                    if add_album == True:
                        album = from_list_control.GetItem(current_select, 2).GetText()
                        self.SetPlaylistItem(current_count + x, artist, song, album, '')                        
                    else:
                        self.SetPlaylistItem(current_count + x, artist, song, '', '')

        #save the playlist
        self.SavePlaylist(self.main_playlist_location)        
        
    def SuperAddToPlaylist(self, add_dict, plize=False):
        #backup current db
        #****self.SearchOrPlaylist(artist, song)
        self.ResizePlaylist()
        if len(add_dict) > 0:
            self.BackupList()
            if plize == True:
                self.CheckClear()
                self.nb_main.SetSelection(NB_PLAYLIST)
            #process dictionary
            #[{'song': 'Some song name', 'artist': 'some artist',}, {...},]
            first_last_row = self.lc_playlist.GetItemCount()
            for x in add_dict:
                row_num = self.lc_playlist.GetItemCount()
                index = self.lc_playlist.InsertStringItem(row_num, '')
                for k, v in x.iteritems():                
                    col_num = PLAYLIST_COLUMNS[k]                
                    self.lc_playlist.SetStringItem(row_num, col_num, v)
            self.nb_main.SetPageText(NB_PLAYLIST, 'Playlist (' + str(self.lc_playlist.GetItemCount()) + ')')
            
            self.GetAllSongRatings(start_from=first_last_row)            
        
    def AddAll(self, list_control, num_cols=2):
        add_arr = []
        for val in range(0, list_control.GetItemCount()):
            add_dict = self.ItemToDict(val, list_control, num_cols)
            add_arr.append(add_dict)            
        self.SuperAddToPlaylist(add_arr, plize=True)
        
    def ItemToDict(self, val, list_control, num_cols=2):
        add_dict = {}
        artist = list_control.GetItem(val, C_ARTIST).GetText()
        song = list_control.GetItem(val, C_SONG).GetText()
        
        add_dict['artist'] = artist
        add_dict['song'] = song
        if num_cols >= 3:
            album = list_control.GetItem(val, C_ALBUM).GetText()
            add_dict['album'] = album
        if num_cols >= 4:
            song_id = list_control.GetItem(val, C_ID).GetText()            
            add_dict['id'] = song_id
        if num_cols >= 5:
            duration = list_control.GetItem(val, C_TIME).GetText()
            add_dict['time'] = duration
        return add_dict
        
    def AddSelected(self, list_control, num_cols=2):
        # add from favourite list to the playlist
        val = list_control.GetFirstSelected()
        add_arr = []
        if (val >= 0): 
            for x in range(0, list_control.GetSelectedItemCount()):
                add_dict = self.ItemToDict(val, list_control, num_cols)
                add_arr.append(add_dict)
                val = list_control.GetNextSelected(val)                
            self.SuperAddToPlaylist(add_arr, plize=False)
        
# ---------------------------------------------------------  
# playlist history ---------------------------------------- 
        
    def OnPlaylistHistoryClick(self, event):
        #toggle slider window back and forth displaying the
        out_bmp = wx.Bitmap(GRAPHICS_LOCATION + "go-next.png", wx.BITMAP_TYPE_ANY)
        in_bmp = wx.Bitmap(GRAPHICS_LOCATION + "go-previous.png", wx.BITMAP_TYPE_ANY)
                
        if self.sp_playlist.GetSashPosition() < 10:
            self.sp_playlist.SetSashPosition(360)
            self.bb_playlist_options.SetBitmapLabel(in_bmp)
        else:
            self.sp_playlist.SetSashPosition(1)
            self.bb_playlist_options.SetBitmapLabel(out_bmp)
        
    def SavePlaylistToDatabase(self, event):
        #save the entire playlist to the database
        #good idea? probably not
        #dlg = wx.Dialog(self, -1, '', size=(195, 100), style=wx.FRAME_SHAPED)
        dlg = wx.TextEntryDialog(self, 'Playlist Name', '')
        dlg.SetWindowStyleFlag(wx.FRAME_SHAPED)
        dlg.SetAutoLayout(True)
        dlg.SetBackgroundColour((255, 210, 0, 255))
        bpos = xrc.XRCCTRL(self, 'm_bb_save_playlist').GetScreenPosition()
        dlg.SetPosition((bpos[0] + 40, bpos[1]))
        dlg.SetSize((260, dlg.GetSize()[1] - 30))
        #b = wx.Button(dlg, wx.ID_OK, "Save", (100, 60))
        #b = wx.Button(dlg, wx.ID_CANCEL, "Cancel", (5, 60))
        #wx.StaticText(dlg, -1, "Playlist Name:", size=(180, -1), pos=(5,5))
        #c = wx.TextCtrl(dlg, -1, size=(180, -1), pos=(5, 28))
        val = dlg.ShowModal()
        
        
        if val == wx.ID_OK:
            playlist_arr = []
            playlist_name = dlg.GetValue()
            date_time = time.strftime('%Y-%m-%d %H:%M:%S')
            for x in range(0, self.lc_playlist.GetItemCount()):
                playlist_arr.append((self.lc_playlist.GetItem(x, C_ARTIST).GetText(), self.lc_playlist.GetItem(x, C_SONG).GetText(), x, date_time))
            #save to db
            local_songs.DbFuncs().InsertPlaylistData(playlist_arr)
            #add label
            if (playlist_name != None) & (playlist_name != None):
                local_songs.DbFuncs().InsertPlaylistLabelData(playlist_name, date_time)        
            self.FillPlaylistTree()

        dlg.Destroy()
        
    def QuickSavePlaylist(self, event):
        #save the entire playlist to the database
        #good idea? probably not
        playlist_arr = []
        date_time = time.strftime('%Y-%m-%d %H:%M:%S')
        for x in range(0, self.lc_playlist.GetItemCount()):
            playlist_arr.append((self.lc_playlist.GetItem(x, C_ARTIST).GetText(), self.lc_playlist.GetItem(x, C_SONG).GetText(), x, date_time))
        local_songs.DbFuncs().InsertPlaylistData(playlist_arr)
        #self.OnPlaylistHistoryClick(event=None)
        self.FillPlaylistTree()
        
    def GetPlaylistFromDatabase(self, playlist_date=None):
        #get a specfic playlist from the db
        if playlist_date == None:
            playlist_date_arr = self.GetDatabasePlaylist()
            if len(playlist_date_arr) == 1:
                playlist_date = playlist_date_arr[0][0]
        if playlist_date != None:
            query = "SELECT * FROM m_playlists WHERE playlist_date = '"+ playlist_date + "' ORDER BY playlist_position"
            results_arr = local_songs.DbFuncs().GetGenericResults(query)            
            #return results_arr
        counter = 0
        for x in results_arr:    
            index = self.lc_playlist_history.InsertStringItem(counter, '')
            self.lc_playlist_history.SetStringItem(counter, C_ARTIST, x[1])
            self.lc_playlist_history.SetStringItem(counter, C_SONG, x[2])
            counter = counter + 1
        
    def GetDatabasePlaylist(self, q_limit=1, start_from=0):
        #get a list of playlists
        #SELECT DISTINCT playlist_date FROM m_playlists ORDER BY playlist_date DESC LIMIT 1
        query = "SELECT DISTINCT m_playlists.playlist_date, playlist_label FROM m_playlists LEFT JOIN m_playlist_labels ON m_playlist_labels.playlist_date=m_playlists.playlist_date ORDER BY m_playlists.playlist_date DESC LIMIT " + str(q_limit) + " OFFSET " + str(start_from)
        results_arr = local_songs.DbFuncs().GetGenericResults(query)
        return results_arr
        
    def FillPlaylistTree(self, save_playlist=True):
        #if save_playlist:
        #    self.SavePlaylist()
        res_arr = self.GetDatabasePlaylist(q_limit=25)
        self.tr_playlist_history.DeleteAllItems()
        il = self.PlaylistImageList()
        self.tr_playlist_history.SetImageList(il)
        # you need the following, i don't know why:
        self.il = il        
        
        child1 = self.tr_playlist_history.AppendItem(self.tr_playlist_history_root, 'Current Playlist')
        self.tr_playlist_history.SetPyData(child1, 'Current Playlist')        
        self.tr_playlist_history.SetItemImage(child1, 1)
        self.tr_playlist_history.SelectItem(child1)
        
        #print res_arr
        for x in res_arr:            
            if (x[1] != '') & (x[1] != None):
                label = x[1]
                child3 = self.tr_playlist_history.AppendItem(self.tr_playlist_history_root, label)
                self.tr_playlist_history.SetPyData(child3, x[0])
                self.tr_playlist_history.SetItemImage(child3, 2)
                
        child2 = self.tr_playlist_history.AppendItem(self.tr_playlist_history_root, 'Quick-Saved')
        self.tr_playlist_history.SetPyData(child2, 'Quick-Saved')
        self.tr_playlist_history.SetItemImage(child2, 0)
        for x in res_arr:
            if(x[1] == '') | (x[1] == None):
                label = x[0]
                child3 = self.tr_playlist_history.AppendItem(child2, label)
                self.tr_playlist_history.SetPyData(child3, x[0])
                self.tr_playlist_history.SetItemImage(child3, 2)
            
    def OnTreeSelChange(self, event):
        selected = event.GetItem()
        if self.tr_playlist_history.GetSelection() >= 1:
            #sel_value = self.tr_playlist_history.GetItemText(selected)
            sel_value = self.tr_playlist_history.GetPyData(selected)
            self.lc_playlist_history.DeleteAllItems()
            if sel_value == 'Current Playlist':
                self.ReadPlaylist2(self.main_playlist_location)
            else:
                self.GetPlaylistFromDatabase(sel_value)
        #event.Skip()
        
    def ReadPlaylist2(self, filename):
        # take current playlist and write to listcontrol
        track_dict = read_write_xml.xml_utils().GetTracksSoup(filename)
        counter = 0
        #print track_dict
        for x in track_dict:
            index = self.lc_playlist_history.InsertStringItem(counter, '')
            self.lc_playlist_history.SetStringItem(counter, C_ARTIST, x['creator'])
            self.lc_playlist_history.SetStringItem(counter, C_SONG, x['title'])
            counter = counter +1
        
    def OnPlaylistTreeActivate(self, event):
        #add selected palylist to the main platlist
        self.AddAll(self.lc_playlist_history)
            
    def OnPlaylistTreeRightClick(self, event):
        #compensate for tricky right-click behaviour
        pt = event.GetPosition()
        item, flags = self.tr_playlist_history.HitTest(pt)
        #print self.tr_playlist_history.GetSelection()
        #print item
        if self.tr_playlist_history.GetSelection() != item:
            self.tr_playlist_history.SelectItem(item)

        item_data = self.tr_playlist_history.GetPyData(item)
        if (item_data != "Current Playlist") & (item_data != "Quick-Saved"):
            # make a menu
            ID_DELETE = 1
            ID_PROPERTIES = 2
            ID_RENAME = 3
            ID_LOAD = 4
            menu = wx.Menu()
            menu.Append(ID_DELETE, "Delete")
            menu.AppendSeparator()
            menu.Append(ID_LOAD, "Load Playlist")
            menu.Append(ID_PROPERTIES, "Properties")
            wx.EVT_MENU(self, ID_DELETE, self.DeletePlaylistFromDb)
            wx.EVT_MENU(self, ID_LOAD, self.OnPlaylistTreeActivate)
            wx.EVT_MENU(self, ID_PROPERTIES, self.DisplayPlaylistProperties)
            self.PopupMenu(menu)
            menu.Destroy()
            
        if (item_data == "Current Playlist"):
            # make a menu            
            ID_LOAD = 4
            menu = wx.Menu()            
            menu.Append(ID_LOAD, "Load Playlist")
            wx.EVT_MENU(self, ID_LOAD, self.OnPlaylistTreeActivate)            
            self.PopupMenu(menu)
            menu.Destroy()
            #event.Skip()
        
    def DeletePlaylistFromDb(self, event):
        #delete selected playlist
        p_date = self.tr_playlist_history.GetPyData(self.tr_playlist_history.GetSelection())
        if len(p_date) > 5:
            query = "DELETE FROM m_playlists WHERE playlist_date='" + p_date + "'"
            local_songs.DbFuncs().DeleteQuery(query)
            self.FillPlaylistTree()
            
    def DisplayPlaylistProperties(self, event):
        self.PlaylistProperties()
        
    def OnTreeBeginEdit(self, event):        
        pass
        #self.tr_playlist_history.EditLabel(self.tr_playlist_history.GetSelection())
        
    def OnTreeEndEdit(self, event):        
        selected = event.GetItem()
        sel_value = self.tr_playlist_history.GetPyData(selected)        
        if self.tr_playlist_history.GetPyData(selected) == 'Current Playlist':
            pass
        else:            
            if (event.GetLabel() != None) & (event.GetLabel() != ''):
                local_songs.DbFuncs().InsertPlaylistLabelData(event.GetLabel(), sel_value)        
        #self.FillPlaylistTree()
        #event.Skip()
        
    def PlaylistProperties(self):
        #make a dialog with a listcontrol        
        dlg = wx.TextEntryDialog(self, 'Playlist Name', 'Properties')
        plid = self.tr_playlist_history.GetPyData(self.tr_playlist_history.GetSelection())
        pllb = self.tr_playlist_history.GetItemText(self.tr_playlist_history.GetSelection())
        dlg.SetValue(pllb)
        if dlg.ShowModal() == wx.ID_OK:
            if (dlg.GetValue() != None) & (dlg.GetValue() != ''):
                local_songs.DbFuncs().InsertPlaylistLabelData(dlg.GetValue(), plid)
                self.tr_playlist_history.SetItemText(self.tr_playlist_history.GetSelection(), dlg.GetValue())
                self.FillPlaylistTree()
        dlg.Destroy()
        
# --------------------------------------------------------- 
# edit menu  ----------------------------------------------

    def GetSelectedList(self):
        #figure out which list is selected, playslist or favourites
        if self.lc_playlist.IsShownOnScreen():
            return (self.lc_playlist, 1, 5)
        if self.favorites.lc_faves.IsShownOnScreen():
            return (self.favorites.lc_faves, 1, 5)
        if self.tab_album.lc_album.IsShownOnScreen():
            return (self.tab_album.lc_album, 0, 3)
        if self.lc_lastfm.IsShownOnScreen():
            return (self.lc_lastfm, 0, 3)
        if self.lc_mylast.IsShownOnScreen():
            return (self.lc_mylast, 0, 2)
        if self.list_sifter.lc_sift.IsShownOnScreen():
            return (self.list_sifter.lc_sift, 0, 2)

    def OnKeyPress(self, event=None):
        #check which listctrl is visable
        #save list for undo
        #delete items(s)
        #check if it's the delete key
         if event.GetKeyCode() == wx.WXK_DELETE:
            if self.lc_playlist.IsShownOnScreen():
                self.RemovePlaylistItem()
            #if self.lc_faves.IsShownOnScreen():
                #self.RemoveFavesItem()
                
    def OnChar(self, event):        
        if event.GetKeyCode() == 1:
            #crtl-a
            self.SelectAll(event.GetEventObject())#self.lc_playlist)
                
    def SelectAll(self, list_control):
        for x in range(0, list_control.GetItemCount()):
            list_control.Select(x)
                
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
        (sel_list, start_col, total_col) = self.GetSelectedList()
        if sel_list != None:
            val = sel_list.GetFirstSelected()
            next_val = val
            # iterate over all selected items and copy
            self.copy_array = []
            for x in range(val, val + sel_list.GetSelectedItemCount()):
                list_arr = []
                for y in range(start_col, total_col): #sel_list.GetColumnCount()):
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
        #(sel_list, start_col, total_col) = self.GetSelectedList()
        # always paste to playlist
        #if 
        sel_list = self.lc_playlist
            #cycle through copied items and paste
        #print self.copy_array
        
        for x in range(0, len(self.copy_array)):
            cur_item = sel_list.GetItemCount()
            #if len(self.copy_array[x][0]) > 0:
            index = sel_list.InsertStringItem(cur_item, '')
            for y in range(0, len(self.copy_array[0])):
                print y
                sel_list.SetStringItem(cur_item, y+1, self.copy_array[x][y])

    def OnUndoClick(self, event):
        #toggle between loading default playlist and backup playlist
        #load playlist backup file        
        if self.lc_playlist.IsShownOnScreen():            
            if self.undo_toggle == 0:
                if self.lc_playlist.GetItemCount() > 0:
                    self.SavePlaylist(self.main_playlist_location)
                self.lc_playlist.DeleteAllItems()
                self.ReadPlaylist(self.main_playlist_location_bak)
                self.undo_toggle = 1
            else:
                self.lc_playlist.DeleteAllItems()
                self.ReadPlaylist(self.main_playlist_location)
                self.undo_toggle = 0   
        
    def BackupList(self):
        #if self.lc_faves.IsShownOnScreen():
         #   self.SaveFaves(self.faves_playlist_location_bak)
        #    self.undo_toggle_faves = 0
        #else: # self.lc_playlist.IsShownOnScreen():
        if self.lc_playlist.GetItemCount() > 0:
            self.SavePlaylist(self.main_playlist_location_bak)
            self.undo_toggle = 0
            print 'backup list'
            self.ResizePlaylist()
                
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
        
    def TTA(self, top_tracks_list):
        # THREAD
        current = WebFetchThread(self, '', '', top_tracks_list, 'PLAYCOUNT')
        #THREAD
        current.start()
        
# ---------------------------------------------------------
# cover/bio pic cache  ------------------------------------

#store album art as md5 album name
#store bio pic as md5 artist name

#check for pic locally
#grab from internet

    def CheckImageCache(self, check_string):
        file_types = ['.jpg', '.png', 'gif']
        existing_file_name = None
        for ext in file_types:
            (file_name, is_file) = file_cache.CreateCachedImage(self.image_save_location, check_string, ext)
            if is_file == True:
                existing_file_name = file_name
                break        
        return existing_file_name
        
       
# --------------------------------------------------------- 
# covers --------------------------------------------------  
    def GetSongArt(self, artist, album):
        # get albumcover for artist/song from last.fm
        
        existing_file = None
        
        if (len(artist) > 0) & (len(album) > 0):
            check_string = artist + '-' + album
            existing_file = self.CheckImageCache(check_string)
            
        if existing_file == None:        
            # THREAD
            current = WebFetchThread(self, artist, 'song', album, 'COVERS')
            #THREAD
            current.start()
        else:
            self.SetImage(existing_file, self.image_save_location)
            self.palbum_art_file = existing_file
        
            
    def SaveSongArt(self, art_url, file_name):
        # get albumcover for artist/song from last.fm
        # check that file doesn't exist
        if os.path.exists(self.image_save_location + file_name) == False:
            #print art_url
            try:
                urllib.urlretrieve(art_url, self.image_save_location + file_name)            
                urllib.urlcleanup()                
            except Exception, expt:
                print "SaveSongArt: " + str(Exception)+str(expt)
            #print 'getting new'
        
    def SetImage(self, file_name, dir_name, resize=False):
        # get albumcover for artist/song from last.fm
        if os.path.isfile(dir_name + file_name):
            cover_bmp = wx.Bitmap(dir_name + file_name, wx.BITMAP_TYPE_ANY)
            
            foo = wx.Bitmap.ConvertToImage(cover_bmp)
            sma_bm = self.bm_cover.GetSize()
            if resize == True:
                #for odd shaped bitmaps            
                self.Resizer(foo, sma_bm)           
            else:
                foo.Rescale(sma_bm[0], sma_bm[1])
            goo = wx.BitmapFromImage(foo)
            self.bm_cover.SetBitmap(goo)
            
            # now the large one
            hoo = wx.Bitmap.ConvertToImage(cover_bmp)
            lar_bm = self.tab_album.bm_cover_large.GetSize()
            if resize == True:
                #for odd shaped bitmaps
                #let's skip changing the album page's cover art to the bio pic
                ##self.Resizer(hoo, lar_bm)
                pass
            else:
                hoo.Rescale(lar_bm[0], lar_bm[1])
                ##
                ioo = wx.BitmapFromImage(hoo)
                self.tab_album.bm_cover_large.SetBitmap(ioo)
            #self.bm_cover.Refresh()
            
            self.album_viewer.SetImage(file_name, dir_name)
        
    def Resizer(self, image, target_size):
        #scales a non-square image to make it look nice
        image_size = image.GetSize()
        #scale in the x axis
        hr = float(image_size[0]) / target_size[0]
        hs = float(image_size[1]) / hr
        # rescale it so it's x= 250 y =? to keep aspect
        image.Rescale(target_size[0], hs) #, wx.IMAGE_QUALITY_HIGH)
        image_size = image.GetSize()
        offset = (target_size[1] - image_size[1]) / 2
        image.Resize((target_size[0], target_size[1]), (0,offset), 0, 0, 0)        
        return image        

# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 

class CurrentSong():
    """Nice things about the current song"""
    def __init__(self, parent, playlist_position=-1, artist='', song='', album='', song_id='', song_time=''):
        self.parent = parent
        self.playlist_position = playlist_position
        self.last_played = 0
        self.song = song
        self.artist = artist
        self.album = album
        self.song_time = song_time        
        self.song_id = song_id          #song-id listed on the listctrl, either 'file location or gs id'
        #self.album_graphic = ''
        #self.artist_graphic = ''        
        self.SetDefaultValues()
        #self.CheckId(song_id)
        
    def __str__(self):        
        print '            artist:   ' + self.artist
        print '              song:   ' + self.song
        print '             album:   ' + self.album
        print 'song_id (location):   ' + self.song_id
        print '          track_id:   ' + str(self.track_id)
        print '         groove_id:   ' + str(self.groove_id)
        print 'music_id (file_id):   ' + str(self.music_id)
        return '---end----'
        
    def SetDefaultValues(self):
        #reset to default values
        self.groove_id = 0              #gs' id
        self.track_id = 0               #track id from local db
        self.scrobbed_song = 0
        self.song_type = 'local'
        self.song_url = ''
        self.song_time_seconds = 0
        self.music_id = 0               #file_id~music_id
        self.status = 'stopped'
        
    def SetAlbum(self, album, artist, song):
        if (artist == self.artist) & (song == self.song):
            self.album = album
        
    def SetSongTime(self, song_time):
        self.song_time = song_time
        pub.sendMessage('main.song_time.text', {'time':self.song_time, 'playlist_number':self.playlist_position})
        
    def SetSongTimeSeconds(self, song_time_seconds):
        self.song_time_seconds = song_time_seconds        

    def SetStatus(self, status):
        self.status = status
        
    def CheckId(self, song_id):
        #checks if song is local or not
        if os.path.isfile(song_id) == False:
            #digit is grooveshark id
            if song_id.isdigit() == True:
                self.groove_id = song_id
            else:
                self.song_id = ''
        else:
            #it's a local song
            query_string = self.artist + ' ' + self.song
            query_results = local_songs.DbFuncs().GetResultsArray(query_string, 1, True)
            if len(query_results) == 1:
                #print query_results
                self.music_id = query_results[0][0]
                self.groove_id = 0

        if (self.song_id =='') & (len(self.artist) > 0) & (len(self.song) > 0):
            # query for song id, so we can play the file            
            query_string = self.artist + ' ' + self.song
            # check locally for song
            query_results = local_songs.DbFuncs().GetSpecificResultArray(query_string, self.artist, self.song)            
            if len(query_results) >= 1:                
                self.song_id = query_results[0][4] #str(query_results[0][4])
                self.music_id = query_results[0][0]
                
                #pub.sendMessage('main.song_id', {'song_id':self.song_id, 'playlist_number':self.playlist_position})
                self.groove_id = 0
                
            #check if file exists
            if os.path.isfile(self.song_id):                
                pub.sendMessage('main.song_id', {'song_id':self.song_id, 'playlist_number':self.playlist_position})
                album = local_songs.GetMp3Album(self.song_id)
                if (len(album) >= 1) & (len(self.album) <1):
                    self.album = album
                    pub.sendMessage('main.album', {'album':self.album, 'playlist_number':self.playlist_position})
            # try grooveshark
            else:
                #grab results from tinysong
                self.parent.SetNetworkStatus('grooveshark', 1)
                query_results = tinysong.Tsong().get_search_results(query_string, 32)
                   #*** change this stuff, change it in prefetch.py too
                if len(query_results) >= 1:
                    self.parent.SetNetworkStatus('grooveshark', 0)
                    returned_song_id = query_results[0]['SongID']

                    # let's check for album and update that too
                    if (self.album =='') & (query_results[0]['AlbumName'] != ''):
                        self.album = query_results[0]['AlbumName']
                        pub.sendMessage('main.album', {'album':self.album, 'playlist_number':self.playlist_position})
                    
                    # check for song match
                    if self.song.upper() != query_results[0]['SongName'].upper():
                        #cylce through results to see if we can get and exact match
                        #otherwise use the first result
                        found_it = False
                        for x in range(1, len(query_results) - 1):                            
                            if (query_results[x]['SongName'].upper() == self.song.upper()) & (found_it != True):
                                xx = query_results[x]['SongID']
                                pub.sendMessage('main.song_id', {'song_id':xx, 'playlist_number':self.playlist_position})
                                self.song_id = xx
                                found_it = True
                                break                                
                    
                    # check for artist match
                    if self.artist.upper() != query_results[0]['ArtistName'].upper():
                        # cycle through till will hit the right artist
                        found_it = False
                        for x in range(1, len(query_results) - 1):                            
                            if (query_results[x]['ArtistName'].upper() == self.artist.upper()) & (found_it != True):
                                yy = query_results[x]['SongID']
                                pub.sendMessage('main.song_id', {'song_id':yy, 'playlist_number':self.playlist_position})
                                self.song_id = yy
                                found_it = True
                                break
                        if found_it == False:
                            self.parent.lc_playlist.SetItemBackgroundColour(self.playlist_position, HICOLOR_1)
                            # don't scrobb the wrong song
                            self.scrobbed_song = 1
                            pub.sendMessage('main.song_id', {'song_id':returned_song_id, 'playlist_number':self.playlist_position})
                            self.song_id = returned_song_id
                    #update playlist
                    else:
                        pub.sendMessage('main.song_id', {'song_id':returned_song_id, 'playlist_number':self.playlist_position})
                        self.song_id = returned_song_id
                else:                    
                    #no search results found
                    self.parent.lc_playlist.SetItemBackgroundColour(self.playlist_position, HICOLOR_2)
                    self.status = 'stopped'
                    # ***skip to next track
                    
        #self.song_url = PLAY_SONG_URL + self.song_id 
                    
    def CheckAlbum(self, album):
        if album=='':
            at = FetchAlbumThread(self.artist, self.song, self.playlist_position)
            at.start()
        #else:
            # publish to pubsub
            #pub.sendMessage('main.album', {'album':self.album, 'playlist_number':self.playlist_position})

# --------------------------------------------------------- 
# ######################################################### 
# ---------------------------------------------------------

class FetchAlbumThread(Thread):
    #grab the album name
    #check current track, verify that it still matches, update album name
    #publish to pubsub when album is retrived, so it can grab album art
    def __init__(self, artist, song, playlist_number):
        Thread.__init__(self)        
        self.artist = artist
        self.song = song
        self.playlist_number = playlist_number
        
    def run(self):
        try:
            album_array = musicbrainz.Brainz().get_song_info(self.artist, self.song)
            album = album_array[1]
            pub.sendMessage('main.album', {'album':album, 'playlist_number':self.playlist_number})
        except Exception, expt:
            print "FetchAlbumThread: " + str(Exception) + str(expt)

# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 

class FetchTimeThread(Thread):
    #grab the album name
    #check current track, verify that it still matches, update album name
    #publish to pubsub when album is retrived, so it can grab album art
    def __init__(self, playlist_number, artist, song):
        Thread.__init__(self)
        self.artist = artist
        self.song = song
        self.playlist_number = playlist_number
        
    def run(self):
        try:
            track_time = musicbrainz.Brainz().get_song_time(self.artist, self.song)
            if track_time != 0:
                pub.sendMessage('main.song_time.seconds', {'time_seconds':track_time, 'playlist_number':self.playlist_number})
        except Exception, expt:
            print "FetchTimeThread: " + (Exception) + str(expt)

# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 

class WebFetchThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, panel, artist, song, album, webfetchtype):
        Thread.__init__(self)
        self.panel = panel
        self.artist = artist
        self.song = song
        self.album = album
        self.webfetchtype = webfetchtype
        #self.lsp = local_songs.Player()
        #if webfetchtype == 'PLAYLOCAL':
        #    if panel.use_backend == 'pymedia':
        #        self.lsp = local_songs.Player()
            ##else:
            ##    self.lsp = player_wx.Player(panel)
               
    #def stop(self):
    #    self.lsp.stop_play()
        #self.lsp.stop()
                
    #def pause(self):
    #    self.lsp.toggle_pause()
                 
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
                ext = '.' + file_name.rsplit('.', 1)[1]
                art_alb = self.artist + '-' + self.album
                (local_file_name, is_file) = file_cache.CreateCachedImage(self.panel.image_save_location, art_alb, ext)
                
                self.panel.SaveSongArt(song_art_url, local_file_name)               
                self.panel.SetImage(local_file_name, self.panel.image_save_location)
                self.panel.palbum_art_file = local_file_name
            else:
                self.panel.SetImage('no_cover.png', GRAPHICS_LOCATION)
                self.panel.palbum_art_file =''
                #print 'no-cover'
            
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
            self.panel.SetNetworkStatus('grooveshark', 1)
            query_results = tinysong.Tsong().get_search_results(query_string, 1)
            #print query_results
            if len(query_results) == 1:
                self.panel.SetNetworkStatus('grooveshark', 0)
                #add to playlist
                #self.panel.SetPlaylistItem(0, artist, song, album, url)                
                #split_array = query_results[0].split('; ')
                #"SongID":8815585,"SongName":"Moonlight Sonata","ArtistID":1833,"ArtistName":"Beethoven","AlbumID":258724,"AlbumName":"Beethoven"
                play_url = query_results[0]['SongID']
                # added a delay, seems to fuck up otherwise
                #time.sleep(1.5)
                self.panel.SetPlaylistItem(0, query_results[0]['ArtistName'], query_results[0]['SongName'], query_results[0]['AlbumName'], play_url)
                
        if self.webfetchtype == 'PLAYCOUNT':
            #for grabbing playcounts
            #self.album is a ararray of arrays [song, artist, '']
            counter = 0
            for x in self.album:
                playcount = audioscrobbler_lite.Scrobb().get_play_count(x[1], x[0])
                #print playcount
                self.panel.tab_lastfm.lc_lastfm.SetStringItem(counter, 4, playcount)
                if counter == 0:
                    self.panel.tab_lastfm.lc_lastfm.SetColumnWidth(4, wx.LIST_AUTOSIZE)
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
            grooveshark_id = self.panel.current_song.groove_id
            music_id = self.panel.current_song.music_id
            track_time = self.panel.current_song.song_time_seconds
            #tag_id = ''            
            album_art_file = self.panel.palbum_art_file
            track_id = local_songs.DbFuncs().InsertTrackData(grooveshark_id, music_id, track_time, tag_id, self.artist, self.song, self.album, album_art_file)#p_grooveshark_id, p_music_id, p_track_time, p_tag_id, p_artist, p_song, p_album, p_album_art_file)
            local_songs.DbFuncs().InsertPlaycountData(track_id)#p_track_id)
            if (res[1] != '') & (res[0] !=''):
                local_songs.DbFuncs().InsertPopData(track_id, res[1], res[0])#p_track_id, p_listeners, p_playcount)

# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 

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
        try:
            g_session.startSession()
        except Exception, exp:
            #print str(exp)
            self.parent.current_song.status = 'stopped'
            dlg = wx.MessageDialog(self.parent, "Grooveshark error: " + str(exp), 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()
            return None
        else:
            g_data = {'SongID': self.song_id, 'Name': self.track, 'ArtistName': self.artist, 'AlbumName': self.album, 'AlbumID': '', 'ArtistID': ''}
            g_song = song.songFromData(g_session, g_data)
            g_song.getStreamDetails()
            return (g_song._lastStreamKey, g_song._lastStreamServer)
                        
    def run(self):
        
        ##self.parent.current_song.status ='buffering'
        
        keyandserver = self.GetStreamKeyAndServer()
        self.parent.SetNetworkStatus('grooveshark', 1)
        if keyandserver != None:
            self.parent.SetNetworkStatus('grooveshark', 0)
        
            #progress thread
            #THREAD
            current = ProgressThread(self.parent, self.temp_file, self.GetFileSize())
            #THREAD
            current.start()

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
                    self.parent.tab_song_collection.lc_scol_col.SetItemCount(song_collection.GetCount())
                    # clear id for this song on the playlist
                    # ASSUME that it's the current selection
                    val = self.parent.lc_playlist.GetFirstSelected()
                    self.parent.lc_playlist.SetStringItem(val, 3, '')
        else:        
            self.parent.SetNetworkStatus('grooveshark', 2)
                
# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 
        
def GetLocalGroovesharkVersion(data_dir):
    #gets the grooveshark version from the local grooveshark.xml file
    #check if file exists
    file_name = 'grooveshark.xml'
    g_version = None
    if os.path.isfile(data_dir + file_name):
        #get the version number from the file
        xml_dict = read_write_xml.xml_utils().get_generic_settings(data_dir + file_name)
        if xml_dict.has_key('version'):
            if len(xml_dict['version']) > 1:
                g_version = xml_dict['version']
    return g_version     
            
# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 

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
            
# --------------------------------------------------------- 
# ######################################################### 
# ---------------------------------------------------------

class TreeListCtrlXmlHandler(xrc.XmlResourceHandler):
    def __init__(self):
        xrc.XmlResourceHandler.__init__(self)
        # Standard styles
        self.AddWindowStyles()
        # Custom styles
        #self.AddStyle("wxTR_FULL_ROW_HIGHLIGHT", wx.TR_FULL_ROW_HIGHLIGHT)
        #self.AddStyle('wxLED_ALIGN_LEFT', gizmos.LED_ALIGN_LEFT)
        #self.AddStyle('wxLED_ALIGN_RIGHT', gizmos.LED_ALIGN_RIGHT)
        #self.AddStyle('wxLED_ALIGN_CENTER', gizmos.LED_ALIGN_CENTER)
        #self.AddStyle('wxLED_DRAW_FADED', gizmos.LED_DRAW_FADED)
    def CanHandle(self,node):
        return self.IsOfClass(node, 'TreeListCtrl')
    # Process XML parameters and create the object
    def DoCreateResource(self):
        assert self.GetInstance() is None
        w = gizmos.TreeListCtrl(self.GetParentAsWindow(),
                                 self.GetID(),
                                 self.GetPosition(),
                                 self.GetSize(),
                                 self.GetStyle())
        #w.SetValue(self.GetText('value'))
        self.SetupWindow(w)
        return w

#---------------------------------------------------------------------------
# --------------------------------------------------------- 
# ######################################################### 
# --------------------------------------------------------- 
#---------------------------------------------------------------------------

       
if __name__ == '__main__':
    #stdoutlog = file('c:\\gw.log', 'a+')
    #sys.stdout = stdoutlog
    #sys.stderr = stdoutlog    
    redirect = False    
    for x in range(0, len(sys.argv)):
        if sys.argv[x] == '-r=true':
            redirect = True
    app = GWApp(redirect=redirect)
    app.MainLoop()