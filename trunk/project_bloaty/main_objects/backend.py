# -*- coding: utf-8 -*-
"""
GrooveWalrus: backend
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

#loads a backend
import sys

########################################################################
class Backend:
    """Loads a backend for playback. eg. pymedia, MPlayer, ..."""
    #----------------------------------------------------------------------
    def __init__(self):
        self.backend = ''
        self.platform = sys.platform
        
    #----------------------------------------------------------------------
        
    def GetBackendList(self):
        #returns a list of backends, and it's supported platform
        backend_list = []
        if sys.platform == 'win32':
            import backends.win32
            backend_list = backends.win32.backend_list
        return backend_list
        
    def SetBackend(self, backend):
        #try to load a specific backend
        try:
            exec "import %s as player" % backend
            self.backend = backend
            return player.Player()
        except Exception, expt:
            print str(Exception)+str(expt)        

    def GetBackend(self):
        print self.backend
        return self.backend

if __name__ == "__main__":       
    x = Backend()
    print x.GetBackendList()
    x.SetBackend('backends.win32.player_pymedia')
    