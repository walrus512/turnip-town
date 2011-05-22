"""
GrooveWalrus: Hotkeys Plug-in 
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

from main_utils import system_files
from main_windows import options_window
from main_utils import hotkeys
from main_utils import global_hotkeys

RESFILE = os.path.join(os.getcwd(), 'plugins','hotkeys') + os.sep + "layout_hotkeys.xml"

class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Hotkeys", size=(375,460), style=wx.FRAME_SHAPED|wx.RESIZE_BORDER) #STAY_ON_TOP)        
        self.parent = parent        
        self.FILEDB = system_files.GetDirectories(self).DatabaseLocation()

        # xrc layout xml
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_hotkeys")

        # control references --------------------
        self.tc_acc_previous = xrc.XRCCTRL(self, 'm_tc_acc_previous')
        self.tc_acc_play = xrc.XRCCTRL(self, 'm_tc_acc_play')
        self.tc_acc_stop = xrc.XRCCTRL(self, 'm_tc_acc_stop')
        self.tc_acc_next = xrc.XRCCTRL(self, 'm_tc_acc_next')
        self.tc_acc_volume_up = xrc.XRCCTRL(self, 'm_tc_acc_volume_up')
        self.tc_acc_volume_down = xrc.XRCCTRL(self, 'm_tc_acc_volume_down')
        self.tc_acc_volume_mute = xrc.XRCCTRL(self, 'm_tc_acc_volume_mute')
        self.tc_acc_repeat = xrc.XRCCTRL(self, 'm_tc_acc_repeat')
        self.tc_acc_shuffle = xrc.XRCCTRL(self, 'm_tc_acc_shuffle')
        
        self.st_acc_previous = xrc.XRCCTRL(self, 'm_st_acc_previous')
        self.st_acc_play = xrc.XRCCTRL(self, 'm_st_acc_play')
        self.st_acc_stop = xrc.XRCCTRL(self, 'm_st_acc_stop')
        self.st_acc_next = xrc.XRCCTRL(self, 'm_st_acc_next')
        self.st_acc_volume_up = xrc.XRCCTRL(self, 'm_st_acc_volume_up')
        self.st_acc_volume_down = xrc.XRCCTRL(self, 'm_st_acc_volume_down')
        self.st_acc_volume_mute = xrc.XRCCTRL(self, 'm_st_acc_volume_mute')
        self.st_acc_repeat = xrc.XRCCTRL(self, 'm_st_acc_repeat')
        self.st_acc_shuffle = xrc.XRCCTRL(self, 'm_st_acc_shuffle')
        #---
        self.tc_previous = xrc.XRCCTRL(self, 'm_tc_previous')
        self.tc_play = xrc.XRCCTRL(self, 'm_tc_play')
        self.tc_stop = xrc.XRCCTRL(self, 'm_tc_stop')
        self.tc_next = xrc.XRCCTRL(self, 'm_tc_next')
        self.tc_volume_up = xrc.XRCCTRL(self, 'm_tc_volume_up')
        self.tc_volume_down = xrc.XRCCTRL(self, 'm_tc_volume_down')
        self.tc_volume_mute = xrc.XRCCTRL(self, 'm_tc_volume_mute')
        self.tc_repeat = xrc.XRCCTRL(self, 'm_tc_repeat')
        self.tc_shuffle = xrc.XRCCTRL(self, 'm_tc_shuffle')
        self.ch_modifier = xrc.XRCCTRL(self, 'm_ch_modifier')
        self.rb_modifier = xrc.XRCCTRL(self, 'm_rb_modifier')
        
        #header for dragging and moving
        self.st_hotkeys_header = xrc.XRCCTRL(self, 'm_st_hotkeys_header')
        self.bm_hotkeys_close = xrc.XRCCTRL(self, 'm_bm_hotkeys_close')
        
        # bindings ----------------        
        self.bm_hotkeys_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        self.tc_acc_previous.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_play.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_stop.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_next.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_volume_up.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_volume_down.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_volume_mute.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_repeat.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.tc_acc_shuffle.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
        self.tc_previous.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_play.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_stop.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_next.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_volume_up.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_volume_down.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_volume_mute.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_repeat.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        self.tc_shuffle.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown2)
        
        # self.tc_acc_modifier.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick, id=xrc.XRCID('m_bu_acc_save'))
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick, id=xrc.XRCID('m_bu_save'))
        self.Bind(wx.EVT_BUTTON, self.CloseMe, id=xrc.XRCID('m_bu_acc_cancel'))
        self.Bind(wx.EVT_BUTTON, self.CloseMe, id=xrc.XRCID('m_bu_cancel'))
                
        #dragging and moving
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_hotkeys_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_hotkeys_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_hotkeys_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_hotkeys_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetSize(self.GetEffectiveMinSize())
        
        # load settings -----------
        self.LoadSettings()
        self.SetLabels()
        
    def OnKeyDown2(self, event):
        #event.Skip()
        #set the keycode to teh text control
        event.GetEventObject().SetValue(str(event.GetRawKeyCode()))
        
    def OnKeyDown(self, event):
        #event.Skip()
        #set the keycode to teh text control
        event.GetEventObject().SetValue(str(event.GetKeyCode()))
        self.SetLabels()
        
    def SetLabels(self):
        #print hotkeys.GetKeyName(int(self.tc_acc_previous.GetValue()))
        self.st_acc_previous.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_previous.GetValue())))
        self.st_acc_play.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_play.GetValue())))
        self.st_acc_stop.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_stop.GetValue())))
        self.st_acc_next.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_next.GetValue())))
        self.st_acc_volume_down.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_volume_down.GetValue())))
        self.st_acc_volume_up.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_volume_up.GetValue())))
        self.st_acc_volume_mute.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_volume_mute.GetValue())))
        self.st_acc_shuffle.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_shuffle.GetValue())))
        self.st_acc_repeat.SetLabel(hotkeys.GetKeyName(int(self.tc_acc_repeat.GetValue())))
        
    def OnSaveClick(self, event):
        """Saves the goddamn stuff to the db."""                
        options_window.SetSetting('hotkey-previous', self.tc_previous.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-play', self.tc_play.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-stop', self.tc_stop.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-next', self.tc_next.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-volume-up', self.tc_volume_up.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-volume-down', self.tc_volume_down.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-volume-mute', self.tc_volume_mute.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-shuffle', self.tc_shuffle.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-repeat', self.tc_repeat.GetValue(), self.FILEDB)
        options_window.SetSetting('hotkey-modifier', self.ch_modifier.GetSelection(), self.FILEDB)
        options_window.SetSetting('hotkey-modifier-type', str(self.rb_modifier.GetSelection()), self.FILEDB)
        
        options_window.SetSetting('acc-previous', self.tc_acc_previous.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-play', self.tc_acc_play.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-stop', self.tc_acc_stop.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-next', self.tc_acc_next.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-volume-up', self.tc_acc_volume_up.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-volume-down', self.tc_acc_volume_down.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-volume-mute', self.tc_acc_volume_mute.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-shuffle', self.tc_acc_shuffle.GetValue(), self.FILEDB)
        options_window.SetSetting('acc-repeat', self.tc_acc_repeat.GetValue(), self.FILEDB)
        
        # set/reset hotkeys
        hotkeys.Hotkeys(self.parent).SetHotkeys()        
        global_hotkeys.GlobalHotkeys(self.parent)
        
        
        self.CloseMe()        
        
    def LoadSettings(self):
        """Loads the goddamn stuff from the db."""
        key_list = [                
                ('hotkey-play',self.tc_play),
                ('hotkey-stop',self.tc_stop),
                ('hotkey-next',self.tc_next),
                ('hotkey-volume-up',self.tc_volume_up),
                ('hotkey-volume-down',self.tc_volume_down),
                #('hotkey-modifier',self.tc_acc_modifier),
                ('hotkey-previous',self.tc_previous),
                ('hotkey-volume-mute',self.tc_volume_mute),
                ('hotkey-repeat',self.tc_repeat),
                ('hotkey-shuffle',self.tc_shuffle),
                
                ('acc-play',self.tc_acc_play),
                ('acc-stop',self.tc_acc_stop),
                ('acc-next',self.tc_acc_next),
                ('acc-volume-up',self.tc_acc_volume_up),
                ('acc-volume-down',self.tc_acc_volume_down),
                #('hotkey-modifier',self.tc_acc_modifier),
                ('acc-previous',self.tc_acc_previous),
                ('acc-volume-mute',self.tc_acc_volume_mute),
                ('acc-repeat',self.tc_acc_repeat),
                ('acc-shuffle',self.tc_acc_shuffle),
                ]
        for key_name in key_list:
            y = options_window.GetSetting(key_name[0], self.FILEDB)
            if y:
                key_name[1].SetValue(y)
                
        rb = options_window.GetSetting('hotkey-modifier-type', self.FILEDB)
        if rb:
            self.rb_modifier.SetSelection(int(rb))
        ch = options_window.GetSetting('hotkey-modifier', self.FILEDB)
        if ch:
            self.ch_modifier.SetSelection(int(ch))
            
    def CloseMe(self, event=None):
        #self.SaveOptions()
        #self.parent.KillReceiver(self.GenericReceiverAction, 'main.playback.new')
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
        