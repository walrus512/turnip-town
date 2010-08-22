"""
GrooveWalrus: Ratings Button
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
import os
import sys

from main_utils import local_songs
from main_thirdp import pylast
API_KEY = "13eceb51a4c2e0f825c492f04bf693c8"
#from main_utils import system_files
#import sqlite3

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())
GRAPHICS_LOCATION = os.path.join(SYSLOC, 'graphics') + os.sep

IMAGE_FILES = [
    #(GRAPHICS_LOCATION + 'weather-clear-night.png', 0, 'Clear'), 
    (GRAPHICS_LOCATION + 'weather-clear.png', 4, 'Great'),
    (GRAPHICS_LOCATION + 'weather-few-clouds.png', 3, 'Good'),
    (GRAPHICS_LOCATION + 'weather-overcast.png', 2, 'Average'), 
    (GRAPHICS_LOCATION + 'weather-storm.png', 1, 'Poor')
    ]


class RatingsButton(wx.BitmapButton):
    _firstEventType = wx.EVT_SIZE
    
    def __init__(self):
        p = wx.PreBitmapButton()
        self.PostCreate(p)
        self.Bind(self._firstEventType, self.OnCreate)            
    
    def _PostInit(self):
        #self.font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        #self.font_bold = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_BUTTON, self.OnClick)
        self.parent = self.GetGrandParent()
        self.sk = None

    def OnCreate(self, evt):
        self.Unbind(self._firstEventType)
        # Called at window creation time
        self._PostInit()
        #self.Refresh()


    def OnClick(self, event):
        #make a menu for rating the current song and other options
          
        # make a menu
        #ID_RATE4 = 4
        #ID_RATE3 = 3
        #ID_RATE2 = 2
        #ID_RATE1 = 1 
        
        menu = wx.Menu()
        re = RateEvents(self.parent)
        MenuAppend(menu, self, re.SongRate)

        #menu.AppendSeparator()
        #item1 = wx.MenuItem(menu, ID_RATE4, "Great")
        #check_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'weather-clear.png', wx.BITMAP_TYPE_ANY)
        #item1.SetBitmap(check_bmp)
        #menu.AppendItem(item1)
        
        #item1 = wx.MenuItem(menu, ID_RATE3, "Good")
        #check_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'weather-few-clouds.png', wx.BITMAP_TYPE_ANY)
        #item1.SetBitmap(check_bmp)
        #menu.AppendItem(item1)
        
        #item1 = wx.MenuItem(menu, ID_RATE2, "Average")
        #check_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'weather-overcast.png', wx.BITMAP_TYPE_ANY)
        #item1.SetBitmap(check_bmp)
        #menu.AppendItem(item1)
        
        #item1 = wx.MenuItem(menu, ID_RATE1, "Poor")
        #check_bmp = wx.Bitmap(GRAPHICS_LOCATION + 'weather-storm.png', wx.BITMAP_TYPE_ANY)
        #item1.SetBitmap(check_bmp)
        #menu.AppendItem(item1)
        
        #wx.EVT_MENU(self, ID_RATE4, self.Rate4)
        #wx.EVT_MENU(self, ID_RATE3, self.Rate3)
        #wx.EVT_MENU(self, ID_RATE2, self.Rate2)
        #wx.EVT_MENU(self, ID_RATE1, self.Rate1)

        self.PopupMenu(menu)
        menu.Destroy()
        
class RateEvents(object):
    def __init__(self, parent):
        self.parent = parent        
        
    def SongRate(self, event):        
        event_id = event.GetId()
        #print event_id
        music_id = self.parent.current_song.track_id
        grooveshark_id = self.parent.current_song.groove_id
        artist = self.parent.current_song.artist
        song = self.parent.current_song.song
        track_id = GetTrackId(artist, song, grooveshark_id, music_id)
        AddRating(self.parent, track_id, event_id)
        if event_id == 4:
            sk = self.parent.GenerateSessionKey2()
            LoveTrack(artist, song, sk)

               
def LoveTrack(artist, song, sk):
    #love track on last.fm too    
    if (len(artist) > 0) & (len(song) > 0) & (sk != None):
        last_track = pylast.Track(artist, song, API_KEY, '6a2eb503cff117001fac5d1b8e230211', sk)
        last_track.love()        
        
def GetTrackId(artist, song, grooveshark_id, music_id):
    track_id = -1
    #track_id = local_songs.DbFuncs().InsertTrackData(grooveshark_id, music_id, track_time, tag_id, self.artist, self.song, self.album, album_art_file)
    if (artist != '') & (song != ''):
        track_id = local_songs.DbFuncs().GetTrackId(grooveshark_id, music_id, artist, song)
    return track_id
    
def AddRating(parent, track_id, rating_type_id):
    #rating_id #track_id #rating_type_id
    # 0:no rating, 1:bad, 2:average, 3:good, 4:great
    if track_id > 0:
        local_songs.DbFuncs().InsertRatingData(track_id, rating_type_id)
    #self.UpdateRowCount()
        parent.favorites.ReadFaves()
        
def MenuAppend(menu, parent, method_loc):
    for x in IMAGE_FILES:
        item1 = wx.MenuItem(menu, x[1], x[2])
        check_bmp = wx.Bitmap(x[0], wx.BITMAP_TYPE_ANY)
        item1.SetBitmap(check_bmp)
        menu.AppendItem(item1)
        wx.EVT_MENU(parent, x[1], method_loc)

    
