"""
GrooveWalrus: Messenger PLus Plug-in 
Copyright (C) 2011
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
import os
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub

#from main_utils import system_files


RESFILE = os.path.join(os.getcwd(), 'plugins','messenger_plus') + os.sep + "layout_messenger_plus.xml"

class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Messenger Plus", size=(375, 160), style=wx.FRAME_SHAPED|wx.RESIZE_BORDER) #STAY_ON_TOP)        
        self.parent = parent        
        #self.FILEDB = system_files.GetDirectories(self).DatabaseLocation()

        # xrc layout xml
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_messenger_plus")

        # control references --------------------
        #self.bu_messenger_plus_clear = xrc.XRCCTRL(self, 'm_bu_messenger_plus_clear')
        self.rb_messenger_plus_enabled = xrc.XRCCTRL(self, 'm_rb_messenger_plus_enabled')
        self.rb_messenger_plus_disabled = xrc.XRCCTRL(self, 'm_rb_messenger_plus_disabled')
                
        #header for dragging and moving
        self.st_messenger_plus_header = xrc.XRCCTRL(self, 'm_st_messenger_plus_header')
        self.bm_messenger_plus_close = xrc.XRCCTRL(self, 'm_bm_messenger_plus_close')
        
        # bindings ----------------        
        self.bm_messenger_plus_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        self.rb_messenger_plus_enabled.Bind(wx.EVT_RADIOBUTTON, self.OnEnable)
        self.rb_messenger_plus_disabled.Bind(wx.EVT_RADIOBUTTON, self.OnDisable)
        
        # self.tc_acc_modifier.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_BUTTON, self.OnClearClick, id=xrc.XRCID('m_bu_messenger_plus_clear'))
                
        #dragging and moving
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_messenger_plus_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_messenger_plus_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_messenger_plus_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_messenger_plus_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetSize(self.GetEffectiveMinSize())
        
        #set a reciever to catch new song events
        self.parent.SetReceiver(self, 'main.playback.new')
        
        # load settings -----------
        #self.LoadSettings()
        self.sp = wx.StandardPaths.Get()
        dd = os.path.join(self.sp.GetDocumentsDir(), u'Grooveshark')        
        
        if os.path.isdir(dd) == False:
            try:
                os.mkdir(dd)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (dd), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
                    self.CloseMe()
        
        self.df = os.path.join(dd, u'currentSong.txt')
        
    def GenericReceiverAction(self, artist, song):
        """Sets the pubsub receiver action."""
        s = unbork(song + '\t\t' + artist +'\tplaying')
        try:
            self.WriteFile(s)
        except Exception, e:
            print 'messenger_plus: ' + str(Exception) + str(e)
            self.WriteFile('')

    def LoadSettings(self):
        """Loads the goddamn stuff from the db."""
        pass
        
    def OnClearClick(self, event):
        # clear MyDocuments + "\\Grooveshark\\currentSong.txt
        self.WriteFile('')
        
    def OnDisable(self, event):
        self.parent.KillReceiver(self.GenericReceiverAction, 'main.playback.new')
        self.WriteFile('')
        
    def OnEnable(self, event):
        self.parent.SetReceiver(self, 'main.playback.new')        
        
    def WriteFile(self, file_text):
        f = open(self.df, 'w')
        f.write(file_text)
        f.close()
        
    def CloseMe(self, event=None):
        #self.SaveOptions()
        self.parent.KillReceiver(self.GenericReceiverAction, 'main.playback.new')
        self.WriteFile('')
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
       
charset = 'utf-8'        
def unbork(s, safe='/', want_unicode=False):
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)    
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s