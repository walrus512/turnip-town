# -*- coding: utf-8 -*-
"""
GrooveWalrus: xmlrpc client
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

import xmlrpclib
import socket

class Client:
    """It's a client"""
    #----------------------------------------------------------------------
    def __init__(self, port=7777):

        hostname = socket.gethostname()
        self.client = xmlrpclib.ServerProxy('http://' + hostname + ':7777')        

    def ListMethods(self):
        # Print list of available methods
        print self.client.system.listMethods()
        return self.client.system.listMethods()

