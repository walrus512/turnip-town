# -*- coding: utf-8 -*-
"""
GrooveWalrus: Pyro Server
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
        
import Pyro.core
from threading import Thread
from wx.lib.pubsub import Publisher as pub

class PyroResponse(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
    def MessageAction(self, message):
        #print message
        pub.sendMessage('main.pyro', {'sysarg': message})

def StartPyro():
    #THREAD
    current = ServerThread()                
    current.start()


# ---------------------------------------------------------
class ServerThread(Thread): 
    """ Loads a pyro server """
    def __init__(self):
        Thread.__init__(self)
                        
    def run(self):
        Pyro.core.initServer()
        daemon=Pyro.core.Daemon()
        uri=daemon.connect(PyroResponse(),"groovewalrus")
    
        print "The daemon runs on port:",daemon.port
        print "The object's uri is:",uri
    
        daemon.requestLoop()
        
#------------------------------------------------------------
def SendPyro(message=None):
    # you have to change the URI below to match your own host/port.
    pysvr = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/groovewalrus")
    pysvr.MessageAction(message)

