# -*- coding: utf-8 -*-
"""
GrooveWalrus: Options
Copyright (C) 2012
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

import sqlite3

def GetSetting(setting_name, file_db):
    #get a value from the settings table
    conn = sqlite3.connect(file_db)
    c = conn.cursor()
    tq = "SELECT setting_value FROM m_settings WHERE setting_name = '%s'" % setting_name
    c.execute(tq)
    h = c.fetchall()
    if len(h) == 1:
        return (h[0][0])
    else:
        return False

def SetSetting(setting_name, setting_value, file_db):
    #set a value from the settings table        
    conn = sqlite3.connect(file_db)
    c = conn.cursor()    
    t = 'SELECT setting_id FROM m_settings WHERE setting_name= "%s"' % setting_name
    c.execute(t)
    h = c.fetchall()
    #print h
    if len(h) >= 1:
        g_setting_id = h[0][0]        
        c.execute('UPDATE m_settings SET setting_value="%s" WHERE setting_id =%i' % (setting_value, g_setting_id))
        conn.commit()
    else:
        c.execute('INSERT INTO m_settings (setting_name, setting_value) values (?,?)', (setting_name, setting_value))
        conn.commit()
    c.close()

def GetAllSettings(file_db):
    #get a value from the settings table
    conn = sqlite3.connect(file_db)
    c = conn.cursor()
    tq = "SELECT * FROM m_settings"
    c.execute(tq)
    h = c.fetchall()
    if len(h) >= 1:
        return h
    else:
        return False