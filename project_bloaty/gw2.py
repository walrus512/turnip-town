#gw2.py

import xmlrpclib
import socket
from main_server import xmlrpc_server

from main_objects import playlist
from main_objects import song

import threading

class ServerThread(threading.Thread):
    def __init__(self):
        self.server = xmlrpc_server.Server()
        threading.Thread.__init__(self)
 
    def run(self):
        self.server.Start()        


#p = subprocess.Popen('./main_server/xmlrpc_server.py')
#x = xmlrpc_server.Server()
#playlist.Start()
#xmlrpc server thread
server_thread = ServerThread()
server_thread.start()
server = server_thread.server.GetServer()

print server

# Register a function under a different name
#def adder_function(x,y):
#    return x + y
#server.register_function(adder_function, 'add')

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'div').
#class MyFuncs:
#    def div(self, x, y):
#        return x // y
#server.register_instance(MyFuncs())

# Register a playlist
playlist = playlist.Playlist()
print dir(playlist)
# register functions
for meth in dir(playlist):
    if meth.startswith('__'):
        break
    server.register_function(meth, meth)
#playlist.song = song.Song()
#server.register_instance(playlist)

#song = song.Song()
#server.register_instance(song)






hostname = socket.gethostname()
s = xmlrpclib.ServerProxy('http://' + hostname + ':7777')
#print s.pow(2,3)

# Print list of available methods
print s.system.listMethods()


#print playlist.GetName()
#playlist.AddItem({'artist':'Beck', 'title':'Sad Song'})
#playlist.AddItem({'artist':'U2', 'title':'Gloria'})
#print playlist.playlist
#playlist.SetItemAttrib(0, 'rating', 0)
#print playlist.playlist
#print playlist.DeleteItem(1)
#print playlist.playlist
#playlist.InsertItem({'artist':'U2', 'title':'Lemon'}, 0)
#print playlist.playlist
#playlist.MoveItem(0, 1)
#print playlist.playlist
#print playlist.GetCount()
 
