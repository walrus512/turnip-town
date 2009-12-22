"""
GrooveWalrus: Played Dizzler
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
from main_utils.read_write_xml import xml_utils
import sys, os
from wx.lib.flashwin import FlashWindow

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
DIZZLER_URL = 'http://www.dizzler.com/player/podmini.swf?m='
DIZZLER_SETTINGS = os.path.join(os.getcwd(), 'plugins','dizzler') + os.sep + "settings_dizzler.xml"
DIZZLER = os.path.join(os.getcwd(), 'plugins','dizzler') + os.sep
RESFILE = os.path.join(os.getcwd(), 'plugins','dizzler') + os.sep + "layout_dizzler.xml"
#http://www.dizzler.com/player/podmini.swf?m=chairlift-bruises

class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Dizzler", size=(475,310), style=wx.FRAME_SHAPED) #STAY_ON_TOP)        
        self.parent = parent
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_dizzler")

        # control references --------------------
        self.pa_dizzler_player = xrc.XRCCTRL(self, 'm_pa_dizzler_player')
        #header for dragging and moving
        self.st_dizzler_header = xrc.XRCCTRL(self, 'm_st_dizzler_header')
        self.st_dizzler_using = xrc.XRCCTRL(self, 'm_st_dizzler_using')
        self.bm_dizzler_close = xrc.XRCCTRL(self, 'm_bm_dizzler_close')

        # bindings ----------------
        self.Bind(wx.EVT_BUTTON, self.SetDizzler, id=xrc.XRCID('m_bu_dizzler_use_dizzler'))
        self.Bind(wx.EVT_BUTTON, self.SetGrooveShark, id=xrc.XRCID('m_bu_dizzler_use_grooveshark'))
        #self.Bind(wx.EVT_TEXT, self.OnChars, self.tc_dizzler_text)
        self.bm_dizzler_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_dizzler_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_dizzler_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_dizzler_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_dizzler_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
            
        self.st_dizzler_using.SetLabel('Using: ' + self.parent.web_music_type)
        
        #self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        #self.LoadSetings()
        
        #flash windows
        self.dizzler_flash = FlashWindow(self.pa_dizzler_player, style=wx.NO_BORDER, size=wx.Size(500,140))#, size=(400, 120))        
        #self.flash.Show(True)
        
        flash_sizer = wx.BoxSizer(wx.VERTICAL)
        flash_sizer.Add(self.dizzler_flash, 1, wx.EXPAND|wx.ALL, 5)
        self.pa_dizzler_player.SetSizer(flash_sizer)
        
        ##self.parent.flash = self.dizzler_flash
        ##self.parent.web_music_url = DIZZLER_URL
        ##self.parent.web_music_type = "Dizzler"
        ##self.MakeModal(False)

    def CloseMe(self, event=None):
        self.Destroy()
               
    def LoadFlashSong(self, artist, song):
        #start playback
        self.dizzler_flash.movie = DIZZLER_URL + artist + "-" + song

    def StopFlashSong(self):
        #stop playback
        self.dizzler_flash.movie = 'temp.swf' 
        
    def SetDizzler(self, event):
        #stop playback
        self.parent.web_music_url = DIZZLER_URL
        self.parent.web_music_type = "Dizzler"
        self.st_dizzler_using.SetLabel('Using Dizzler')
        
    def SetGrooveShark(self, event):
        #stop playback
        #self.parent.web_music_url = DIZZLER_URL
        self.parent.web_music_type = "GrooveShark"
        self.st_dizzler_using.SetLabel('Using GrooveShark')
        
    def LoadSetings(self):
        #load the setting from settings_dizzler.xml if it exists
        settings_dict = xml_utils().get_generic_settings(SYSLOC + DIZZLER_SETTINGS)
        #print settings_dict
        if len(settings_dict) > 1:
            username=''
            if settings_dict.has_key('username'):
                username = settings_dict['username']
            password =''
            if settings_dict.has_key('password'):
                password = settings_dict['password']
            default_text=''
            if settings_dict.has_key('default_text'):
                default_text = settings_dict['default_text']

            self.tc_dizzler_username.SetValue(username)
            self.tc_dizzler_password.SetValue(password)   
            self.tc_dizzler_default.SetValue(default_text)

    def SaveOptions(self, event):
        # save value to options.xml
        window_dict = {}        
        window_dict['password'] = self.tc_dizzler_password.GetValue()
        window_dict['username'] = self.tc_dizzler_username.GetValue()
        window_dict['default_text'] = self.tc_dizzler_default.GetValue()
        
        xml_utils().save_generic_settings(SYSLOC  + DIZZLER, "settings_dizzler.xml", window_dict)

            
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
