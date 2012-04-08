from Components.MenuList import MenuList

#from .. import boxwrapper, dreamclass
from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request 

from BaseScreens import Smb_BaseScreen, Smb_BaseEditScreen, Smb_BaseListScreen

#from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_PLUGIN
#from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE
from Components.Label import Label
from Screens.MessageBox import MessageBox

from Components.Input import Input
from Screens.InputBox import InputBox

from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont

from Plugins.Extensions.ShareMyBox.__init__ import _
    
class Smb_Channellist_MainMenu(Smb_BaseListScreen):
  backToMainMenu = True
  title = _("Your Channellists")
  
  def build(self):
     
    self["myMenu"] = MenuList(self.buildlist(), False, eListboxPythonMultiContent)
    #self.act = self.myaction(self)
    
    self["myMenu"].l.setFont(0, gFont("Regular", 20))
    self["myMenu"].l.setFont(1, gFont("Regular", 14))
    self["myMenu"].l.setItemHeight(40)   
    
    #self["myMenu"].onSelectionChanged = [self.Changed]
    
    self["Description"] = Label("")    
    
    self["red"] = Label("Download")
    self["green"] = Label("Upload")
    self["yellow"] = Label("Edit")
    self["blue"] = Label("Delete")    
    
    self.actions['red'] = self.ActionHelperDownload
    self.actions['green'] = self.ActionHelperUpload
    self.actions['yellow'] = self.ActionHelperEdit
    self.actions['blue'] = self.ActionHelperDelete
    self.actions['0'] = self.ActionHelperAdd
    
    self.context = ["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"]
        
  def buildlist(self):
    
    list = []
    


    png = boxwrapper.Icon("channellist_list")

    try:
      api = boxwrapper.SendRequestAuth('ChannellistList').GetList()
    except Exception as e:
      self.ErrorException(e)
      return
    
    for x in api:
      list.append([
            str(x['cid']),
            MultiContentEntryText(pos=(60, 0), size=(320, 25), font=0, text=str(x['name'])),
            MultiContentEntryText(pos=(60, 22), size=(320, 17), font=1, text=dreamclass.format_date(x['updated_on'])),
            MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png = png),
            x
    ])

    return list  

  def onMenuChanged(self, item):
    obj = item[-1]
    items = {
          'Update': dreamclass.format_date(obj.get('content_updated')),
          'Orbitals': str(obj.get('orbitals')),
          'Comment': str(obj.get('comment')),
          }

    self.DescriptionToText(items)      
  
  def ActionHelperAdd(self):
    self.session.openWithCallback(self.ActionCreate, InputBox, title=_("Please enter a name for the new channellist"), text=" " * 20, maxSize=20, type=Input.TEXT)
 
  def ActionHelperDownload(self):
    self.session.openWithCallback(self.ActionDownload, MessageBox, _("Download and overwrite current channellist?"), MessageBox.TYPE_YESNO)            
        
  def ActionHelperDelete(self):
    self.session.openWithCallback(self.ActionDelete, MessageBox, _("Do you want delete this item?"), MessageBox.TYPE_YESNO)   
      
  def ActionHelperUpload(self):
    self.session.openWithCallback(self.ActionUpload, MessageBox, _("Upload and overwrite this list?"), MessageBox.TYPE_YESNO)   
     
  def ActionHelperEdit(self):
    cid = self["myMenu"].l.getCurrentSelection()[0]
    self.session.openWithCallback(self.ActionEdit, Smb_Channellist_Edit, cid)  
  
  def restart(self, result):
    if result is False: return
    boxwrapper.Restart()    
     
  def ActionDelete(self, result):
    try:
      if result is False or self.Id() is None: return
        
      msg = Request().ChannellistDelete(self.Id()).GetResponse()
      self.SetMessage(msg)
      self.rebuild()
    except Exception as e:
      self.SetMessage(str(e))

  def ActionEdit(self, result = '', error = False):
    self.SetMessage(result)
    if error is False:
      self.rebuild()
     
  def ActionCreate(self, word = None):
    if word is None: return
    
    try:      
      word = str(word).strip()
      if len(word) == 0: return
         
      ret = Request().ChannellistAdd(word).GetResponse()
      self.SetMessage(ret)
      self.rebuild()
    except Exception as e:
      self.SetMessage(str(e))      
          
  def ActionDownload(self, result):
    try:
      if result is False or self.Id() is None: return
        
      zip = boxwrapper.GetConfigDir('bouquets.zip')      
      Request().ChannellistDownload(self.Id(), zip)
      dreamclass.Uncompress(zip, True)
              
      self.session.openWithCallback(self.restart, MessageBox, _("Restart to reload new channelllist?"), MessageBox.TYPE_YESNO)
      self.SetMessage('Download ok')
    except Exception as e:
      self.SetMessage(str(e))
      
      
  def ActionUpload(self, result):
    try:      
      if result is False or self.Id() is None: return     
          
      path = boxwrapper.GetConfigDir() + '/'
      bouquets = dreamclass.BouquetsFilesFindAsArray(path, ["bouquets.tv", "bouquets.radio"])
            
      tmp = dreamclass.Compress(bouquets)
      upload = [tmp]
            
      msg = Request().ChannellistUpload(self.Id(), upload).GetResponse()
      self.rebuild()
      self.SetMessage(msg)        
    except Exception as e:
      self.SetMessage(e)      


from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSelection


class Smb_Channellist_Edit(Smb_BaseEditScreen):
  def buildlist(self):
    
    cid = self.args
    ret = Request().ChannellistDetails(cid).GetList()

    fields = [
       {'name': 'name', 'field': ConfigText(fixed_size = False), 'text': 'Name', 'value': str(ret['name'])},
       {'name': 'comment', 'field': ConfigText(fixed_size = False), 'text': 'Comment', 'value': str(ret['comment'])},
       #{'name': 'friends', 'field': ConfigText() , 'text': 'Friends', 'value': dreamclass.str2bool(ret['home'])},       
      ]
 
    list = []
    for field in fields:
      field['field'].setValue(ret[field['name']])
      list.append(getConfigListEntry(_(field['text']), field['field'], field['name']))
      
    return list
  
  def save(self, values):
    try:
      return Request().ChannellistEdit(self.args, values).GetResponse()
    except Exception as e:
      return "Error:" + str(e), True
          
