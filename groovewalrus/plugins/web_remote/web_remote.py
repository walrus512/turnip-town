"""
GrooveWalrus: Web Remote Plug-in 
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
import urllib
import os
import socket

#from main_utils.read_write_xml import xml_utils
from main_utils import system_files
import http_server

#SYSLOC = os.getcwd()
#WEB_REMOTE_SETTINGS = os.path.join(os.getcwd(), 'plugins','web_remote') + os.sep + "settings_web_remote.xml"
WEB_REMOTE = os.path.join(os.getcwd(), 'plugins','web_remote') + os.sep
RESFILE = os.path.join(os.getcwd(), 'plugins','web_remote') + os.sep + "layout_web_remote.xml"

class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Web Remote", size=(375,200), style=wx.FRAME_SHAPED|wx.RESIZE_BORDER) #STAY_ON_TOP)        
        self.parent = parent

        # settings xml file
        self.WEB_REMOTE_SETTINGS = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep

        # xrc layout xml
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_web_remote")

        # control references --------------------
        self.bu_web_remote_start_server = xrc.XRCCTRL(self, 'm_bu_web_remote_start_server')
        self.bu_web_remote_stop_server = xrc.XRCCTRL(self, 'm_bu_web_remote_stop_server')
        self.tc_web_remote_status = xrc.XRCCTRL(self, 'm_tc_web_remote_status')        
        
        #header for dragging and moving
        self.st_web_remote_header = xrc.XRCCTRL(self, 'm_st_web_remote_header')
        self.bm_web_remote_close = xrc.XRCCTRL(self, 'm_bm_web_remote_close')
        
        # bindings ----------------        
        self.Bind(wx.EVT_BUTTON, self.StartServer, id=xrc.XRCID('m_bu_web_remote_start_server'))
        self.Bind(wx.EVT_BUTTON, self.StopServer, id=xrc.XRCID('m_bu_web_remote_stop_server'))
        self.bm_web_remote_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
                
                
        #dragging and moving
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_web_remote_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_web_remote_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_web_remote_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_web_remote_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        # load settings -----------
        #self.LoadSettings()        
        
        self.StartServer(event=None)
        
                
    def StartServer(self, event):        
        self.server = http_server.HttpControl()
        self.server.StartHttp()
        self.bu_web_remote_start_server.Enable(False)
        self.bu_web_remote_stop_server.Enable(True)        
        self.tc_web_remote_status.SetValue('http://' + socket.gethostbyname(socket.gethostname()) + ':8723/')
    
    def StopServer(self, event):
        self.server.StopHttp()
        self.bu_web_remote_stop_server.Enable(False)
        self.bu_web_remote_start_server.Enable(True)
        #self.tc_web_remote_status.SetValue('http://localhost:8723/')
            
    def CloseMe(self, event=None):
        #self.SaveOptions()
        #self.parent.KillReceiver(self.GenericReceiverAction)
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
            try:            
                dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
                #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
                nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
                self.Move(nPos)
            except AttributeError:
                pass

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        #self.hide_me()
        #self..Destroy()
        pass
            
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
    #s = urllib.quote(s)#, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
