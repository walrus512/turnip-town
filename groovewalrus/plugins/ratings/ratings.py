"""
GrooveWalrus: Ratings
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

import urllib
import urllib2

import wx
import wx.xrc as xrc
import sys, os
from main_utils import local_songs

RESFILE = os.path.join(os.getcwd(), 'plugins','ratings') + os.sep + "layout_ratings.xml"


class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Ratings", size=(475,100), style=wx.FRAME_SHAPED) #STAY_ON_TOP)        
        self.parent = parent
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_ratings")

        # control references --------------------
        #header for dragging and moving
        self.st_ratings_header = xrc.XRCCTRL(self, 'm_st_ratings_header')
        self.st_ratings_song = xrc.XRCCTRL(self, 'm_st_ratings_song')
        self.bm_ratings_close = xrc.XRCCTRL(self, 'm_bm_ratings_close')
        self.bm_ratings_tab = xrc.XRCCTRL(self, 'm_bm_ratings_tab')

        # bindings ----------------
        self.Bind(wx.EVT_BUTTON, self.Rate0, id=xrc.XRCID('m_bb_ratings0'))
        self.Bind(wx.EVT_BUTTON, self.Rate1, id=xrc.XRCID('m_bb_ratings1'))
        self.Bind(wx.EVT_BUTTON, self.Rate2, id=xrc.XRCID('m_bb_ratings2'))
        self.Bind(wx.EVT_BUTTON, self.Rate3, id=xrc.XRCID('m_bb_ratings3'))
        self.Bind(wx.EVT_BUTTON, self.Rate4, id=xrc.XRCID('m_bb_ratings4'))
        #self.Bind(wx.EVT_BUTTON, self.SetGrooveShark, id=xrc.XRCID('m_bu_ratings_use_grooveshark'))
        #self.Bind(wx.EVT_TEXT, self.OnChars, self.tc_ratings_text)
        self.bm_ratings_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        self.bm_ratings_tab.Bind(wx.EVT_LEFT_UP, self.OnMakeTabClick)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_ratings_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_ratings_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_ratings_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_ratings_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
            
        #self.st_ratings_using.SetLabel('Using: ' + self.parent.web_music_type)
        
        #self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        #self.LoadSetings()
        
        
    def CloseMe(self, event=None):
        self.Destroy()
        
    def OnMakeTabClick(self, event=None):
        # transfer plug-in to tab in main player
        # make a new page                
        page1 = PageOne(self.parent.nb_main)
        # add the pages to the notebook
        self.parent.nb_main.AddPage(page1, "Ratings")
        
        #flash windows
        #dizzler_flash = FlashWindow(page1, style=wx.NO_BORDER, size=wx.Size(500,140))#, size=(400, 120))        
        #self.flash.Show(True)        
        #flash_sizer = wx.BoxSizer(wx.VERTICAL)
        #flash_sizer.Add(dizzler_flash, 1, wx.EXPAND|wx.ALL, 5)
        #page1.SetSizer(flash_sizer)        
        #self.parent.use_web_music = True
        #self.parent.flash = dizzler_flash
        #self.Destroy()
        
    def Rate0(self, event):
        track_id = self.GetTrackId()
        self.AddRating(track_id, 0)
        
    def Rate1(self, event):
        track_id = self.GetTrackId()
        self.AddRating(track_id, 1)
        
    def Rate2(self, event):
        track_id = self.GetTrackId()
        self.AddRating(track_id, 2)
        
    def Rate3(self, event):
        track_id = self.GetTrackId()
        self.AddRating(track_id, 3)
        
    def Rate4(self, event):
        track_id = self.GetTrackId()
        self.AddRating(track_id, 4) 
        
    def DisplayTrackInfo(self, event=None):        
        self.st_ratings_song.SetLabel(self.parent.partist + ' - ' + self.parent.ptrack)
        
    def GetTrackId(self):
        music_id = self.parent.pmusic_id
        grooveshark_id = self.parent.pgroove_id
        artist = self.parent.partist
        song = self.parent.ptrack
        #track_id = local_songs.DbFuncs().InsertTrackData(grooveshark_id, music_id, track_time, tag_id, self.artist, self.song, self.album, album_art_file)
        track_id = local_songs.DbFuncs().InsertTrackData(grooveshark_id, music_id, 0, 0, artist, song, '', '')
        return track_id
        
    def AddRating(self, track_id, rating_type_id):
        #rating_id #track_id #rating_type_id
        # 0:no rating, 1:bad, 2:average, 3:good, 4:great
        self.DisplayTrackInfo()
        local_songs.DbFuncs().InsertRatingData(track_id, rating_type_id)
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
        #self..Destroy()
          
      
class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)        
              
# ===================================================================            

              
charset = 'utf-8'
        
def url_quote(s, safe='/', want_unicode=False):
    """
    Wrapper around urllib.quote doing the encoding/decoding as usually wanted:
    
    @param s: the string to quote (can be str or unicode, if it is unicode,
              config.charset is used to encode it before calling urllib)
    @param safe: just passed through to urllib
    @param want_unicode: for the less usual case that you want to get back
                         unicode and not str, set this to True
                         Default is False.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    #s = urllib.quote(s, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
     
# ===================================================================   
