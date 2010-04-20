# -*- coding: utf-8 -*-
"""
GrooveWalrus: Album Viewer 
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

class AlbumViewer(wx.Frame):
    def __init__(self, parent, graphics_loc):        
        wx.Frame.__init__(self, parent, -1, size=(300,300), style=wx.FRAME_NO_TASKBAR)# wx.STAY_ON_TOP|wx.FRAME_SHAPED|wx.FRAME_NO_TASKBAR
        
        self.parent = parent
        self.checkmark_loc = graphics_loc        
        self.bitmap_cover = wx.StaticBitmap(self, -1, size=(300,300))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bitmap_cover, 1, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClickMenu)
                
        self.bitmap_cover.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.bitmap_cover.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.bitmap_cover.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.bitmap_cover.Bind(wx.EVT_RIGHT_UP, self.OnRightClickMenu)
        
        self.Show(False)
        self.MakeModal(False)

    def SetImage(self, file_name, dir_name):
        # set 
        cover_bmp = wx.Bitmap(dir_name + file_name, wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        
        foo = wx.Bitmap.ConvertToImage(cover_bmp)
        if self.parent.palbum_art_file =='':
            self.parent.Resizer(foo, (300,300))
        else:
            foo.Rescale(300, 300)
        goo = wx.BitmapFromImage(foo)
        self.bitmap_cover.SetBitmap(goo)
        
    def ToggleShow(self, event=None):
        if self.IsShown():
            self.Show(False)
        else:
            self.Show(True)
        return self.IsShown()
            
    def ToggleOnTop(self, event):
        if self.GetWindowStyle() == 2:
            self.SetWindowStyle(wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR)            
        else:
            self.SetWindowStyle(wx.FRAME_NO_TASKBAR)
            
    def OnRightClickMenu(self, event):        
        # make a menu
        ID_HIDE = 1
        ID_TOP = 2
        
        menu = wx.Menu()
        
        # Show how to put an icon in the menu
        item = wx.MenuItem(menu, ID_TOP, "Toggle Always On Top")
        
        # display checkmark in menu if frame in on top
        if self.GetWindowStyle() != 2:
            check_bmp = wx.Bitmap(self.checkmark_loc + 'checkmark.png', wx.BITMAP_TYPE_ANY)
            item.SetBitmap(check_bmp)
        menu.AppendItem(item)
        
        submenu = wx.Menu()
        submenu.Append(2031,"0%")
        submenu.Append(2032,"13%")
        submenu.Append(2033,"25%")
        submenu.Append(2035,"50%")
        menu.AppendMenu(203, "Transparency", submenu)        
        #self.MakeTransparent(self, 170)

        menu.AppendSeparator()
        menu.Append(ID_HIDE, "Hide Me")        
        
        wx.EVT_MENU(self, ID_TOP, self.ToggleOnTop)
        wx.EVT_MENU(self, ID_HIDE, self.ToggleShow)
        wx.EVT_MENU(self, 2031, self.OnTransp)
        wx.EVT_MENU(self, 2032, self.OnTransp)
        wx.EVT_MENU(self, 2033, self.OnTransp)
        wx.EVT_MENU(self, 2035, self.OnTransp)
        
        self.PopupMenu(menu)
        menu.Destroy()
        
        
# ---------------------------------------------------------
    def OnTransp(self, event):
        # range 0 to 255
        self.MakeTransparent(self, (255 - (event.GetId() - 2031) * 32))        
        
# tittlebar-like move and drag
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
            try:
                self.popup.IsShown()
            except AttributeError:
                pass
            else:
                if (self.popup.IsShown()):
                    pPos = (self.wPos.x + (dPos.x - self.ldPos.x),34)
                    self.popup.Move(pPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        #self.Show(False)
        #self.parent.Destroy()
        self.ToggleShow()        
              
# ---------------------------------------------------------        
    def MakeTransparent(self, window, amount):
        hwnd = window.GetHandle()
        try:
            import ctypes
            _winlib = ctypes.windll.user32
            style = _winlib.GetWindowLongA(hwnd, 0xffffffecL)
            style |= 0x00080000
            _winlib.SetWindowLongA(hwnd, 0xffffffecL, style)
            _winlib.SetLayeredWindowAttributes(hwnd, 0, amount, 2)

        except ImportError:
            import win32api, win32con, winxpgui
            _winlib = win32api.LoadLibrary("user32")
            pSetLayeredWindowAttributes = win32api.GetProcAddress(
                _winlib, "SetLayeredWindowAttributes")
            if pSetLayeredWindowAttributes == None:
                return
            exstyle = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if 0 == (exstyle & 0x80000):
                win32api.SetWindowLong(hwnd,
                                       win32con.GWL_EXSTYLE,
                                       exstyle | 0x80000)
            winxpgui.SetLayeredWindowAttributes(hwnd, 0, amount, 2)
# ---------------------------------------------------------
 

