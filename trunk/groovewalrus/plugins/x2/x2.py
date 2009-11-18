"""
GrooveWalrus: X2 Music Browsing Plug-in 
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

import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

from matplotlib.widgets import Lasso
from matplotlib.nxutils import points_inside_poly
from matplotlib.collections import RegularPolyCollection
from numpy import nonzero

import numpy as np
import sqlite3

import wx
import wx.xrc as xrc

from plugins.x2 import pca_module

RESFILE = "\\.\\plugins\\x2\\layout_x2.xml"

FEATURES_ARRAY = ['track_time','playcount','listeners','local_playcount'
#,'eq1',
#                    'eq2','eq3','eq4','eq5','eq6','eq7','eq8','eq9',
#                    'eq10','genre'
                    ]



class GraphFrame(wx.Frame):
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, 'X2', size=(650,600))

class MainPanel(wx.Dialog):
    def __init__(self, parent):#, main_playlist, nb_playlist):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.parent = parent
        self.nb_playlist = 0
        self.main_playlist = self.parent.lc_playlist
        
        #self.super_parent = super_parent
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)
        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_x2main")
        
        #self.panel = panel
        #background = 'tulips.jpg'
        #img = wx.Image(background, wx.BITMAP_TYPE_ANY)
        #self.buffer = wx.BitmapFromImage(img)
        #dc = wx.BufferedDC(wx.ClientDC(panel), self.buffer)           
        #self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        
        # control references --------------------
        self.pa_x2main = xrc.XRCCTRL(self, 'm_pa_x2main')
        self.pa_x2_graph = xrc.XRCCTRL(self, 'm_pa_x2_graph')   
        self.lc_x2_plist = xrc.XRCCTRL(self, 'm_lc_x2_plist')
        self.cl_x2_features = xrc.XRCCTRL(self, 'm_cl_x2_features')
        self.sl_x2_pointsize = xrc.XRCCTRL(self, 'm_sl_x2_pointsize')
        self.lc_x2_plist.InsertColumn(0,"Artist")
        self.lc_x2_plist.InsertColumn(1,"Song")
        self.lc_x2_plist.SetColumnWidth(0, 100)
        self.lc_x2_plist.SetColumnWidth(1, 100)        
        
        self.Bind(wx.EVT_BUTTON, self.OnAutoGenerateX2Playist, id=xrc.XRCID('m_bu_x2_plize'))
        self.Bind(wx.EVT_BUTTON, self.OnCenterClick, id=xrc.XRCID('m_bu_x2_center'))
        self.Bind(wx.EVT_SLIDER, self.OnPointSizeClick, id=xrc.XRCID('m_sl_x2_pointsize'))
        self.Bind(wx.EVT_SPIN, self.OnZoomClick, id=xrc.XRCID('m_sb_x2_zoom'))
        self.Bind(wx.EVT_SPIN, self.OnPanXClick, id=xrc.XRCID('m_sb_x2_panx'))
        self.Bind(wx.EVT_SPIN, self.OnPanYClick, id=xrc.XRCID('m_sb_x2_pany'))        
        self.Bind(wx.EVT_CHECKBOX, self.OnXAxisClick, id=xrc.XRCID('m_cb_x2_xlog'))
        self.Bind(wx.EVT_CHECKBOX, self.OnYAxisClick, id=xrc.XRCID('m_cb_x2_ylog'))
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheckListBox, self.cl_x2_features)
                
        self.current_zoom = 0
        self.current_panx = 0
        self.current_pany = 0
        
        #features array

        #tag_array = GetTags()
        self.cl_x2_features.Set(FEATURES_ARRAY)
        #self.cl_x2_features.AppendItems(tag_array)
        
        self.figure = Figure(None, None, (1,1,1), None, 1.0, True, None)#facecolor=0.75, edgecolor='white')
        #(figsize=None, dpi=None, facecolor=None, edgecolor=None, linewidth=1.0, frameon=True, subplotpars=None)
        self.MakeScatt([0,1,2,3])
        self.build_graph()
        self.build_collection()
        self.canvas = FigureCanvas(self.pa_x2_graph, -1, self.figure)
        
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        #self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        #self.canvas.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.canvas.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        
        # Note that event is a MplEvent
        #self.canvas.mpl_connect('motion_notify_event', self.OnMouseMotion)
        #self.canvas.Bind(wx.EVT_ENTER_WINDOW, self.ChangeCursor)

        #lasso
        self.mpl = self.canvas.mpl_connect('button_press_event', self.onpress)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.pa_x2main, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)                
        self.Fit()

# -----------------------------------------
# -----------------------------------------
    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self.panel, self.buffer)
        
    def ChangeCursor(self, curtype):
        self.canvas.SetCursor(wx.StockCursor(curtype))

    def OnMouseRightDown(self, evt):
        self.canvas.mpl_disconnect(self.mpl)
        self.canvas.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.ChangeCursor(wx.CURSOR_HAND)
        self.Refresh()
        self.oldx = evt.GetPosition()[0]
        self.oldy = evt.GetPosition()[1]
        #self.wPos = self.ClientToScreen((0,0))
        self.CaptureMouse()
        #print 'right-down'

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.RightIsDown():
            dPos = evt.GetPosition() #evt.GetEventObject().ClientToScreen(evt.GetPosition())
            #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
            #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
            #print(nPos)
            #print self.ldPos
            
            curx = dPos[0]
            cury = dPos[1]
            x = self.axes.get_xaxis()
            y = self.axes.get_yaxis()
            if (curx - self.oldx) < -10:
                x.pan(.5)
                self.oldx = curx
            if (curx - self.oldx) > 10:
                x.pan(-.5)
                self.oldx = curx
            if (cury - self.oldy) > 10:
                y.pan(.5)
                self.oldy = cury
            if (cury - self.oldy) < -10:
                y.pan(-.5)
                self.oldy = cury            
            
            self.canvas.draw()
            

    def OnMouseRightUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass
        self.ChangeCursor(wx.CURSOR_DEFAULT)
        self.canvas.Unbind(wx.EVT_MOTION)
        self.Unbind(wx.EVT_MOTION)
        self.mpl = self.canvas.mpl_connect('button_press_event', self.onpress)
            
    def UpdateStatusBar(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.statusBar.SetStatusText(( "x= " + str(x) + "  y=" +str(y) ), 0)

    def OnPointSizeClick(self, event):
        self.point_size = self.sl_x2_pointsize.GetValue() + 50 # range 50 to 300
        self.figure.clear()        
        self.build_graph()
        self.build_collection()
        self.canvas.draw()
        
    def OnCenterClick(self, event):        
        self.figure.clear()        
        self.build_graph()
        self.build_collection()
        self.canvas.draw()
        
    def OnZoomClick(self, event=None):
        x = self.axes.get_xaxis()
        y = self.axes.get_yaxis()
        if event.GetPosition() > self.current_zoom:
            x.zoom(1)
            y.zoom(1)
        else:
            x.zoom(-1)
            y.zoom(-1)
        self.current_zoom = event.GetPosition()
        self.canvas.draw()
        
    def OnMouseWheel(self, evt):
        rotation = evt.GetWheelRotation()
        x = self.axes.get_xaxis()
        y = self.axes.get_yaxis()
        if rotation > 0:
            x.zoom(1)
            y.zoom(1)
        else:
            x.zoom(-1)
            y.zoom(-1)
        self.canvas.draw()
        # Done handling event
        #evt.Skip()
        
    def OnPanXClick(self, event):
        x = self.axes.get_xaxis()
        y = self.axes.get_yaxis()
        if event.GetPosition() > self.current_panx:
            x.pan(1)
        else:
            x.pan(-1)
        self.current_panx = event.GetPosition()
        self.canvas.draw()
        
    def OnPanYClick(self, event):
        x = self.axes.get_xaxis()
        y = self.axes.get_yaxis()
        if event.GetPosition() > self.current_pany:
            y.pan(1)
        else:
            y.pan(-1)
        self.current_pany = event.GetPosition()
        self.canvas.draw()
        
    def OnXAxisClick(self, event):
        if self.axes.get_xscale() == 'log':
            self.axes.set_xscale('linear')
        else:        
            self.axes.set_xscale('log')
        #self.axes.autoscale_view()
        #self.canvas.draw_idle()
        #self.axes.autoscale_view()
        self.canvas.draw()
        #self.canvas.Refresh(eraseBackground=False)
        
    def OnYAxisClick(self, event):
        if self.axes.get_yscale() == 'log':
            self.axes.set_yscale('linear')            
        else:        
            self.axes.set_yscale('log')
        #self.axes.autoscale_view()        
        self.canvas.draw()
        
# ----------------------------------------------------------
    def OnCheckListBox(self, event):
        index = event.GetSelection()
        label = self.cl_x2_features.GetString(index)
        #print label
        #print index
        self.cl_x2_features.SetSelection(index)    # so that (un)checking also selects (moves the highlight)
        #print self.cl_x2_features.GetCount()
        selected_array =[]
        for x in range(0, self.cl_x2_features.GetCount()):
            if self.cl_x2_features.IsChecked(x) == True:
                selected_array.append(x)
        print selected_array
        if len(selected_array) >= 1:
            #print 'fofofofof'            
            self.figure.clear()
            self.MakeScatt(selected_array)
            self.build_graph()
            self.build_collection()            
            self.canvas.draw()

# ----------------------------------------------------------
# ----------------------------------------------------------

    def MakeScatt(self, selected_array): 
    
        pre_data_array, self.song_array, self.color_array, use_std = GetResultsArray(selected_array)
        #print pre_data_array
        pca1, pca2, pca3 = pca_module.PCA_svd(pre_data_array, use_std)
        #print self.data_array
        #print pca1
        #self.data = pca1
        #print pca2
        #grab the first 2 components
        self.data_array = np.array_split(pca1,[2,],axis=1)[0]
        #print self.data_array
        
        #self.axes.set_xlabel(r'$\Delta_i$', fontsize=20)
        #self.axes.set_ylabel(r'$\Delta_{i+1}$', fontsize=20)
        #self.axes.set_title('Volume and percent change')
        #self.axes.grid(True)
        ### use zoom instead
        #self.xmin = self.data1.min()# - (self.data1.max() * 0.1)
        #self.xmax = self.data1.max()# * 1.1
        #self.ymin = self.data2.min()# - (self.data2.max() * 0.1)
        #self.ymax = self.data2.max()# * 1.1

        
    def build_graph(self):

        self.axes = self.figure.add_subplot(111, axisbg=(1,1,1))
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        #self.axes.frame_on(False)
        #subplot(111, axisbg='darkslategray')
        #ax = fig.add_subplot(111)
        #self.axes.scatter(self.data2, self.data1, c=[0.5,0.5,1.0], s=200, alpha=0.5)
        
    def build_collection(self):
        self.point_size = self.sl_x2_pointsize.GetValue() + 50 # range 50 to 300
        self.collection = RegularPolyCollection(
            #self.axes.figure.dpi,
            numsides = 80, 
            sizes=(self.point_size,),
            facecolors=self.color_array,
            offsets = self.data_array,            
            transOffset = self.axes.transData)
        self.collection.set_alpha(0.7)
        self.axes.add_collection(self.collection)        
        
        #self.axes.axis([self.xmin, self.xmax, self.ymin, self.ymax])
        self.axes.autoscale_view()
        x = self.axes.get_xaxis()
        y = self.axes.get_yaxis()
        x.zoom(-1)
        y.zoom(-1)
        #self.axes.axis('tight')
        ##self.axes.axis('off')        
        
    def callback(self, verts):
        facecolors = self.collection.get_facecolors()
        ind = nonzero(points_inside_poly(self.data_array, verts))[0]
        for i in range(len(self.data_array)):
            if i in ind:
                facecolors[i] = (1,1,0,.5)
                #print facecolors[i]
                #pass
            else:
                facecolors[i] = self.color_array[i]
                #pass

        #print facecolors[i]
        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        del self.lasso
        #self.ind = ind
        self.pass_data(ind)
        
    def onpress(self, event):
        #print event.button
        if self.canvas.widgetlock.locked(): 
            #print 'foo'
            self.canvas.widgetlock.release(self.lasso)
            #return
        if event.inaxes is None: 
            return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
        
    def pass_data(self, ind):
        #populate parents list control
        self.lc_x2_plist.DeleteAllItems()
        for x in ind:
            self.lc_x2_plist.InsertStringItem(0, self.song_array[x][0])
            self.lc_x2_plist.SetStringItem(0, 1, self.song_array[x][1])
        #pass
            
    def update_data(self):
        pass
        #self.figure.clf()
        #build_graph(self)
        #self.MakeScatt()
        #self.build_collection()
        
    def OnAutoGenerateX2Playist(self, event):
        # copy the sifted list to the playlist
        self.parent.CheckClear()
        insert_at = self.parent.lc_playlist.GetItemCount()
        for x in range(self.lc_x2_plist.GetItemCount(), 0, -1):
            artist = self.lc_x2_plist.GetItem(x-1, 0).GetText()
            song = self.lc_x2_plist.GetItem(x-1, 1).GetText()
            self.parent.SetPlaylistItem(insert_at, artist, song, '', '')
        #save the playlist
        self.parent.SavePlaylist()
        # switch tabs
        self.parent.nb_main.SetSelection(self.nb_playlist)
        
# ####################################
import sys
import os
SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))

FILEDB = SYSLOC + '\\gravydb.sq3'
   
     
#2track id
#3tag id
#4tag label
#5listeners
#6playcount
#0artist
#1song
#7time 
def BuildQuery(selected_array):
    query2 =''
    query1 = 'select artist, song, m_tracks.track_id, m_tag.tag_id, tag_label'
    for x in selected_array:
        query2 = query2 + ', ' + FEATURES_ARRAY[x]
    query3 =''' from m_tracks, m_tag, m_pop, m_playcount
            WHERE   m_tracks.track_id = m_pop.track_id AND 
                    m_tracks.tag_id = m_tag.tag_id AND 
                    m_tracks.track_id = m_playcount.track_id'''
            #order by ppl DESC
    
    return query1 + query2 + query3        
        
def GetResultsArray(selected_array):
    TRANS = 0.7
    color_arr = [
                (1.0,0.0,1.0,TRANS),
                (1.0,0.5,0.0,TRANS),                
                (0.5,0.0,1.0,TRANS),
                (0.5,0.5,0.5,TRANS),
                (0.8,1.0,1.0,TRANS),
                (1.0,0.0,0.0,TRANS),
                (0.0,0.0,0.5,TRANS),
                (0.3,0.3,0.3,TRANS),
                (0.0,0.0,0.5,TRANS),
                (0.5,0.1,0.0,TRANS)
                ]    
    use_std = True
    
    conn = sqlite3.connect(FILEDB)
    c = conn.cursor()
    #self.data = np.array([(0.1,0.8),(0.1,0.3), (0.3,0.1)])
    query = BuildQuery(selected_array)
    print query
    c.execute(query)
    h = c.fetchall()
    
    color_a = np.zeros((len(h), 4))
    #number of slected/checked componenets
    comps = len(selected_array)
    if comps == 1:
        comps = 2
        use_std = False
    data_a = np.zeros((len(h), comps))
    song_a = []
    
    #build a list of the checked/selected items
    #features in query results start at 5
    selected_list_string = ''
    for y in range(0, len(selected_array)):
        selected_list_string = selected_list_string + 'x[' + str(y+5) + '],'
        if len(selected_array) == 1:
            selected_list_string = selected_list_string + '0.1,'
    selected_list = '(' + selected_list_string + ')'
    
    counter = 0
    for x in h:
        file_name = ''
        if len(x) > 1:
            #print x            
            #data_a[counter] = np.array([x[5],x[6],x[7],x[8]])
            #print selected_list
            data_a[counter] = np.array(eval(selected_list))
            song_a.append([x[0],x[1]])
            cc = x[3] % 10
            #color_arr.append((cc,cc,1,0.5))
            color_a[counter] =  np.array(color_arr[cc])
            counter = counter + 1
    c.close()
    #print color_a
    
    return data_a, song_a, color_a, use_std
     
def GetTags():
    data_arr = []
    conn = sqlite3.connect(FILEDB)
    c = conn.cursor()
    q1 = "SELECT tag_id, tag_label FROM m_tag ORDER BY tag_id"
    c.execute(q1)
    h = c.fetchall()
    counter = 0
    for x in h:
        data_arr.append(x[1])
    c.close()
    return data_arr
    
    
                                        
class App(wx.App):

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = GraphFrame()
        self.SetTopWindow(frame)
        panel = MainPanel(frame)
        frame.Show(True)
        return True

if __name__=='__main__':
    app = App(0)
    app.MainLoop()
