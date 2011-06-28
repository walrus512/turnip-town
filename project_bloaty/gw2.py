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
#x.Start()
#xmlrpc server thread
server_thread = ServerThread()
server_thread.start()

hostname = socket.gethostname()
s = xmlrpclib.ServerProxy('http://' + hostname + ':7777')
#print s.pow(2,3)

# Print list of available methods
print s.system.listMethods()

x = playlist.Playlist()
print x.GetName()
x.AddSong({'artist':'Beck', 'title':'Sad Song'})
x.AddSong({'artist':'U2', 'title':'Gloria'})
print x.playlist
x.SetSongAttrib(0, 'rating', 0)
print x.playlist
print x.DeleteSong(1)
print x.playlist
x.InsertSong({'artist':'U2', 'title':'Lemon'}, 0)
print x.playlist
x.MoveSong(0, 1)
print x.playlist
print x.GetCount()
print x.GetCurrentNumber()
 
