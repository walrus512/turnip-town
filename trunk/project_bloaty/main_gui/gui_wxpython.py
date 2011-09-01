RESFILE = './main_gui/wxpython/layout_main.xrc'
RESFILE_TB = './main_gui/wxpython/m_tb_main.xrc'
RESFILE_PA = './main_gui/wxpython/m_pa_pages.xrc'

import wx
import wx.xrc as xrc
import wx.aui
import wx.lib.agw.ribbon as RB

from main_server import xmlrpc_client

class MainFrame(wx.Frame): 
    def __init__(self): 
        wx.Frame.__init__(self, None, -1, 'zoop', size=(600, 530), pos=(200,200), style=wx.CAPTION|wx.CLOSE_BOX|wx.SYSTEM_MENU)#wx.DEFAULT_FRAME_STYLE|wx.WANTS_CHARS) #^(wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)) #, style=wx.STAY_ON_TOP) 
        
        # tell FrameManager to manage this frame        
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.SetMinSize(wx.Size(500, 400))
        
        # xrc gui layout ------------------
        # XML Resources can be loaded from a file like this:
        res1 = xrc.XmlResource(RESFILE_TB)
        self.m_tb_main = res1.LoadToolBar(self, "m_tb_main")
        self.m_tb_main.Realize()
        
        #tell the frame to not manage teh toolbar, aui manager will instead
        self.SetToolBar(None)
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE_PA)
        self.m_pa_pages = res.LoadPanel(self, "m_pa_pages")
        
        self.pa_ribbon = xrc.XRCCTRL(self,'m_pa_ribbon')
        self.lc_playlist = xrc.XRCCTRL(self,'m_lc_playlist')
        
        # ribbon bar
        self._ribbon = RB.RibbonBar(self.pa_ribbon, wx.ID_ANY)
        dummy_3 = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Playlist") #, CreateBitmap("empty"))
        dummy_4 = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Last.fm") #, CreateBitmap("empty"))
        dummy_5 = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Favorites") #, CreateBitmap("empty"))
        self._ribbon.Realize()
        bgcolour = self.pa_ribbon.GetBackgroundColour()
        self._ribbon.GetArtProvider().SetColourScheme(bgcolour, 0, 1)
        
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self._ribbon, 1, wx.EXPAND)
        self.pa_ribbon.SetSizer(s)
        self.pa_ribbon.SetMinSize((400,120))
        

        # add a bunch of panes
        self._mgr.AddPane(self.m_pa_pages, wx.aui.AuiPaneInfo().Name("MainPanel").
                          CenterPane())
        
        self._mgr.AddPane(self.m_tb_main, wx.aui.AuiPaneInfo().
                          Name("Playback").Caption("Playback Toolbar").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))

        
        #self._mgr.AddPane(self.m_pa_pages, wx.aui.AuiPaneInfo().
        #                  Name("Playlist").Caption("Playlist").Top().
        #                  CloseButton(True).MaximizeButton(True))
                          
                          
        #self._mgr.AddPane(self._ribbon, wx.aui.AuiPaneInfo().
        #                  Name("Ribbon").Top().
        #                  CloseButton(True).MaximizeButton(True))
                                                
        # "commit" all changes made to FrameManager   
        self._mgr.Update()
        

#class MainPanel(wx.Panel):
#    def __init__(self, parent, resfile=RESFILE):
#        wx.Panel.__init__(self, parent, -1)
        
#        self.parent = parent
        
        # xml-rpc client
        xmlrpc = xmlrpc_client.Client()
        self.cl = xmlrpc.client
        xmlrpc.ListMethods()
        
        
        # xrc gui layout ------------------
        # XML Resources can be loaded from a file like this:
#        res = xrc.XmlResource(RESFILE)
#        self.panel = res.LoadPanel(self, "m_pa_main")
        
#        self.lc_playlist = xrc.XRCCTRL(self,'m_lc_playlist')
        
        self.Bind(wx.EVT_TOOL, self.OnPlayClick, id=xrc.XRCID("m_tl_play"))
        self.Bind(wx.EVT_TOOL, self.OnStopClick, id=xrc.XRCID("m_tl_stop"))
        #self.Bind(wx.EVT_BUTTON, self.OnButtonThree, id=xrc.XRCID("m_button3"))
        #self.Bind(wx.EVT_BUTTON, self.OnLoadClick, id=xrc.XRCID("m_button4"))
        
        # and do the layout
#        sizer = wx.BoxSizer(wx.VERTICAL)
#        sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL, 0)        
#        self.SetSizer(sizer)
#        self.SetAutoLayout(True)
        
#        self.Layout()
       

        self.cl.AddItem({'Artist':'Beck', 'Title':'Sad Song', 'Location':'Y:/1.mp3'})
        self.cl.AddItem({'Artist':'U2', 'Title':'Gloria', 'Location':'Y:/1.mp3', 'Fun':'yup'})
        print self.cl.PrintPlaylist()
        
        self.PopulatePlaylist()
    
    def OnPlayClick(self, event):
        backends = self.cl.GetBackendList()
        print self.cl.GetBackendList()
        self.cl.SetBackend(backends[0])
        backend = self.cl.GetBackend()
        self.cl.PlayWith(backend, 'Y:/1.mp3')
        
    def OnStopClick(self, event):
        backends = self.cl.GetBackendList()
        print self.cl.GetBackendList()
        self.cl.SetBackend(backends[0])
        backend = self.cl.GetBackend()
        self.cl.Stop()
        
    #playlist -----------------------------
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
    ###panel = MainPanel(frame, resfile)
    panel = None
    frame.Show(True)    
    app.MainLoop()
    return ((app, frame, panel))

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    panel = MainPanel(frame)
    frame.Show(True)
    
    app.MainLoop()