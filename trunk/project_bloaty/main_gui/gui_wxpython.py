RESFILE = './main_gui/test2.xrc'

import wx
import wx.xrc as xrc

from main_server import xmlrpc_client

class MainFrame(wx.Frame): 
    def __init__(self): 
        wx.Frame.__init__(self, None, -1, 'zoop', size=(600, 330), pos=(200,200), style=wx.CAPTION|wx.CLOSE_BOX|wx.SYSTEM_MENU)#wx.DEFAULT_FRAME_STYLE|wx.WANTS_CHARS) #^(wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)) #, style=wx.STAY_ON_TOP) 
        pass

class MainPanel(wx.Panel):
    def __init__(self, parent, resfile=RESFILE):
        wx.Panel.__init__(self, parent, -1)
        
        self.parent = parent
        
        # xml-rpc client
        xmlrpc = xmlrpc_client.Client()
        self.cl = xmlrpc.client
        xmlrpc.ListMethods()
        
        
        # xrc gui layout ------------------
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)
        self.panel = res.LoadPanel(self, "m_pa_main")
        
        self.lc_playlist = xrc.XRCCTRL(self,'m_listCtrl1')
        
        self.Bind(wx.EVT_BUTTON, self.OnButtonOne, id=xrc.XRCID("m_button1"))
        self.Bind(wx.EVT_BUTTON, self.OnButtonTwo, id=xrc.XRCID("m_button2"))
        self.Bind(wx.EVT_BUTTON, self.OnButtonThree, id=xrc.XRCID("m_button3"))
        self.Bind(wx.EVT_BUTTON, self.OnLoadClick, id=xrc.XRCID("m_button4"))
        
        # and do the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL, 0)        
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        self.Layout()
       
    # playback ---------------------------    
    def OnButtonOne(self, event):
        self.cl.AddItem({'Artist':'Beck', 'Title':'Sad Song', 'Location':'Y:/1.mp3'})
        self.cl.AddItem({'Artist':'U2', 'Title':'Gloria', 'Location':'Y:/1.mp3', 'Fun':'yup'})
        print self.cl.PrintPlaylist()
    
    def OnButtonTwo(self, event):
        backends = self.cl.GetBackendList()
        print self.cl.GetBackendList()
        self.cl.SetBackend(backends[0])
        backend = self.cl.GetBackend()
        self.cl.PlayWith(backend, 'Y:/1.mp3')
        
    def OnButtonThree(self, event):
        backends = self.cl.GetBackendList()
        print self.cl.GetBackendList()
        self.cl.SetBackend(backends[0])
        backend = self.cl.GetBackend()
        self.cl.Stop()
        
    #playlist -----------------------------
    def OnLoadClick(self, event):
        self.PopulatePlaylist()
    
    def PopulatePlaylist(self):
        #load a plalist
        x = self.cl.GetPlaylist()
        #print x
        #print x[0]
        column_list = []
        for gg in range (0, self.lc_playlist.GetColumnCount()): 
            column_list.append(self.lc_playlist.GetColumn(gg).GetText())        
        
        counter = 1
        for dict in x:
            for key in dict.keys():
                if key not in column_list:
                    column_list.append(key)
                    c = self.lc_playlist.InsertColumn(wx.NewId(), key)                    
            #print self.lc_playlist.GetColumnCount()
            #print self.lc_playlist.GetColumn(1).GetText()            
            index = self.lc_playlist.InsertStringItem(counter - 1, '')            
            for kk in range (0, self.lc_playlist.GetColumnCount()):
                try:                    
                    self.lc_playlist.SetStringItem(counter - 1, kk, dict[self.lc_playlist.GetColumn(kk).GetText()])
                except Exception, expt:
                    print 'lp: ' + str(Exception) + str(expt)
            
            counter += 1
        
           # self.lc_playlist.SetColumnWidth(c, 60)            

        
def LoadGui(resfile=RESFILE):
    app = wx.App()
    frame = MainFrame()
    panel = MainPanel(frame, resfile)
    frame.Show(True)    
    app.MainLoop()
    return ((app, frame, panel))

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    panel = MainPanel(frame)
    frame.Show(True)
    
    app.MainLoop()