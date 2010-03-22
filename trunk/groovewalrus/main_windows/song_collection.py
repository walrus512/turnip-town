# -*- coding: utf-8 -*-
"""
GrooveWalrus: Song Collection
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
#After adding directories which contain your mp3 files to your song collection (may take some time depending on number of files), the directories will be monitored and updated as new mp3's are added.

import wx
import wx.xrc as xrc
import os
import sqlite3
from main_utils import system_files
from threading import Thread
import time

SYSLOC = os.getcwd()
SONGDB_RESFILE = SYSLOC + os.sep + 'layout_songdb.xml'
#GRAPHICS_LOCATION = os.path.join(os.getcwd(), 'graphics') + os.sep

class SongDBWindow(wx.Dialog):
    """Song DB Window for adding songs"""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Song Collection Locations", size=(600, 400), pos=(10,10))#, style=wx.FRAME_SHAPED) #STAY_ON_TOP)#wx.FRAME_SHAPED)
        self.parent = parent
        
        self.FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(SONGDB_RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_song_db")

        # control references --------------------
        self.st_songdb_root = xrc.XRCCTRL(self, 'm_st_songdb_root')
        self.st_songdb_status = xrc.XRCCTRL(self, 'm_st_songdb_status')
        self.st_songdb_file = xrc.XRCCTRL(self, 'm_st_songdb_file')
        self.ga_songdb_index = xrc.XRCCTRL(self, 'm_ga_songdb_index')
        self.st_songdb_header = xrc.XRCCTRL(self, 'm_st_songdb_header')
        self.lb_songdb_directories = xrc.XRCCTRL(self, 'm_lb_songdb_directories')
        #self.bm_search_close = xrc.XRCCTRL(self, 'm_bm_search_close')
        #self.dp_songdb_dir = xrc.XRCCTRL(self, 'm_dp_songdb_dir')


        # bindings ----------------
        self.Bind(wx.EVT_BUTTON, self.OnAddClick, id=xrc.XRCID('m_bu_songdb_add'))
        self.Bind(wx.EVT_BUTTON, self.OnRemoveClick, id=xrc.XRCID('m_bu_songdb_remove'))
        self.Bind(wx.EVT_BUTTON, self.OnExitClick, id=xrc.XRCID('m_bu_songdb_ok'))
        self.Bind(wx.EVT_BUTTON, self.OnUpdateClick, id=xrc.XRCID('m_bu_songdb_update'))
        #self.Bind(wx.EVT_BUTTON, self.OnSearchClear, id=xrc.XRCID('m_bb_search_clear'))
        #self.Bind(wx.EVT_TEXT_ENTER, self.OnSearchClick, self.tc_search_text)
        #self.bm_search_close.Bind(wx.EVT_LEFT_UP, self.hide_me)
        
        ##self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        ##self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        ##self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        ##self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        ##self.st_songdb_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        ##self.st_songdb_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        ##self.st_songdb_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        ##self.st_songdb_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
                
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        self.GetLocations()        
       
#----------------------------------------------------------------------
    def show_me(self):
        # show the window
        self.MoveMe()
        self.Show(True) # Shows it
        #totals = DbFuncs().GetCountAndLast()
        #self.st_songdb_total.SetLabel(str(totals[0]))
        #self.st_songdb_last.SetLabel(totals[1])        
        
    def MoveMe(self, event=None):
        # show the window        
        ps = self.parent.GetSize()
        pp = self.parent.GetScreenPosition()
        ss = self.GetSize()        
        xn = pp[0] + (ps[0] - ss[0])
        yn = pp[1] + (ps[1] - ss[1])
        #self.SetSize((450, 450))
        self.SetPosition((xn, yn))        
        
    def hide_me(self, event=None):
        # hide the window
        self.Show(False)
        
    def OnExitClick(self, event):
        self.Destroy()
    
# --------------------------------------------------------- 
# list song collection dirs from database
# add a new song collection dir to database
# add songs from new dir to database
# check for new songs in existing dirs and add to database

    def OnAddClick(self, event):
        # In this case we include a "New directory" button. 
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            print dlg.GetPath()
            self.InsertLocation(dlg.GetPath())
        dlg.Destroy()
        
    def InsertLocation(self, folder_path):
        # insert folder path in the db
        # "m_folders": "CREATE TABLE IF NOT EXISTS m_folders (folder_id INTEGER PRIMARY KEY, folder_name TEXT, last_update DATE_TIME, primary_folder CHAR)"
        if len(folder_path) > 0:
            conn = sqlite3.connect(self.FILEDB)
            c = conn.cursor()
            c.execute('INSERT INTO m_folders (folder_name) VALUES ("' + str(folder_path) + '")')
            conn.commit()
            c.close()            
            self.GetLocations()
            self.AddData(folder_path)
            
    def GetLocations(self):
        #return a list of folder locations from db
        #add to list
        
        #clear list
        self.lb_songdb_directories.Clear()
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        
        t = 'SELECT folder_name FROM m_folders ORDER BY folder_name'
        c.execute(t)
        h = c.fetchall()
        #print h
        counter = 0
        for x in h:
            self.lb_songdb_directories.Insert(x[0], counter)
            counter = counter + 1
        c.close()
        
    def OnRemoveClick(self, event):
        # check for selected folder and remove
        list_item = self.lb_songdb_directories.GetSelection()
        if list_item >= 0:
            folder_name = self.lb_songdb_directories.GetString(list_item)
            if len(folder_name) > 1:
                conn = sqlite3.connect(self.FILEDB)        
                c = conn.cursor()
                c.execute('DELETE FROM m_folders WHERE folder_name = "' + folder_name + '"')# LIMIT 1')
                conn.commit()
                c.close()
                self.GetLocations()
        
    def AddData(self, folder_path):

        #dlg = wx.ProgressDialog("Adding Songs", " ", maximum = maxlen, parent=self, style = wx.PD_CAN_ABORT) # | wx.PD_APP_MODAL)
        self.st_songdb_root.SetLabel(folder_path)        
        self.st_songdb_status.SetLabel("Adding")
        #THREAD
        current = FileThread(self, folder_path)
        #THREAD
        current.start()
        #dlg.Update(count)                
        #dlg.Destroy()
        
    def OnUpdateClick(self, event):
        #add any new files to db for existing folder
        list_item = self.lb_songdb_directories.GetSelection()
        if list_item >= 0:
            folder_name = self.lb_songdb_directories.GetString(list_item)
            if len(folder_name) > 1:
                self.AddData(folder_name)

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
            #try:
            #    self.popup.IsShown()
            #except AttributeError:
            #    pass
            #else:
            #    if (self.popup.IsShown()):
            #        pPos = (self.wPos.x + (dPos.x - self.ldPos.x),34)
             #       self.popup.Move(pPos)

    def OnMouseLeftUp(self, evt):
        self.ReleaseMouse()

    def OnRightUp(self, evt):
        self.hide_me()
        #self..Destroy()
        
# --------------------------------------------------------- 
# ####################################
class FileThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, parent, base_path):
        Thread.__init__(self)
        self.parent = parent
        self.base_path = base_path
        self.FILEDB = system_files.GetDirectories(self.parent).DataDirectory() + os.sep + 'gravydb.sq3'
                        
    def run(self):
        self.FillDb(self.base_path)

# ---------------------------------------------------------
    def FillDb(self, base_path):
        #basePath = 'E:\\Music\\Albums\\Albums_01'
        #basePath = 'E:\\Music'
        #basepath = e:\
            
        allfiles = []
        subfiles = []
        self.parent.ga_songdb_index.SetValue(0)
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        counter = 0
        first_dir = True
        
        for root, dirs, files in os.walk(base_path):
            if first_dir == True:
                self.parent.ga_songdb_index.SetRange(len(dirs) + 1)
                first_dir = False
            for f in files:
                if f.endswith('.mp3'):
                    self.parent.st_songdb_file.SetLabel(f)
                    path_n = root.rsplit(os.sep, 1)[0].replace(os.sep, '/')
                    folder_n = root.rsplit(os.sep, 1)[1]
                    file_n = f
                    
                    #check if file already exists in db
                    t = 'SELECT music_id FROM m_files WHERE folder_path = "' + path_n + '" AND folder_name = "' + folder_n + '" AND file_name = "' + file_n + '"'
                    c.execute(t)
                    h = c.fetchall()
                    
                    #add if not found
                    if len(h) == 0:                    
                        self.parent.st_songdb_status.SetLabel("Adding")
                        c.execute('INSERT INTO m_files values (null,?,?,?)', (path_n, folder_n, file_n))                    
                        conn.commit()                        
                    else:
                        self.parent.st_songdb_status.SetLabel("Skipping")
                    #print file_n
                    #print path_n
                    #print folder_n
                    time.sleep(.05)
            counter = counter + 1
            self.parent.ga_songdb_index.SetValue(counter)            
        c.close()
        self.parent.st_songdb_status.SetLabel("Finished")
        self.parent.parent.lc_scol_col.SetItemCount(GetCount())
    
        
#-----------------------------------------------------


def GetCount():
    FILEDB = system_files.GetDirectories(None).DataDirectory() + os.sep + 'gravydb.sq3'
    # get row count
    rcount = 0    
    conn = sqlite3.connect(FILEDB)
    c = conn.cursor()
    t = "SELECT COUNT(*) as rcount FROM m_files ORDER BY music_id DESC LIMIT 1"
    c.execute(t)
    h = c.fetchall()
    for x in h:        
        rcount = x[0]
    c.close()
    return rcount 

def AddSingleFile(complete_filename):
    #add a single file to the database, files table
    FILEDB = system_files.GetDirectories(None).DataDirectory() + os.sep + 'gravydb.sq3'
        
    conn = sqlite3.connect(FILEDB)
    c = conn.cursor()
    f = complete_filename
    
    if f.endswith('.mp3'):
        path_n = f.rsplit(os.sep, 1)[0].replace(os.sep, '/')
        folder_n = ''
        file_n = f.rsplit(os.sep, 1)[1]
        
        #check if file already exists in db
        t = 'SELECT music_id FROM m_files WHERE folder_path = "' + path_n + '" AND folder_name = "' + folder_n + '" AND file_name = "' + file_n + '"'
        c.execute(t)
        h = c.fetchall()
        
        #add if not found
        if len(h) == 0:                    
            c.execute('INSERT INTO m_files values (null,?,?,?)', (path_n, folder_n, file_n))                    
            conn.commit()            
        #print file_n
        #print path_n
        #print folder_n        
    c.close()