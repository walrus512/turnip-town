# http://wiki.wxpython.org/ListControls#Drag_and_Drop_with_lists
import wx
MAIN_PLAYLIST = "playlist.xspf"

#---------------------------------------------------------------------------
# ####################################
class DragList(wx.ListCtrl):
    _firstEventType = wx.EVT_SIZE
    #_firstEventType = wx.EVT_WINDOW_CREATE

    def __init__(self):
        p = wx.PreListCtrl()
        # the Create step is done by XRC.
        self.start_pos = (0,0)
        self.PostCreate(p)
        # Apparently the official way to do this is:
        #self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        # But this seems to be the actually working way, cf:
        # http://aspn.activestate.com/ASPN/Mail/Message/wxPython-users/2169189
                
        self.Bind(self._firstEventType, self.OnCreate)      

    def _PostInit(self):
        # initializes drag drop
        dt = ListDrop(self._insert)
        self.SetDropTarget(dt)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self._startDrag)

    def OnCreate(self, evt):
        self.Unbind(self._firstEventType)
        # Called at window creation time
        self._PostInit()
        self.Refresh()
        
    # drag-drop start 
              
    def getItemInfoString(self, idx):
        """Collect all relevant data of a listitem, and put it in a list"""
        l = ''
        #l = l + unicode(str(idx) + '|') # We need the original index, so it is easier to eventualy delete it
        #l.append(self.GetItemData(idx)) # Itemdata
        l = l + unicode(self.GetItemText(idx) + '|') # Text first column
        for i in range(1, self.GetColumnCount()): # Possible extra columns
            l = l + unicode(self.GetItem(idx, i).GetText() + '|')
        return l
     
    def _startDrag(self, e):
        """ Put together a data object for drag-and-drop _from_ this list. """

        # Create the data object: Just use plain text.
        data = wx.PyTextDataObject()
        #idx = e.GetIndex()
        #text = self.GetItem(idx).GetText()

        idx = self.GetFirstSelected()
        current_select = self.GetFirstSelected()
        item_string = ''
        #print 'hoo:' + str(idx)
        #print 'count:' + str(self.GetSelectedItemCount())
        for x in range(idx, idx + self.GetSelectedItemCount()):
            item_string = item_string + (self.getItemInfoString(current_select))
            current_select = self.GetNextSelected(current_select)
            #print item_string
        data.SetText(item_string)
            
        # Create drop source and begin drag-and-drop.
        dropSource = wx.DropSource(self)
        dropSource.SetData(data)
        res = dropSource.DoDragDrop(flags=wx.Drag_DefaultMove)
        

        # If move, we want to remove the item from this list.
        if res == wx.DragMove:
            # It's possible we are dragging/dropping from this list to this list.  In which case, the
            # index we are removing may have changed...

            # Find correct position.
            #pos = self.FindItem(idx, text)
            #print 'count' + str(self.GetSelectedItemCount())
            #print 'count2' + str(self.GetItemCount())
            if self.GetSelectedItemCount() == 1:
                self.DeleteItem(self.GetFirstSelected())
            else:
                # delete removes one form the list instantly so you don't need to increment, ie, removing 6, makes 7 -> 6
                for x in range(self.GetSelectedItemCount(), 0, -1):
                    #if x == 0:
                    #print 'count' + str(self.GetSelectedItemCount())
                    #print self.GetNextSelected(self.GetFirstSelected())
                    self.DeleteItem(self.GetFirstSelected())
                    
                    #   first_sel = self.GetFirstSelected()
                    #else:
                        # problems if there items selected aren't contigueus
                    #   self.DeleteItem(self.GetNextSelected(first_sel) - x)
                    #   first_sel =     
                    #print 'del: ' + str(self.GetFirstSelected())
            # save playlist
            # *** bad
            #self.GetGrandParent().GetGrandParent().SavePlaylist(MAIN_PLAYLIST)

    def _insert(self, x, y, text):
        """ Insert text at given x, y coordinates --- used with drag-and-drop. """

        # Clean text.
        #text = filter(lambda x: x in (string.letters + string.digits + string.punctuation + ' '), text)

        # Find insertion point.
        index, flags = self.HitTest((x, y))

        if index == wx.NOT_FOUND:
            if flags & wx.LIST_HITTEST_NOWHERE:
                index = self.GetItemCount()
            else:
                return

        # Get bounding rectangle for the item the user is dropping over.
        rect = self.GetItemRect(index)

        # If the user is dropping into the lower half of the rect, we want to insert _after_ this item.
        if y > (rect.y + rect.height/2):
            index = index + 1

        all_rows = text.split('|')
        #print len(all_rows)
        #print text
        #print self.GetColumnCount()
        if len(all_rows) == (self.GetColumnCount() + 1): #6:
            the_range = 1;
        else:
            the_range = (len(all_rows)- 1) / self.GetColumnCount() #5  
        #each row has 5 items
        #print 'range: ' + str(the_range)
        counter = 0
        counter2 = 0
        for x in range(0, the_range):
            self.InsertStringItem(index + counter2, all_rows[0 + counter])
            for y in range(1, self.GetColumnCount()):
                #print y
                self.SetStringItem(index + counter2, y, all_rows[y + counter])
            #    print y
            #self.SetStringItem(index + counter2, 2, all_rows[2 + counter])
            #self.SetStringItem(index + counter2, 3, all_rows[3 + counter])
            #self.SetStringItem(index + counter2, 4, all_rows[4 + counter])
            #print counter2
            counter = counter + self.GetColumnCount() #5
            counter2 = counter2 + 1
                  

class ListDrop(wx.PyDropTarget):
    """ Drop target for simple lists. """

    def __init__(self, setFn):
        """ Arguments:
         - setFn: Function to call on drop.
        """
        wx.PyDropTarget.__init__(self)

        self.setFn = setFn

        # specify the type of data we will accept
        self.data = wx.PyTextDataObject()
        self.SetDataObject(self.data)

    # Called when OnDrop returns True.  We need to get the data and
    # do something with it.
    def OnData(self, x, y, d):
        # copy the data from the drag source to our data object
        if self.GetData():
            self.setFn(x, y, self.data.GetText())

        # what is returned signals the source what to do
        # with the original data (move, copy, etc.)  In this
        # case we just return the suggested value given to us.
        return d

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
        
