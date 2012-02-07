"""
GrooveWalrus: Minimode Plug-in 
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
import os
from main_controls import playback_panel

RESFILE = os.path.join(os.getcwd(), 'plugins','minimode') + os.sep + "layout_minimode.xml"
GRAPHICS_LOCATION = ''

class MainPanel(wx.Frame):
    def __init__(self, parent, pathToPlugins=None):
        if(not pathToPlugins==None):
            RESFILE = os.path.join(pathToPlugins,'minimode') + os.sep + "layout_minimode.xml"
        
        wx.Frame.__init__(self, parent, -1, "minimode", size=(620,42), pos=((wx.GetDisplaySize()[0] / 2) - (310),-2), style=wx.FRAME_SHAPED | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR)        
        
        self.parent = parent
        
        #self.minimode_SETTINGS = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep
        
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        self.panel = res.LoadPanel(self, "m_pa_plugin_minimode")

        # control references --------------------
        self.bm_minimode_play = xrc.XRCCTRL(self, 'm_bm_minimode_play')
        self.bm_minimode_forward = xrc.XRCCTRL(self, 'm_bm_minimode_forward')
        self.bm_minimode_backward = xrc.XRCCTRL(self, 'm_bm_minimode_backward')
        self.bm_minimode_grabber = xrc.XRCCTRL(self, 'm_bm_minimode_grabber')
        self.m_pa_minimode_status = xrc.XRCCTRL(self, 'm_pa_minimode_status')
        

        #header for dragging and moving
        self.st_minimode_header = xrc.XRCCTRL(self, 'm_st_minimode_header')
        self.bm_minimode_close = xrc.XRCCTRL(self, 'm_bm_minimode_close')
        self.hw_minimode_home = xrc.XRCCTRL(self, 'm_hw_minimode_home')
        self.hw_minimode_at = xrc.XRCCTRL(self, 'm_hw_minimode_at')

        # bindings ----------------
        self.bm_minimode_play.Bind(wx.EVT_LEFT_UP, self.OnPlayClick)
        self.bm_minimode_forward.Bind(wx.EVT_LEFT_UP, self.OnForwardClick)
        self.bm_minimode_backward.Bind(wx.EVT_LEFT_UP, self.OnBackwardClick)
        self.bm_minimode_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        
        self.bm_minimode_play.Bind(wx.EVT_ENTER_WINDOW, self.OnPlayHover)
        self.bm_minimode_play.Bind(wx.EVT_LEAVE_WINDOW, self.OnPlayHoverOut)
        self.bm_minimode_forward.Bind(wx.EVT_ENTER_WINDOW, self.OnForwardHover)
        self.bm_minimode_forward.Bind(wx.EVT_LEAVE_WINDOW, self.OnForwardHoverOut)
        self.bm_minimode_backward.Bind(wx.EVT_ENTER_WINDOW, self.OnBackwardHover)
        self.bm_minimode_backward.Bind(wx.EVT_LEAVE_WINDOW, self.OnBackwardHoverOut)
        
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.bm_minimode_grabber.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.bm_minimode_grabber.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.bm_minimode_grabber.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.bm_minimode_grabber.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       

        #cursor for grabber moving
        cursor = wx.StockCursor(wx.CURSOR_SIZING)
        self.bm_minimode_grabber.SetCursor(cursor)
            
        #self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.ALL|wx.GROW, 0)
        #self.SetSizer(sizer)
        self.SetSizerAndFit(sizer)
        self.SetAutoLayout(True)
        self.SetSize((580,34))
        #self.SetTransparent(200)
        
        #make it smaller and uglier
        self.m_pa_minimode_status.SetSize(1)
        #self.m_pa_minimode_status.SetColours(background='#f5f5f5', text='#000000', progress='#ff9000', download='#965b0f')
        
        # timer ----------------
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.time_count = 0
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
    def OnTimer(self, event):
        self.Refresh()
        
    def CloseMe(self, event=None):
        self.Destroy()
        
    def OnPlayClick(self, event):
        self.parent.OnPlayClick(None)
        
    def OnForwardClick(self, event):
        self.parent.OnForwardClick(None)
        
    def OnBackwardClick(self, event):
        self.parent.OnBackwardClick(None)
        
    def OnPlayHover(self, event):
        hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + './plugins/minimode/m_play-hover.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.bm_minimode_play.SetBitmap(hover_bmp)
        
    def OnPlayHoverOut(self, event):
        hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + './plugins/minimode/m_play.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.bm_minimode_play.SetBitmap(hover_bmp)
        
    def OnForwardHover(self, event):
        hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + './plugins/minimode/m_forward-hover.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.bm_minimode_forward.SetBitmap(hover_bmp)
        
    def OnForwardHoverOut(self, event):
        hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + './plugins/minimode/m_forward.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.bm_minimode_forward.SetBitmap(hover_bmp)

    def OnBackwardHover(self, event):
        hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + './plugins/minimode/m_backward-hover.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.bm_minimode_backward.SetBitmap(hover_bmp)
        
    def OnBackwardHoverOut(self, event):
        hover_bmp = wx.Bitmap(GRAPHICS_LOCATION + './plugins/minimode/m_backward.png', wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        self.bm_minimode_backward.SetBitmap(hover_bmp)   
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
            if (self.wPos.y + (dPos.y - self.ldPos.y)) < 10:
                #snap to top to screen
                nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
            else:
                nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, event):        
        #self.Destroy()
        pass
        
# --------------------------------------------------------- 
