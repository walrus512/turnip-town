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
import sys
import sqlite3
import time
import wx

from threading import Thread

from main_thirdp import eyeD3
from main_utils import system_files

SYSLOC = os.path.dirname(os.path.abspath(__file__))

class DbFuncs(object):
    def __init__(self):
        self.FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        self.CreateTables()
        self.UpdateTables()
       
    def CreateTables(self):
        # create the db if nescessary
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
        
    def UpdateTables(self):
        #make some table updates
        pass    
    
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
                #*** unicode errors/not used: filen = str(x[1]) + '/' + str(x[2])
                filen = ''
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
        q_rep = query.replace("'","").replace("!","").replace("?","").replace("&"," ").replace(",","").replace("-"," ")
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
        try:        
            h = c.fetchall()
        except Exception, expt:
            print "GetResultsArray: " + str(Exception)+str(expt)
            return r_arr
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
            c.execute('UPDATE m_tracks SET track_time= ?, tag_id= ?, artist= ?, song= ?, album= ?, album_art_file= ? WHERE track_id= ?', (str(p_track_time), str(p_tag_id), p_artist, p_song, p_album, p_album_art_file, str(g_track_id)))
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
        
    def GetOnlyTrackId(self, artist, song):
        conn = sqlite3.connect(self.FILEDB)
        c = conn.cursor()
        t = 'SELECT track_id FROM m_tracks WHERE artist="' + artist + '" AND song="' + song + '"'
        c.execute(t)
        h = c.fetchall()
        #print t
        g_track_id = False
        if len(h) >= 1:
            g_track_id = h[0][0]
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
            c.execute("INSERT INTO m_tag (tag_label) VALUES (?)", (p_tag_label,))
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
            c.execute("UPDATE m_pop SET track_id= ?, listeners= ?, playcount= ? WHERE pop_id = ?", (p_track_id, p_listeners, p_playcount, g_pop_id))
            conn.commit()
        else:
            c.execute("INSERT INTO m_pop (track_id, listeners, playcount) VALUES (?,?,?)", (p_track_id, p_listeners, p_playcount))
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
            c.execute('UPDATE m_playcount SET track_id= ?, local_playcount= ?, last_play_date=datetime("now","localtime") WHERE playcount_id = ?',  (p_track_id, g_local_playcount, g_playcount_id))
            conn.commit()
        else:
            c.execute('INSERT INTO m_playcount (track_id, local_playcount, last_play_date) VALUES (?, 1, datetime("now","localtime"))', (p_track_id,))
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
            c.execute("UPDATE m_rating SET rating_type_id= ? WHERE track_id = ?", (p_rating_id, p_track_id))
            conn.commit()
        else:
            c.execute('INSERT INTO m_rating (track_id, rating_type_id) VALUES (?,?)', (p_track_id, p_rating_id))
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
            c.execute("INSERT INTO m_feeds (feed_url) VALUES (?)", (p_feed_url,))
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
            c.execute("UPDATE m_playlist_labels SET playlist_label= ? WHERE playlist_date = ?", (p_label, str(p_date_time)))
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

#====================================================
class VirtualList(wx.ListCtrl):
    def __init__(self):
        self.query_flag = True        
        p = wx.PreListCtrl()
        # the Create step is done by XRC.
        self.PostCreate(p)
        self.FILEDB = system_files.GetDirectories(None).DatabaseLocation()
    
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
            c = conn.cursor()
            #conn.text_factory = str
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

#---------------------------------------------------------------------------
# ####################################
def GetMp3Length(file_name):
    #try:
    c = eyeD3.tag.Mp3AudioFile(file_name)
    return int(c.getPlayTime())
    #except Exception, expt:
    #    print "local_songs: GetMp3Length: " + str(Exception)+str(expt)
    #    return (240)
    
    
def GetMp3Artist(file_name):
    c = eyeD3.tag.Mp3AudioFile(file_name)
    a =''
    try:
        b = c.tag.getArtist()    
        a = ' '.join(i.capitalize() for i in b.split(' '))
    except AttributeError:
        pass
    return a
    
    
def GetMp3Title(file_name):
    #print file_name
    c = eyeD3.tag.Mp3AudioFile(file_name)
    a =''
    try:
    	b = c.tag.getTitle()
    	a = ' '.join(i.capitalize() for i in b.split(' '))
    except AttributeError:
    	print str(AttributeError)
    #    pass
    return a
    
def GetMp3Album(file_name):
    c = eyeD3.tag.Mp3AudioFile(file_name)
    try:
        b = c.tag.getAlbum()
        a = ' '.join(i.capitalize() for i in b.split(' '))
    except AttributeError:
        a = ''
    return a
    
def SetMp3Album(file_name, album):
    c = eyeD3.tag.Mp3AudioFile(file_name)
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
