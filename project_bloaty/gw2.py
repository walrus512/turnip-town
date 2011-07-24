#gw2.py

#import xmlrpclib
#import socket

from main_server import xmlrpc_server

#from main_objects import playlist
#from main_objects import song
import megasaurus

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

#temp
import time

x = megasaurus.Megasaurus()

# xml-rpc server ------------------

server_thread = ServerThread()
server_thread.start()
#server_thread.server.RegisterFunction(playlist.MakePlaylist, 'MakePlaylist')
#server_thread.server.RegisterFunction(playlist.adder_function, 'add')
server_thread.server.RegisterInstance(x)
#server_thread.server.RegisterInstance(y)


# xml-rpc client

###hostname = socket.gethostname()
###s = xmlrpclib.ServerProxy('http://' + hostname + ':7777')
#print s.pow(2,3)

# Print list of available methods
###print s.system.listMethods()


###print s.GetName()
###s.AddItem({'artist':'Beck', 'title':'Sad Song', 'location':'Y:/1.mp3'})
###s.AddItem({'artist':'U2', 'title':'Gloria', 'location':'Y:/1.mp3'})
#print s.playlist
#x.SetItemAttrib(0, 'rating', 0)
#print x.playlist
#print x.DeleteItem(1)
#print x.playlist
#x.InsertItem({'artist':'U2', 'title':'Lemon'}, 0)
#print x.playlist
#x.MoveItem(0, 1)
#print x.playlist
#print x.GetCount()
#print x.GetCurrentNumber()
###print s.GetCount()
###print s.PrintPlaylist()
###backends = s.GetBackendList()
###print s.GetBackendList()
###s.SetBackend(backends[0])
###backend = s.GetBackend()
#print player
###s.PlayWith(backend, 'Y:/1.mp3')
#time.sleep(4)
#s.Stop()

from main_gui import gui_wxpython

main_gui = gui_wxpython.LoadGui()
