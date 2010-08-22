#!/bin/env python
"""
GrooveWalrus: Song Details Window 
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
import wx.xrc as xrc
import sys, os
SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())

DETAILS_RESFILE = SYSLOC + '\\layout_details.xml'
#columns
C_RATING = 0
C_ARTIST = 1
C_SONG = 2
C_ALBUM = 3
C_ID = 4
C_TIME = 5

class DetailsWindow(wx.Dialog):
    """Details Window for editing song info"""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Details", size=(400, 260), style=wx.FRAME_SHAPED) #STAY_ON_TOP)#wx.FRAME_SHAPED)
        self.parent = parent
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(DETAILS_RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_details")

        # control references --------------------
        self.tc_details_artist = xrc.XRCCTRL(self, 'm_tc_details_artist')
        self.tc_details_song = xrc.XRCCTRL(self, 'm_tc_details_song')
        self.tc_details_album = xrc.XRCCTRL(self, 'm_tc_details_album')
        self.tc_details_id = xrc.XRCCTRL(self, 'm_tc_details_id')
        self.tc_details_time = xrc.XRCCTRL(self, 'm_tc_details_time')
        self.st_details_header = xrc.XRCCTRL(self, 'm_st_details_header')
    
        
        # bindings ----------------
        #self.Bind(wx.EVT_BUTTON, self.OnSearchClick, id=xrc.XRCID('m_bb_search_button'))
        #self.Bind(wx.EVT_BUTTON, self.OnSearchListClick, id=xrc.XRCID('m_bb_search_add'))
        #self.Bind(wx.EVT_BUTTON, self.OnSearchClear, id=xrc.XRCID('m_bb_search_clear'))
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_details_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_details_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_details_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        #self.st_details_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        
        self.val = self.parent.lc_playlist.GetFirstSelected()
        self.tc_details_artist.SetValue(self.parent.lc_playlist.GetItem(self.val, C_ARTIST).GetText())
        self.tc_details_song.SetValue(self.parent.lc_playlist.GetItem(self.val, C_SONG).GetText())
        self.tc_details_album.SetValue(self.parent.lc_playlist.GetItem(self.val, C_ALBUM).GetText())
        self.tc_details_id.SetValue(self.parent.lc_playlist.GetItem(self.val, C_ID).GetText())
        self.tc_details_time.SetValue(self.parent.lc_playlist.GetItem(self.val, C_TIME).GetText())
                
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
#----------------------------------------------------------------------
                
    def show_me(self):
        # show the window
        if self.ShowModal() == wx.ID_OK:            
            artist = self.tc_details_artist.GetValue()
            song = self.tc_details_song.GetValue()
            album = self.tc_details_album.GetValue()
            url = self.tc_details_id.GetValue()
            duration = self.tc_details_time.GetValue()
            self.parent.UpdatePlaylistItem(self.val, artist, song, album, url, duration)
        self.Destroy()

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
            #try:
            #    self.popup.IsShown()
            #except AttributeError:
            #    pass
            #else:
            #    if (self.popup.IsShown()):
            #        pPos = (self.wPos.x + (dPos.x - self.ldPos.x),34)
             #       self.popup.Move(pPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):        
        self.Destroy()
        
# --------------------------------------------------------- 
