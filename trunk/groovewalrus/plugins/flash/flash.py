"""
GrooveWalrus: Flash Player
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

#import urllib
#import urllib2

import wx
import wx.xrc as xrc
from main_utils.read_write_xml import xml_utils
from main_utils import system_files
import os #,sys
from wx.lib.flashwin import FlashWindow

#SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
DIZZLER_URL = 'http://www.dizzler.com/player/podmini.swf?m='
DIZZLER_SETTINGS = os.path.join(os.getcwd(), 'plugins','flash') + os.sep + "settings_flash.xml"
DIZZLER = os.path.join(os.getcwd(), 'plugins','flash') + os.sep
RESFILE = os.path.join(os.getcwd(), 'plugins','flash') + os.sep + "layout_flash.xml"
#http://www.dizzler.com/player/podmini.swf?m=chairlift-bruises

class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Flash", size=(475,310), style=wx.FRAME_SHAPED) #STAY_ON_TOP)        
        self.parent = parent
        
        self.FLASH_SETTINGS = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_dizzler")

        # control references --------------------
        self.pa_dizzler_player = xrc.XRCCTRL(self, 'm_pa_dizzler_player')
        #header for dragging and moving
        self.st_dizzler_header = xrc.XRCCTRL(self, 'm_st_dizzler_header')
        #self.st_dizzler_using = xrc.XRCCTRL(self, 'm_st_dizzler_using')
        self.bm_dizzler_close = xrc.XRCCTRL(self, 'm_bm_dizzler_close')
        self.bm_dizzler_tab = xrc.XRCCTRL(self, 'm_bm_dizzler_tab')
        self.cb_flash_autoload = xrc.XRCCTRL(self, 'm_cb_flash_autoload')
        self.rx_flash_service = xrc.XRCCTRL(self, 'm_rx_flash_service')

        # bindings ----------------
        #self.Bind(wx.EVT_BUTTON, self.SetDizzler, id=xrc.XRCID('m_bu_dizzler_use_dizzler'))
        #self.Bind(wx.EVT_BUTTON, self.SetGrooveShark, id=xrc.XRCID('m_bu_dizzler_use_grooveshark'))
        #self.Bind(wx.EVT_TEXT, self.OnChars, self.tc_dizzler_text)
        self.bm_dizzler_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        self.bm_dizzler_tab.Bind(wx.EVT_LEFT_UP, self.OnMakeTabClick)
        self.Bind(wx.EVT_CHECKBOX, self.SaveOptions, self.cb_flash_autoload)
        self.Bind(wx.EVT_RADIOBOX, self.SetService, self.rx_flash_service)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_dizzler_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_dizzler_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_dizzler_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_dizzler_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
            
        #self.st_dizzler_using.SetLabel('Using: ' + self.parent.web_music_type)
        
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
        
        self.parent.use_web_music = True
        self.parent.flash = self.dizzler_flash
        ##self.parent.web_music_url = DIZZLER_URL
        ##self.parent.web_music_type = "Dizzler"
        ##self.MakeModal(False)
        
        self.LoadSettings()
        self.SetService(None)

    def CloseMe(self, event=None):
        self.parent.use_web_music = False
        self.parent.OnStopClick(None)
        self.Destroy()
        
    def OnMakeTabClick(self, event=None):
        # transfer plug-in to tab in main player
        # make a new page                
        page1 = PageOne(self.parent.nb_main)
        # add the pages to the notebook
        self.parent.nb_main.AddPage(page1, "Flash")
        
        #flash windows
        dizzler_flash = FlashWindow(page1, style=wx.NO_BORDER, size=wx.Size(500,140))#, size=(400, 120))        
        #self.flash.Show(True)        
        flash_sizer = wx.BoxSizer(wx.VERTICAL)
        flash_sizer.Add(dizzler_flash, 1, wx.EXPAND|wx.ALL, 5)
        page1.SetSizer(flash_sizer)        
        self.parent.use_web_music = True
        self.parent.flash = dizzler_flash
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
        
    def SetService(self, event):
        service = self.rx_flash_service.GetSelection()
        if service == 0:
            self.parent.web_music_url =''
            self.parent.web_music_type = "GrooveShark"
        else:
           self.parent.web_music_url = DIZZLER_URL
           self.parent.web_music_type = "Dizzler"
        self.SaveOptions(None)
        
    def LoadSettings(self):
        #load the setting from settings_falsh.xml if it exists
        settings_dict = xml_utils().get_generic_settings(self.FLASH_SETTINGS + "settings_flash.xml")
        #print settings_dict
        if len(settings_dict) >= 1:
            autoload=0
            if settings_dict.has_key('autoload'):
                autoload = int(settings_dict['autoload'])
            self.cb_flash_autoload.SetValue(autoload)
            service=0
            if settings_dict.has_key('service'):
                service = int(settings_dict['service']) 
            self.rx_flash_service.SetSelection(service)            

    def SaveOptions(self, event):
        # save value to options.xml
        window_dict = {}        
        window_dict['autoload'] = str(int(self.cb_flash_autoload.GetValue()))
        window_dict['service'] = str(int(self.rx_flash_service.GetSelection()))
        xml_utils().save_generic_settings(self.FLASH_SETTINGS, "settings_flash.xml", window_dict)

            
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
