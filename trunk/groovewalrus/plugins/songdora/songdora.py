"""
GrooveWalrus: Pandora
Copyright (C) 2010
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
import wx.xrc as xrc
#from main_utils.read_write_xml import xml_utils
from main_utils import system_files
import sys, os
from beautifulsoup import BeautifulSoup
import urllib2


#SYSLOC = os.getcwd()
RESFILE = os.path.join(os.getcwd(), 'plugins','songdora') + os.sep + "layout_songdora.xml"
MAIN_PLAYLIST = system_files.GetDirectories(None).DataDirectory() + os.sep + "playlist.xspf"
#FILEDB = system_files.GetDirectories(None).DataDirectory() + os.sep + 'gravydb.sq3'

class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "songdora", size=(475,450), style=wx.FRAME_SHAPED) #STAY_ON_TOP)        
        self.parent = parent        
               
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_songdora")

        # control references --------------------        
        #header for dragging and moving
        self.st_songdora_header = xrc.XRCCTRL(self, 'm_st_songdora_header')
        self.lc_songdora_list = xrc.XRCCTRL(self, 'm_lc_songdora_list')
        self.bm_songdora_close = xrc.XRCCTRL(self, 'm_bm_songdora_close')
        #self.rx_songdora_radio = xrc.XRCCTRL(self, 'm_rx_songdora_radio')
        
        self.lc_songdora_list.InsertColumn(0,"Artist")
        self.lc_songdora_list.InsertColumn(1,"Song")
        self.lc_songdora_list.InsertColumn(2,"Album")
        self.lc_songdora_list.SetColumnWidth(0, 180)
        self.lc_songdora_list.SetColumnWidth(1, 260)
        self.lc_songdora_list.SetColumnWidth(2, 60)

        # bindings ----------------
        self.bm_songdora_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_songdora_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_songdora_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_songdora_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_songdora_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDoubleClick, self.lc_songdora_list)
        #self.Bind(wx.EVT_RADIOBOX, self.OnRadioClick, self.rx_songdora_radio)
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick, self.lc_songdora_list)
        
        # set layout --------------        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        #self.LoadSetings()
        self.GetLastPlayed()

    def CloseMe(self, event=None):
        self.Destroy()
        
    def Get6Songs(self, search):
        
        page = urllib2.urlopen("http://www.pandora.com/music/song/eaa9c7fe3b3b0fd3")

        soup = BeautifulSoup(page)
        for songs in soup('span', id="similar_song"): #span id="similar_song"
            track = songs.contents[1]
           
            a = songs.contents[6]           
            soupa = BeautifulSoup(str(a))
            artist = soupa.a.string
            
            b = songs.contents[11]           
            soupb = BeautifulSoup(str(b))
            album = soupb.a.string
            
            print str(track).split('"')[3]
            print artist
            print album
        
        
    def OnDoubleClick(self, event):
        # pass the artist + track to the playlist
        val = self.lc_songdora_list.GetFirstSelected()
        artist = self.lc_songdora_list.GetItem(val, 0).GetText()
        song = self.lc_songdora_list.GetItem(val, 1).GetText()
        #search for selected song
        self.parent.SearchOrPlaylist(artist, song)
        
    def OnRightClick(self, event):
        val = self.lc_songdora_list.GetFirstSelected()
        if val != -1:
            if (self.lc_songdora_list.GetItem(val, 0).GetText() != '') & (self.lc_songdora_list.GetItem(val, 1).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 1
                ID_CLEAR = 2
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")
                menu.AppendSeparator()
                menu.Append(ID_CLEAR, "Clear Playlist")
                wx.EVT_MENU(self, ID_PLAYLIST, self.AddToPlaylist)
                wx.EVT_MENU(self, ID_CLEAR, self.parent.OnClearPlaylistClick)       
                self.PopupMenu(menu)
                menu.Destroy()
           
    def AddToPlaylist(self, event):
        val = self.lc_songdora_list.GetFirstSelected()
        total = self.lc_songdora_list.GetSelectedItemCount()
        current_count = self.parent.lc_playlist.GetItemCount()
        #print val
        if (val >= 0):            
            artist =    self.lc_songdora_list.GetItem(val, 0).GetText()
            song =      self.lc_songdora_list.GetItem(val, 1).GetText()
            self.parent.SetPlaylistItem(current_count, artist, song, '', '')
            current_select = val
            if total > 1:
                for x in range(1, self.lc_songdora_list.GetSelectedItemCount()):
                    current_select =    self.lc_songdora_list.GetNextSelected(current_select)
                    artist =            self.lc_songdora_list.GetItem(current_select, 0).GetText()
                    song =              self.lc_songdora_list.GetItem(current_select, 1).GetText()                    
                    self.parent.SetPlaylistItem(current_count + x, artist, song, '', '')

        #save the playlist
        self.parent.SavePlaylist(MAIN_PLAYLIST)
        # switch tabs
        #self.nb_main.SetSelection(NB_PLAYLIST)
                
                           
# --------------------------------------------------------- 
# titlebar-like move and drag
    
    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        self.hide_me()
        #self.Destroy()