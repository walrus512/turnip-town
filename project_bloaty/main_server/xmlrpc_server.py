# -*- coding: utf-8 -*-
"""
GrooveWalrus: xmlrpc server
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



from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import socket


class RequestHandler(SimpleXMLRPCRequestHandler):
# Restrict to a particular path.
    rpc_paths = ('/RPC2',)

class Server:
    """It's a server"""
    #----------------------------------------------------------------------
    def __init__(self, port=7777):
    
        # Create server
        hostname = socket.gethostname()
        self.server = SimpleXMLRPCServer((hostname, port),
                                    requestHandler=RequestHandler, allow_none=True)
        self.server.register_introspection_functions()
        
        self.server.register_function(self.StopServer, 'shutdown')

    # Register pow() function; this will use the value of
    # pow.__name__ as the name, which is just 'pow'.
    #server.register_function(pow)

    # Register a function under a different name
    #def adder_function(x,y):
        #return x + y
    

    # Register an instance; all the methods of the instance are
    # published as XML-RPC methods (in this case, just 'div').
   # class MyFuncs:
     #   def div(self, x, y):
      #      return x // y

    #server.register_instance(MyFuncs())
    def Start(self):
        # Run the server's main loop
        print 'start'
        self.server.serve_forever()
        
    def StopServer(self):
        # Run the server's main loop
        print 'stop'
        self.server.shutdown()
        
    def GetServer(self):
        return self.server
    
    def RegisterFunction(self, function, function_name):
        self.server.register_function(function, function_name)
        
    def RegisterInstance(self, instance):
        self.server.register_instance(instance)

if __name__ == "__main__":
    x = Server()
    x.Start()
    x.Stop()