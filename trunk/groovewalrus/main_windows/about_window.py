"""
GrooveWalrus: About Window 
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

def ShowAbout(program_name, program_version):
    """ An about window, radical! """
    # First we create and fill the info object
    info = wx.AboutDialogInfo()
    info.Name = program_name
    info.Version = program_version
    info.Copyright = "(c) 1906 - 2018"
    info.Description = """
Products Used
==========
Groove Shark - http://grooveshark.com
Last.fm - http://last.fm
Music Brainz - http://musicbrainz.org
---
Python - http://www.python.org
wxpython - http://www.wxpython.org
wxFormBuilder - http://wxformbuilder.org
py2exe - http://www.py2exe.org
---
pyMedia - http://pymedia.org
Kaa Metadata - http://doc.freevo.org/2.0/Kaa
EventGhost - http://sourceforge.net/projects/eventghost/
GrooveShark.py - Zimmmer: http://hak5.org
GrooveShark PyApi - http://github.com/Tim-Smart/grooveshack     
PyLast.py - http://code.google.com/p/pylast/
---
Tango Icons - http://tango.freedesktop.org
"Walrus" Photo - http://picasaweb.google.com/dschmitz   
"Gw" Icon - http://tinylab.deviantart.com/
"""
    info.WebSite = ("http://groove-walrus.turnip-town.net", "http://groove-walrus.turnip-town.net")

    # Then we call wx.AboutBox giving it that info object
    wx.AboutBox(info)