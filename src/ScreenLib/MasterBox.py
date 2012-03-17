from Components.MenuList import MenuList

from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request 

from BaseScreens import Smb_BaseScreen, Smb_BaseListScreen


from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_PLUGIN
from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE
from Components.Label import Label

from Screens.InputBox import InputBox
from Components.Input import Input

from Screens.MessageBox import MessageBox

from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont
from Tools.LoadPixmap import LoadPixmap

import time
    
class MainMenu(Smb_BaseListScreen):

  def build(self):
     
    self["myMenu"] = MenuList(self.buildlist(), False, eListboxPythonMultiContent)
    self["myMenu"].onSelectionChanged = [self.Changed]
    self["myMenu"].l.setFont(0, gFont("Regular", 20))
    self["myMenu"].l.setFont(1, gFont("Regular", 14))
    self["myMenu"].l.setItemHeight(40)   
    
    self["Description"] = Label("/var")
    
    self["red"] = Label("Add")
    self["green"] = Label("Delete")
    self["yellow"] = Label("")
    self["blue"] = Label("")    
    
    self.actions['red'] = self.ActionHelperAdd
    self.actions['green'] = self.ActionHelperDelete
    self.actions['yellow'] = lambda: self.action
    self.actions['blue'] = lambda: self.action('delete')
    self.context = ["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"]
        
  def Changed(self):
    item = self["myMenu"].l.getCurrentSelection()
    if item is None: return
            
    obj = item[-1]
    self["Description"].setText(str(obj['boxkey']))        
        
  def buildlist(self):
    
    list = []
    
    icon_friend = boxwrapper.Icon('friend')
    icon_disable = boxwrapper.Icon('friend_disable')
    
    try:
      api = boxwrapper.SendRequestAuth('MasterList').GetList()
    except Exception as e:
      self.ErrorException(e)
      return    
        

    for x in api:
      
      icon = icon_friend
      if not x['approved'] == "1":
        icon = icon_disable
      
      list.append([
            str(x['sid']),
            MultiContentEntryText(pos=(60, 0), size=(320, 25), font=0, text=str(x['name'])),
            MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png = icon),
            x
    ])        
      
    return list  
  
  def onMenuChanged(self, item):
    obj = item[-1]
    items = {
          'Update': dreamclass.format_date(obj['updated_on']),
          'Approved': str(obj['approved']),
          }

    self.DescriptionToText(items)      
    
  def ActionHelperAdd(self):
    self.session.openWithCallback(self.AddFriendCallback, InputBox, title=_("Please enter Username or Mail of friends account"), text=" " * 55, maxSize=55, type=Input.TEXT)    
        
  def ActionHelperDelete(self):
    self.session.openWithCallback(self.ActionDelete, MessageBox, _("Do you want delete this item?"), MessageBox.TYPE_YESNO)   

  def AddFriendCallback(self, word = None):
    if word is None: return
    
    try:      
      word = str(word).strip()
      if len(word) == 0: return
         
      ret = Request().FriendAdd(word).GetResponse()
      self.SetMessage(ret)
      
    except Exception as e:
      self.SetMessage(str(e))  

  def ActionDelete(self, result):
    try:
      if result is False or self.Id() is None: return
        
      msg = Request().FriendDelete(self.Id()).GetResponse()
      self.SetMessage(msg)
      self.rebuild()
    except Exception as e:
      self.SetMessage(str(e))

  def rebuild(self):
    self["myMenu"].setList(self.buildlist())
    
  def delete(self, result):
    if result is False: return     
    
    try:    
      oid = self["myMenu"].l.getCurrentSelection()[0]
      if oid is not None:
        msg = Request().BouquetDelete(oid).GetResponse()
        self.SetMessage(msg)
        self.rebuild()
          
    except Exception as e:
      self.SetMessage("Error:" + str(e))      
    
  def create(self, word):
    if word is None: return
    
    word = str(word).strip()
    if len(word) == 0: return

    
    try:
      ret = Request().BouquetAdd(word).GetResponse()
      self.SetMessage(ret)
      self.rebuild()
        
    except Exception as e:
      self.SetMessage("Error:" + str(e))  

  def upload(self, result):
    if result is False: return     

    bid = self["myMenu"].l.getCurrentSelection()[0]
    if bid is None: return None
    
    try:
      path = boxwrapper.GetConfigDir()
      bfile = path + "/bouquets.tv"
      bouquets = dreamclass.BouqetFilesFind(bfile)
      ret = Request().UploadBouquets(bid, bouquets).GetResponse()
      self.SetMessage(ret)
    except Exception as e:
      self.SetMessage("Error:" + str(e))

