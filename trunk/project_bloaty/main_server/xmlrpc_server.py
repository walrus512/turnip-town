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
                                    requestHandler=RequestHandler)
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

if __name__ == "__main__":
    x = Server()
    x.Start()
    x.Stop()