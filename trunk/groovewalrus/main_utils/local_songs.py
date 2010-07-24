# -*- coding: utf-8 -*-
"""
GrooveWalrus: play local songs / gravy db setup / mp3 tag reading
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

import os
import sqlite3
import time
from threading import Thread

from main_thirdp import mp3tag
from main_utils import system_files

import sys
SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())

#queries


# use sqlite to store collection
# index files based on directories
# update based on folder numbers
class DbFuncs(object):
    def __init__(self):
        self.FILEDB = system_files.GetDirectories(None).DatabaseLocation()
       
    def create_tables(self):

        conn = sqlite3.connect(self.FILEDB)

        c = conn.cursor()        
        tabledict = {"m_files": "CREATE TABLE IF NOT EXISTS m_files (music_id INTEGER PRIMARY KEY, folder_path TEXT, folder_name TEXT, file_name TEXT)",
         "m_tracks": "CREATE TABLE IF NOT EXISTS m_tracks (track_id INTEGER PRIMARY KEY, grooveshark_id INTEGER, music_id INTEGER, track_time INTEGER, tag_id INTEGER, artist TEXT, song TEXT, album TEXT, album_art_file TEXT)",
         "m_pop": "CREATE TABLE IF NOT EXISTS m_pop (pop_id INTEGER PRIMARY KEY, track_id INTEGER, listeners INTEGER, playcount INTEGER)",
         "m_tag": "CREATE TABLE IF NOT EXISTS m_tag (tag_id INTEGER PRIMARY KEY, tag_label TEXT)",
         "m_playcount": "CREATE TABLE IF NOT EXISTS m_playcount (playcount_id INTEGER PRIMARY KEY, track_id INTEGER, local_playcount INTEGER, last_play_date DATETIME)",
         "m_rating": "CREATE TABLE IF NOT EXISTS m_rating (rating_id INTEGER PRIMARY KEY, track_id INTEGER, rating_type_id INTEGER)",
         "m_settings": "CREATE TABLE IF NOT EXISTS m_settings (setting_id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)",
         "m_folders": "CREATE TABLE IF NOT EXISTS m_folders (folder_id INTEGER PRIMARY KEY, folder_name TEXT, last_update DATE_TIME, primary_folder CHAR)",
         "m_feeds": "CREATE TABLE IF NOT EXISTS m_feeds (feed_id INTEGER PRIMARY KEY, feed_name TEXT, feed_url TEXT, last_update DATE_TIME)",
         "m_played": "CREATE TABLE IF NOT EXISTS m_played (played_id INTEGER PRIMARY KEY, played_type_id INTEGER, track_id INTEGER, played_date DATE_TIME)",
         "m_playlists": "CREATE TABLE IF NOT EXISTS m_playlists (playlist_id INTEGER PRIMARY KEY, artist TEXT, song TEXT, playlist_position INTEGER, playlist_date DATE_TIME)",
         "m_playlist_labels": "CREATE TABLE IF NOT EXISTS m_playlist_labels (playlist_label_id INTEGER PRIMARY KEY, playlist_label TEXT, playlist_date DATE_TIME)"
         }
    
        # Create table
        for x in tabledict:
            c.execute(tabledict[x])
        conn.commit()
        c.close()    
    
    def GetCountAndLast(self, query='default'):
        # get row count
        rcount = 0
        filen = ''        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        if query == 'default':
            t = "SELECT music_id, folder_path, folder_name, COUNT(*) as rcount FROM m_files ORDER BY music_id DESC LIMIT 1"
        else:
           t = query 
        c.execute(t)
        h = c.fetchall()
        for x in h:        
            rcount = x[3]
            if x[1] != None:
                filen = str(x[1]) + '/' + str(x[2])
        c.close()
        return (rcount, filen)
        
    def GetLast(self, query='default'):
        # get row count
        rcount = 0    
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        if query == 'default':
            t = "SELECT COUNT(*) as rcount FROM m_files ORDER BY music_id DESC LIMIT 1"
        else:
           t = query 
        c.execute(t)
        h = c.fetchall()
        for x in h:        
            rcount = x[0]
        c.close()
        return rcount
        
    def GetRow(self, row_num, column):
        # get row count
        row_num = row_num + 1
        ritem = ''
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        tq = "SELECT music_id, file_name, folder_name, folder_path FROM m_files WHERE music_id = " + str(row_num)
        c.execute(tq)
        h = c.fetchall()
        for x in h:
            ritem = x[column]
        c.close()
        return (ritem)
        
        
    def RemoveRow(self, music_id):
        # get row count
        
        if len(music_id) > 0:
            conn = sqlite3.connect(self.FILEDB)
            c = conn.cursor()
            #t = "DELETE FROM m_files WHERE music_id = " + str(music_id) # + " LIMIT 1"   
            #print t
            c.execute('DELETE FROM m_files WHERE music_id=?', (int(music_id), ))
            conn.commit()
            c.close()
            
    def MakeQuery(self, query, qlimit, folder_query=1):
        q_rep = query.replace("'","").replace("!","").replace("&"," ").replace(",","").replace("-"," ")
        q_split = q_rep.split(' ')
        s = ''
        the_and = ''
        #check if we want to search files or folders
        if folder_query > 1:
            f_string = 'folder_name'
        else:
            f_string = 'file_name'
            
        if len(q_split) > 1:
            for y in q_split:
                s = s + the_and + " " + f_string + " LIKE '%" + y + "%'"
                the_and = ' AND'
            t = "SELECT music_id, file_name, folder_name, folder_path FROM m_files WHERE " + s + " ORDER BY RANDOM() LIMIT " + str(qlimit)
        else:
            t = "SELECT music_id, file_name, folder_name, folder_path FROM m_files WHERE " + f_string + " LIKE '%" + query + "%'  ORDER BY RANDOM() LIMIT " + str(qlimit) #('%' + query + '%',)
            
        if folder_query > 2:
            t = t.replace(' music_id, file_name, folder_name, folder_path ', ' DISTINCT folder_name ')
            t = t.replace(' LIMIT ', ' ORDER BY folder_name LIMIT ')
            t = t.replace('ORDER BY RANDOM()', '')
            #print t
        return t
        
    def GetResults(self, query, qlimit):
        r_arr = []
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        
        t = self.MakeQuery(query, qlimit)
        
        c.execute(t)
        h = c.fetchall()
        for x in h:
            #print x[0].replace('_', ' ').replace(' - ', '-')
            r_arr.append(x[3] + '/' + x[2] + '/' + x[1])
        c.close()
        return r_arr
                
    def GetResultsArray(self, query, qlimit, with_count=False, folder_query=1):
        r_arr = []
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
           
        t = self.MakeQuery(query, qlimit, folder_query)#, with_count)
        #print t
        c.execute(t)
        h = c.fetchall()
        counter = 0
        for x in h:
            file_name = ''
            if len(x) > 1:
                file_name = x[3] + '/' + x[2] + '/' + x[1]
            #print x[0].replace('_', ' ').replace(' - ', '-')
            s_arr = []
            if with_count == True:
                if folder_query > 2:
                    s_arr.append('')
                    s_arr.append('')
                    s_arr.append(x[0])
                    s_arr.append('')
                else:
                    s_arr.append(x[0])
                    s_arr.append(x[1])
                    s_arr.append(x[2])
                    s_arr.append(x[3])
            else:
                if os.path.isfile(file_name):
                    s_arr.append(GetMp3Artist(file_name))
                    s_arr.append(GetMp3Title(file_name))
                    s_arr.append(GetMp3Album(file_name))
            s_arr.append(file_name)
            r_arr.append(s_arr)
            counter = counter + 1
            
        c.close()
        return r_arr
        
    def GetSpecificResultArray(self, query, specific_artist, specific_song):
        #used when automatically getting the first result for automatic playbalc
        r_arr = []
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        limit = 15
        t = self.MakeQuery(query, limit)#, with_count)
        
        c.execute(t)
        h = c.fetchall()
        c.close()
        
        for x in h:
            file_name = ''
            if len(x) > 1:
                file_name = x[3] + '/' + x[2] + '/' + x[1]
            s_arr = []
            g_artist = ''
            g_song = ''
            if os.path.isfile(file_name):
                g_artist = GetMp3Artist(file_name)
                g_song = GetMp3Title(file_name)
        
            found_exact_match = False

            if (specific_artist == g_artist) & (specific_song == g_song):
                found_exact_match = True
                    
            if found_exact_match == True:
                s_arr.append(x[0])
                s_arr.append(x[1])
                s_arr.append(x[2])
                s_arr.append(x[3])
                s_arr.append(file_name)
                r_arr.insert(0, s_arr)
            else:
                s_arr.append(x[0])
                s_arr.append(x[1])
                s_arr.append(x[2])
                s_arr.append(x[3])
                s_arr.append(file_name)
                r_arr.append(s_arr)                

        return r_arr
        
        
    def InsertTrackData(self, p_grooveshark_id, p_music_id, p_track_time, p_tag_id, p_artist, p_song, p_album, p_album_art_file):
        #check for existing track
        #update values
        #add new record
        #grooveshark_id, music_id, track_time, tag_id, artist, 
        #song, album, album_art_file, rating_type_id
        if p_tag_id == '':
            p_tag_id = 0;    
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        
        #if p_grooveshark_id >= 1:
        #    qp = " grooveshark_id = " + str(p_grooveshark_id)
        #else:
        ##qp = " music_id = " + str(p_music_id)
        #print qp
        ##if p_music_id >= 1:
        ##    t = "SELECT track_id FROM m_tracks WHERE" + qp
        #print t
        ##if (p_grooveshark_id == 0) & (p_music_id == 0):
        ##elif p_grooveshark_id >= 1:
        ##    qp = " grooveshark_id = " + str(p_grooveshark_id)
        ##    t = "SELECT track_id FROM m_tracks WHERE" + qp
        ##else:
        t = 'SELECT track_id FROM m_tracks WHERE artist="' + p_artist + '" AND song="' + p_song + '"' # AND track_time=' + str(p_track_time)
        
        c.execute(t)
        h = c.fetchall()
        #print t
        if len(h) >= 1:
            g_track_id = h[0][0]        
            c.execute('UPDATE m_tracks SET track_time= ' + str(p_track_time) + ', tag_id=' + str(p_tag_id) + ', artist="' + p_artist + '", song="' + p_song + '", album="' + p_album + '", album_art_file="' + p_album_art_file + '" WHERE track_id=' + str(g_track_id))
            conn.commit()
        else:
            c.execute('INSERT INTO m_tracks values (null,?,?,?,?,?,?,?,?)', (p_grooveshark_id, p_music_id, p_track_time, p_tag_id, p_artist, p_song, p_album, p_album_art_file))
            conn.commit()
            t = 'SELECT track_id FROM m_tracks ORDER BY track_id DESC LIMIT 1'
            c.execute(t)
            #print t
            g_track_id = c.fetchall()[0][0]
        c.close()
        return g_track_id
        
    def GetTrackId(self, grooveshark_id, music_id, artist, song):
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        t = 'SELECT track_id FROM m_tracks WHERE artist="' + artist + '" AND song="' + song + '"'
        c.execute(t)
        h = c.fetchall()
        #print t
        if len(h) >= 1:
            g_track_id = h[0][0]        
        else:
            c.execute('INSERT INTO m_tracks values (null,?,?,?,?,?,?,?,?)', (grooveshark_id, music_id, 240, '', artist, song, '', ''))
            conn.commit()
            t = 'SELECT track_id FROM m_tracks ORDER BY track_id DESC LIMIT 1'
            c.execute(t)
            #print t
            g_track_id = c.fetchall()[0][0]
        c.close()
        return g_track_id
        
    def InsertTagData(self, p_tag_label):
        #check for existing tag
        #if doesn't exit add a new one
        #return tag id in either case
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        
        t = 'SELECT tag_id FROM m_tag WHERE tag_label="' + p_tag_label + '"'
        c.execute(t)
        h = c.fetchall()
        #print h
        if len(h) >= 1:
            tag_id = h[0][0]
        else:
            c.execute('INSERT INTO m_tag (tag_label) VALUES ("' + p_tag_label + '")')
            conn.commit()
            t = 'SELECT tag_id FROM m_tag WHERE tag_label="' + p_tag_label + '"'
            c.execute(t)
            tag_id = c.fetchall()[0][0]
        c.close()
        
        return tag_id
        
    def InsertPopData(self, p_track_id, p_listeners, p_playcount):
        #track_id, listeners, playcount
        #check for existing
        #update record
        #add new record
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        
        t = 'SELECT pop_id FROM m_pop WHERE track_id=' + str(p_track_id) + ''
        c.execute(t)
        h = c.fetchall()
        #print h
        if len(h) >= 1:
            g_pop_id = h[0][0]
            c.execute('UPDATE m_pop SET track_id= ' + str(p_track_id) + ', listeners=' + str(p_listeners) + ', playcount=' + str(p_playcount) + ' WHERE pop_id =' + str(g_pop_id))
            conn.commit()
        else:
            c.execute('INSERT INTO m_pop (track_id, listeners, playcount) VALUES (' + str(p_track_id) + ', ' + str(p_listeners) + ', ' + str(p_playcount) + ')')
            conn.commit()
        c.close()
        
    def InsertPlaycountData(self, p_track_id):
        #track_id, local_playcount, last_play_date
        #check for existing
        #update record
        #select datetime('now','localtime')
        #check for pcount 
        #if doesn't exist add a new one
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        
        t = 'SELECT playcount_id, local_playcount FROM m_playcount WHERE track_id=' + str(p_track_id) + ''
        c.execute(t)
        h = c.fetchall()
        #print h
        if len(h) >= 1:
            g_playcount_id = h[0][0]
            g_local_playcount = int(h[0][1]) + 1
            c.execute('UPDATE m_playcount SET track_id= ' + str(p_track_id) + ', local_playcount=' + str(g_local_playcount) + ', last_play_date=datetime("now","localtime") WHERE playcount_id =' + str(g_playcount_id))
            conn.commit()
        else:
            c.execute('INSERT INTO m_playcount (track_id, local_playcount, last_play_date) VALUES (' + str(p_track_id) + ', 1, datetime("now","localtime"))')
            conn.commit()
        c.close()
        
        #return tag_id
        
    def InsertRatingData(self, p_track_id, p_rating_id):
        # add rating for track
        #rating_id INTEGER PRIMARY KEY, track_id INTEGER, rating_type_id INTEGER
        #check for existing
        #update record or creat new
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        
        t = 'SELECT rating_id, rating_type_id FROM m_rating WHERE track_id=' + str(p_track_id) + ''
        c.execute(t)
        h = c.fetchall()
        #print h
        if len(h) >= 1:                        
            c.execute('UPDATE m_rating SET rating_type_id= ' + str(p_rating_id) + ' WHERE track_id =' + str(p_track_id))
            conn.commit()
        else:
            c.execute('INSERT INTO m_rating (track_id, rating_type_id) VALUES (' + str(p_track_id) + ', ' + str(p_rating_id) +')')
            conn.commit()
        c.close()
        
    def InsertFeedData(self, p_feed_url):
        # add feed url
        #check for existing
        #update record or creat new        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()        
        t = 'SELECT feed_url FROM m_feeds WHERE feed_url="' + str(p_feed_url) + '"'
        c.execute(t)
        h = c.fetchall()
        #print h
        if len(h) >= 1:                        
            #c.execute('UPDATE m_feed SET rating_type_id= ' + str(p_rating_id) + ' WHERE track_id =' + str(p_track_id))
            #conn.commit()
            pass
        else:
            c.execute('INSERT INTO m_feeds (feed_url) VALUES ("' + str(p_feed_url) +'")')
            conn.commit()
        c.close()
        
    def RemoveFeedRow(self, p_feed_url):
        # get row count
        
        if len(p_feed_url) > 0:
            conn = sqlite3.connect(self.FILEDB)
            c = conn.cursor()
            #t = "DELETE FROM m_files WHERE music_id = " + str(music_id) # + " LIMIT 1"   
            #print t
            c.execute('DELETE FROM m_feeds WHERE feed_url=?', (p_feed_url, ))
            conn.commit()
            c.close()
                    
    def InsertPlaylistData(self, p_playlist_arr):
        # add feed url
        #check for existing
        #update record or creat new        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        for x in p_playlist_arr:
            #[(artist, song, pos, datetime)]
            c.execute('INSERT INTO m_playlists (artist, song, playlist_position, playlist_date) VALUES (?,?,?,?)', x)
        conn.commit()
        c.close()
        
    def GetGenericResults(self, query):
        r_arr = []        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        #print query
        c.execute(query)
        h = c.fetchall()
        for x in h:
            r_arr.append(x)
        c.close()
        return r_arr
        
    def DeleteQuery(self, query):
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        c.close()
        
    def InsertPlaylistLabelData(self, p_label, p_date_time):
        # add feed url
        #check for existing
        #update record or creat new        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()        
        t = 'SELECT playlist_date FROM m_playlist_labels WHERE playlist_date="' + str(p_date_time) + '"'
        c.execute(t)
        h = c.fetchall()
        #print h
        if len(h) >= 1:                        
            c.execute('UPDATE m_playlist_labels SET playlist_label= "' + str(p_label) + '" WHERE playlist_date ="' + str(p_date_time) + '"')
            conn.commit()            
        else:
            c.execute('INSERT INTO m_playlist_labels (playlist_label, playlist_date) VALUES (?,?)', (p_label, p_date_time))
            conn.commit()
        c.close()
        
    def InsertPlayedData(self, track_id, played_type_id):
        # add feed url
        #check for existing
        #update record or creat new        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        c.execute('INSERT INTO m_played (played_type_id, track_id, played_date) VALUES ( ?, ?,datetime("now","localtime"))', (played_type_id, track_id))
        conn.commit()
        c.close()
            
#if (os.path.isfile(self.FILEDB)):
#    pass
#else:
# **********************************
#DbFuncs().create_tables()
# **********************************
#FillDb()

#After adding directories which contain your mp3 files to your song collection (may take some time depending on number of files), the directories will be monitored and updated as new mp3's are added.

import wx
import wx.xrc as xrc

SONGDB_RESFILE = SYSLOC + os.sep + 'layout_songdb.xml'

class SongDBWindow(wx.Dialog):
    """Song DB Window for adding songs"""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Song Collection Locations", size=(600, 400), pos=(10,10))#, style=wx.FRAME_SHAPED) #STAY_ON_TOP)#wx.FRAME_SHAPED)
        self.parent = parent
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(SONGDB_RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_song_db")

        # control references --------------------
        #self.st_songdb_total = xrc.XRCCTRL(self, 'm_st_songdb_total')
        #self.st_songdb_last = xrc.XRCCTRL(self, 'm_st_songdb_last')
        self.st_songdb_header = xrc.XRCCTRL(self, 'm_st_songdb_header')
        #self.bm_search_close = xrc.XRCCTRL(self, 'm_bm_search_close')
        #self.dp_songdb_dir = xrc.XRCCTRL(self, 'm_dp_songdb_dir')
        
        
        # bindings ----------------
        self.Bind(wx.EVT_BUTTON, self.OnAddClick, id=xrc.XRCID('m_bu_songdb_add'))
        #self.Bind(wx.EVT_BUTTON, self.OnSearchListClick, id=xrc.XRCID('m_bb_search_add'))
        #self.Bind(wx.EVT_BUTTON, self.OnSearchClear, id=xrc.XRCID('m_bb_search_clear'))
        #self.Bind(wx.EVT_TEXT_ENTER, self.OnSearchClick, self.tc_search_text)
        #self.bm_search_close.Bind(wx.EVT_LEFT_UP, self.hide_me)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_songdb_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_songdb_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_songdb_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_songdb_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
                
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        
    def OnGetItemText(self, item, col):
        return "Item %d, column %d" % (item, col)
        
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
# --------------------------------------------------------- 
    def OnAddClick(self, event):
        # show the window
        base_path = self.dp_songdb_dir.GetPath()
        
        maxlen = 150

        dlg = wx.ProgressDialog("Adding Songs", " ", maximum = maxlen, parent=self, style = wx.PD_CAN_ABORT) # | wx.PD_APP_MODAL)
        
        #THREAD
        current = FileThread(dlg, self.parent, self.dp_songdb_dir.GetPath(), maxlen)
        #THREAD
        current.start()
        #dlg.Update(count)                
        #dlg.Destroy()        

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
#================================================           
#EMULATE=0

#import pymedia.muxer as muxer, pymedia.audio.acodec as acodec, pymedia.audio.sound as sound
#import time

#class Player(object): 
#    def __init__(self):
#        self.local_play_status = True
#        self.paused = False
#        self.snd = None
                
#    def stop_play(self):
#        #self.stop()
#        self.local_play_status = False
#        if os.name != 'nt':
#            time.sleep(4)
        #self.stop()
            
#    def toggle_pause(self):
#        if self.snd:
#            if self.paused == False:
#                self.pause()
#            else:
#                self.unpause()
            
#    def pause(self):
#        """ Pause playing the current file """
 #       if self.snd.isPlaying():
  #          self.paused= True
   #         if self.snd:
    #            self.snd.pause()
                
#    def unpause(self):
 #       """ Resume playing the current file """
  #      if self.snd.isPlaying():
   #         if self.snd:
    #            self.snd.unpause()
     #   self.paused= False
  
#    def isPaused( self ):
 #       """ Returns whether playback is paused """
  #      return self.paused
   #     
#    def stop(self):
 #       """ Stop playing the current file """
  #      if self.snd.isPlaying():            
   #         if self.snd:
    #            self.snd.stop()
#
#    def play(self, name, card=0, rate=1, tt=-1):
 #   
 #       #dm= muxer.Demuxer( str.split( name, '.' )[ -1 ].lower() )
  #      dm= muxer.Demuxer( 'mp3' )
   #     snds= sound.getODevices()
    #    if card not in range( len( snds ) ):
     #       raise 'Cannot play sound to non existent device %d out of %d' % ( card+ 1, len( snds ) )
      #  f= open( name, 'rb' )
#        self.snd= resampler= dec= None
 #       s= f.read( 32000 )
  #      t= 0
   #     while (len( s )):
    #        #print self.local_play_status
     #       frames= dm.parse( s )
      #      if frames:
       #         for fr in frames:
        #        # Assume for now only audio streams
    #
     #               if dec== None:
      #                  #print dm.getHeaderInfo(), dm.streams
       #                 dec= acodec.Decoder( dm.streams[ fr[ 0 ] ] )
        #    
         #           r= dec.decode( fr[ 1 ] )
          #          if r and r.data:
           #             if self.snd== None:
            #                #print 'Opening sound with %d channels -> %s' % ( r.channels, snds[ card ][ 'name' ] )
             #               self.snd= sound.Output( int( r.sample_rate* rate ), r.channels, sound.AFMT_S16_LE, card )
                            #print r.channels
              #              if rate< 1 or rate> 1:
               #                 resampler= sound.Resampler( (r.sample_rate,r.channels), (int(r.sample_rate/rate),r.channels) )
                #                print 'Sound resampling %d->%d' % ( r.sample_rate, r.sample_rate/rate )
              
                 #       data= r.data
                  #      if resampler:
                   #         data= resampler.resample( data )
                    #    if EMULATE:
                     #       # Calc delay we should wait to emulate snd.play()
    #
     #                       d= len( data )/ float( r.sample_rate* r.channels* 2 )
      #                      time.sleep( d )
       #                     if int( t+d )!= int( t ):
        #                        print 'playing: %d sec\r' % ( t+d ),
         #                   t+= d
          #              else:
           #                 self.snd.play( data )
            #            #print snd.getPosition()
  #          if tt> 0:
   #             if self.snd and self.snd.getPosition()< tt:
    #                break

     #       s= f.read( 512 )
      #      if self.local_play_status == False:               
       #         break
                    
 #       while self.snd.isPlaying():
  #          time.sleep( 0.05 )

#====================================================
class VirtualList(wx.ListCtrl):
    def __init__(self):
        self.query_flag = True        
        p = wx.PreListCtrl()
        # the Create step is done by XRC.
        self.PostCreate(p)
        self.FILEDB = system_files.GetDirectories(None).DataDirectory() + os.sep + 'gravydb.sq3'
    
    def OnGetItemText(self, item, col):
        ritem = self.GetRow(item, col)
        while ritem == '':
            item = item + 1
            ritem = self.GetRow(item, col)
        return ritem
        
    def GetRow(self, row_num, column):
        # get row count
        row_num = row_num + 1
        ritem = ''
        if self.query_flag == True:            
            conn = sqlite3.connect(self.FILEDB)
            # for unicode/crazy text errors
            conn.text_factory = str
            c = conn.cursor()
            tq = "SELECT music_id, file_name, folder_name, folder_path FROM m_files WHERE music_id = " + str(row_num)            
            #tq = "SELECT music_id, file_name, folder_name, folder_path FROM m_files LIMIT 1 OFFSET " + str(row_num - 1)
            
            c.execute(tq)
            h = c.fetchall()
            for x in h:
                ritem = x[column]                
                #check for ''
                if (ritem == None) or (ritem == ''):
                    ritem = ' '
            c.close()
        else:            
            ritem = '1'
            #print row_num - 1
            #print len(self.res_arr)            
            if (row_num - 1) >= len(self.res_arr):
                #empty results on the ctrl will cause problems with us skipping holes in the id range
                #so make them spaces
                ritem = ' '
            else:
                ritem = self.res_arr[row_num - 1][column]
        return ritem
        
    def SetQuery(self, song, qtype):
        # change virtual list results to another user entered query                
        self.DeleteAllItems()
        if song == '':
            self.query_flag = True
            self.SetItemCount(DbFuncs().GetCountAndLast()[0])
        else:
            if qtype == 'file':
                self.res_arr = DbFuncs().GetResultsArray(song, 100, True)
                self.SetItemCount(len(self.res_arr))
            else:
                self.res_arr = DbFuncs().GetResultsArray(song, 100, True, 3)
                self.SetItemCount(len(self.res_arr))
            #print self.res_arr
            
            self.query_flag = False


        
        
# ####################################
class FileThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, parent, grand_parent, base_path, maxlen):
        Thread.__init__(self)
        self.parent = parent
        self.grand_parent = grand_parent
        self.base_path = base_path
        self.maxlen = maxlen
        self.FILEDB = system_files.GetDirectories(self.grand_parent).DataDirectory() + os.sep + 'gravydb.sq3'
                        
    def run(self):
        self.FillDb(self.base_path)

# ---------------------------------------------------------
    def FillDb(self, base_path):
        #basePath = 'E:\\Music\\Albums\\Albums_01'
        #basePath = 'E:\\Music'
            
        allfiles = []
        subfiles = []
        
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        counter = 1
        
        for root, dirs, files in os.walk(base_path):
            for f in files:
                if f.endswith('.mp3'):
                    #allfiles.append(os.path.join(root, f))
                    #path = os.path.join(root, f).replace(os.sep, '/')
                    path_n = root.rsplit(os.sep, 1)[0].replace(os.sep, '/')
                    folder_n = root.rsplit(os.sep, 1)[1]
                    file_n = f
                    c.execute('INSERT INTO m_files values (null,?,?,?)', (path_n, folder_n, file_n))
                    #CREATE TABLE m_files (file_id INTEGER PRIMARY KEY, folder_path TEXT, file_name TEXT, artist_name TEXT, song_name TEXT)
                    conn.commit()
                    #print file_n
                    self.parent.Update(counter, file_n)
                    #print path_n
                    #print folder_n
                    time.sleep(.05)
                    counter = counter + 1
                    if counter >= 90:
                        counter = 10
        c.close()
        self.grand_parent.lc_scol_col.SetItemCount(GetCountAndLast()[0])
        self.parent.Destroy()
        

#---------------------------------------------------------------------------
# ####################################
def GetMp3Length(file_name):
    c = mp3tag.Mp3AudioFile(file_name)    
    return int(c.getPlayTime())
    
def GetMp3Artist(file_name):
    c = mp3tag.Mp3AudioFile(file_name)
    a =''
    try:
        b = c.tag.getArtist()    
        a = ' '.join(i.capitalize() for i in b.split(' '))
    except AttributeError:
        pass
    return a
    
    
def GetMp3Title(file_name):
    c = mp3tag.Mp3AudioFile(file_name)
    a =''
    try:
        b = c.tag.getTitle()
        a = ' '.join(i.capitalize() for i in b.split(' '))
    except AttributeError:
        pass
    return a
    
def GetMp3Album(file_name):
    c = mp3tag.Mp3AudioFile(file_name)
    try:
        b = c.tag.getAlbum()
        a = ' '.join(i.capitalize() for i in b.split(' '))
    except AttributeError:
        a = ''
    return a
    
def SetMp3Album(file_name, album):
    c = mp3tag.Mp3AudioFile(file_name)
    try:    
        c.tag.setAlbum(album)
        c.tag.update()
    except AttributeError:
        print 'AttributeError'

    #try:
    #c.tag.setAlbum(album)
    #except e, error:
        #pass
    
    
 #---------------------------------------------------------------------------   
    
'''   
m_files
    music_id    
    folder_path
    folder_name
    file_name
    
m_tracks
    track_id
    grooveshark_id
    music_id
    track_time    
    tag_id
    artist
    song
    album
    album_art_file
    rating_type_id

m_pop
    pop_id
    track_id
    listeners
    playcount    

m_tag
    tag_id
    tag_label

m_playcount
    playcount_id
    track_id
    local_playcount
    last_play_date
'''
