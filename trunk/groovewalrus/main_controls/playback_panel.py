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
        self.SetSize()
        self.SetColours()
                
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnCreate(self, evt):
        self.Unbind(self._firstEventType)
        # Called at window creation time
        self._PostInit()
        self.Refresh()
        
    def SetSmallPanel(self):
        #make a smaller version
        self.font = wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.font_bold = wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

    def SetColours(self, background='#f5f5f5', text='#000000', progress='#B0E2FF', download='#0080FF'):
        '''Sets the background, text, progress, and download colors, #B0E2FF'''
        self.SetBackgroundColour(background)
        self.progress_colour = progress
        self.download_colour = download
        self.text_colour = text
        
    def SetSize(self, size_type=0):
        '''Sets the size, 0 regular, 1 smaller'''
        if size_type == 0:
            self.font_size = 9
            self.font = wx.Font(self.font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            self.font_bold = wx.Font(self.font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            self.progress_height = 25
            self.download_height = 5
        else:
            self.font_size = 7
            self.font = wx.Font(self.font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            self.font_bold = wx.Font(self.font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            self.progress_height = 21
            self.download_height = 3
            
    def OnPaint(self, event):
        w, h = self.GetSize()
        #let's use double buffering to avoid flickering        
        dbuffer = wx.EmptyBitmap(w, h)
        dc = wx.BufferedPaintDC(self, dbuffer)        
        #dc = wx.PaintDC(self)
        dc.Clear()
        
        dc.SetFont(self.font)
        par = self.GetGrandParent()
        try:
            artist = par.current_song.artist
        except AttributeError, error:
            #print error
            par = par.GetParent()
            artist = par.current_song.artist
            
        track = par.current_song.song
        status = par.current_song.status
        track_time = par.ConvertTimeFormated(par.current_song.song_time_seconds)
        play_time = par.ConvertTimeFormated(par.time_count)
        download_percent = par.download_percent
        
        play_to = 0
        if (par.current_song.song_time_seconds > 0) & (par.time_count > 0):
            play_to = w * (float(par.time_count) / float(par.current_song.song_time_seconds))
        down_to = w * float(download_percent * 0.01)
        
        if (status == 'stopped') or (status == 'loading'):
            play_to = 0
            play_time = ''

        dc.SetPen(wx.Pen(self.progress_colour))
        dc.SetBrush(wx.Brush(self.progress_colour))
        dc.DrawRectangle(0, 0, play_to, self.progress_height)
        if download_percent > 0:
            dc.SetPen(wx.Pen(self.download_colour))
            dc.SetBrush(wx.Brush(self.download_colour))
            dc.DrawRectangle(0, self.progress_height, down_to, self.download_height)
        else:
            dc.DrawRectangle(0, self.progress_height, play_to, self.download_height)

        dc.SetTextForeground(self.text_colour)
        #font size is used to figure out approx spacing
        dc.DrawText(status, self.font_size, 3)
        dc.DrawText(track_time, self.font_size * 8, 3)
        dc.DrawText(play_time, self.font_size * 13, 3)
        dc.SetFont(self.font_bold)
        if len(artist) > 0:
            dc.DrawText(artist + ' - ' + track, self.font_size * 18, 3)

    def OnSize(self, event):
        self.Refresh()
        
    def OnEraseBackground(self, event):
        pass # Or None, for DBuffer       
