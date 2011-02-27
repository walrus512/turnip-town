"""
GrooveWalrus: Version Check and Update
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
import xml.etree.ElementTree as ET
import urllib
from main_utils import read_write_xml
import os, sys

VERSION_URL = "http://groove-walrus.turnip-town.net/dru/version/version5.xml"

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())


class VersionCheck():
    def __init__(self, parent, current_version):
        self.parent = parent
        self.current_version = current_version
    
    def CheckVersion(self):
        tree =''
    	try:
        	url_blob = urllib.urlopen(VERSION_URL + '?' + self.current_version)
        	tree = read_write_xml.xml_utils().read_xml_tree(url_blob)
       	except Exception, inst:
       	     print 'Exception: version check: ' + str(inst)
        
        if tree != '':
            root = tree.getroot()            
            # check if remote version number is greater than local version, yes than update icon
            if ( float(root.text) > float(self.current_version) ):
                # display update icon and link
                self.parent.bb_update.Show(True)
                #self.parent.hl_update.Show(True)
