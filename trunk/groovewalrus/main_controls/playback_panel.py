"""
GrooveWalrus: Playback Panel
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


class PlaybackPanel(wx.Panel):
    _firstEventType = wx.EVT_SIZE
    
    def __init__(self):
        p = wx.PrePanel()
        self.PostCreate(p)
        self.Bind(self._firstEventType, self.OnCreate)     
    
    
    def _PostInit(self):
        self.font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.font_bold = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)        

    def OnCreate(self, evt):
        self.Unbind(self._firstEventType)
        # Called at window creation time
        self._PostInit()
        self.Refresh()

    def OnPaint(self, event):
        w, h = self.GetSize()
        #let's use double buffering to avoid flickering        
        dbuffer = wx.EmptyBitmap(w, h)
        dc = wx.BufferedPaintDC(self, dbuffer)        
        #dc = wx.PaintDC(self)
        dc.Clear()
        
        dc.SetFont(self.font)
        artist = self.GetGrandParent().partist
        track = self.GetGrandParent().ptrack
        status = self.GetGrandParent().pstatus
        track_time = self.GetGrandParent().ConvertTimeFormated(self.GetGrandParent().current_play_time)
        play_time = self.GetGrandParent().ConvertTimeFormated(self.GetGrandParent().time_count)
        download_percent = self.GetGrandParent().download_percent
        
        play_to = 0
        if (self.GetGrandParent().current_play_time > 0) & (self.GetGrandParent().time_count > 0):
            play_to = w * (float(self.GetGrandParent().time_count) / float(self.GetGrandParent().current_play_time))
        down_to = w * float(download_percent * 0.01)
        
        if status != 'playing':
            play_to = 0
            play_time = ''

        dc.SetPen(wx.Pen('#B0E2FF'))
        dc.SetBrush(wx.Brush('#B0E2FF'))
        dc.DrawRectangle(0, 0, play_to, 25)
        if download_percent > 0:
            dc.SetPen(wx.Pen('#0080FF'))
            dc.SetBrush(wx.Brush('#0080FF'))
            dc.DrawRectangle(0, 25, down_to, 5)
        else:
            dc.DrawRectangle(0, 25, play_to, 5)

        dc.DrawText(status, 10, 3)
        dc.DrawText(track_time, 70, 3)
        dc.DrawText(play_time, 115, 3)
        dc.SetFont(self.font_bold)
        if len(artist) > 0:
            dc.DrawText(artist + ' - ' + track, 165, 3)

    def OnSize(self, event):
        self.Refresh()
        
    def OnEraseBackground(self, event):
        pass # Or None, for DBuffer       
