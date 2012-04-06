from Components.MenuList import MenuList

from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request 

from BaseScreens import Smb_BaseScreen, Smb_BaseListScreen, Smb_BaseEditScreen

from Components.Label import Label

from Screens.InputBox import InputBox
from Components.Input import Input

import os
    
from Screens.MessageBox import MessageBox

from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont


import FileUpload
    

class MainMenu(Smb_BaseListScreen):
  
  title = 'Your Files'
 
  def build(self):
     
    self["myMenu"] = MenuList(self.buildlist(), False, eListboxPythonMultiContent)
    self["myMenu"].l.setFont(0, gFont("Regular", 20))
    self["myMenu"].l.setFont(1, gFont("Regular", 14))
    self["myMenu"].l.setItemHeight(40)   
    
    self["Description"] = Label("/var")
       
    self["red"] = Label("Download")
    self["green"] = Label("Edit")
    self["yellow"] = Label("Upload current")
    self["blue"] = Label("Delete")    
    
    self.actions['red'] = lambda: self.action('download')
    self.actions['green'] = self.edit
    self.actions['yellow'] = lambda: self.action('upload')
    self.actions['blue'] = lambda: self.action('delete')
    
    self.actions['0'] = lambda: self.action('add')
    
    
    self.context = ["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"]
        

  def buildlist_ext(self, api):
    
    list = []
    
    file_outdated = boxwrapper.Icon("file_outdated")
    file_not_found = boxwrapper.Icon("file_not_found")
    png = boxwrapper.Icon("files")    
    
    for x in api:
      
      icon = png
      filename = x['name']
      if not os.path.exists(filename):
        icon = file_not_found
      else:
        pass
        #if os.path.getmtime(filename) < x['updated_on']:
        #  icon = file_outdated 
      
      list.append([
            str(x['fid']),
            MultiContentEntryText(pos=(60, 0), size=(320, 25), font=0, text=str(x['name'])),
            MultiContentEntryText(pos=(60, 22), size=(320, 17), font=1, text=dreamclass.format_date(x['updated_on'])),
            MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png = icon),
            x
    ])
      
    return list      
        
  def buildlist(self):
        
    try:
      api = boxwrapper.SendRequestAuth('FileList').GetList()
    except Exception as e:
      self.ErrorException(e)
      return        

    return self.buildlist_ext(api)
  
  
  
  def action(self, actiontype):
    if actiontype == "create":
      self.session.openWithCallback(self.create, InputBox, title=_("Please enter a name for prombt!"), text=" " * 20, maxSize=20, type=Input.TEXT)            
        
    if actiontype == "delete":
      self.session.openWithCallback(self.delete, MessageBox, _("Do you want delete this item?"), MessageBox.TYPE_YESNO)   
      
    if actiontype == "add":
      self.session.openWithCallback(self.add, FileUpload.MainMenu, "test")           

    if actiontype == "edit":
      self.session.openWithCallback(self.edit, MessageBox, _("Do you want upload this item?"), MessageBox.TYPE_YESNO)    
      
    if actiontype == "download":
      self.session.openWithCallback(self.download, MessageBox, _("Do you want download this item?"), MessageBox.TYPE_YESNO)        
      
    if actiontype == "upload":
      self.session.openWithCallback(self.upload, MessageBox, _("Do you want delete this item?"), MessageBox.TYPE_YESNO)        

  def rebuild(self):
    self["myMenu"].setList(self.buildlist())
    
  def onMenuChanged(self, item):
    obj = item[-1]
    items = {
          'Update': dreamclass.format_date(obj['updated_on']),
          'Description': str(obj['comment'])
          }

    filename = obj['name']
    if os.path.exists(filename):
      items['Local'] = dreamclass.format_date(os.path.getmtime(filename))

    self.DescriptionToText(items)         
    
  def delete(self, result = False):
    if result is False: return     
    
    try:    
      fid = self["myMenu"].l.getCurrentSelection()[0]
      if fid is not None:
        msg = Request().FileDelete(fid).GetResponse()
        self.SetMessage(msg)
        self.rebuild()
          
    except Exception as e:
      self.SetMessage("Error:" + str(e))      
      
  def download(self, result = False):
    try:
      if result is False: return
      if not self["myMenu"].l.getCurrentSelection(): return
      if self.Id() is None: return   
      
      Request().FileDownload(self.Id())
      self.SetMessage('Download successfully')
      self.rebuild()
            
    except Exception as e:
      self.SetMessage("Error:" + str(e))      
      
  def add(self, filename = None):      
    if filename is None: return    
    try:    
      msg = Request().FileAdd([filename]).GetResponse()
      self.SetMessage(msg)
      self.rebuild()      
    except Exception as e:
      self.SetMessage("Error:" + str(e))              
      
  def edit(self, result = False):
    fid = self["myMenu"].l.getCurrentSelection()[0]
    self.session.openWithCallback(self.ActionEdit, Smb_File_Edit, fid)          
    
  def ActionEdit(self, result = '', error = False):
    self.SetMessage(result)
    if error is False:
      self.rebuild()    
    
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
    
    try:
      selc = self["myMenu"].l.getCurrentSelection()
      filename = selc[-1]['name']
      
      import os
      if not os.path.exists(filename):
        raise Exception('File not found')
      
      ret = Request().FileUpload(selc[0], [filename]).GetResponse()
      
      self.SetMessage(ret)      
      #if message != "":
      #  self.SetMessage(message) 
     
             
      if result:
        self.rebuild()
      
    except Exception as e:
      self.SetMessage(str(e))


from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSelection
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.ActionMap import ActionMap
        
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen

class Smb_File_Edit(Smb_BaseEditScreen):
  def buildlist(self):
    
    fid = self.args
    print fid
    ret = Request().FileDetails(fid).GetList()

    fields = [
       {'name': 'comment', 'field': ConfigText(fixed_size = False), 'text': 'Comment', 'value': str(ret['comment'])},
      ]
 
    list = []
    for field in fields:
      field['field'].setValue(ret[field['name']])
      list.append(getConfigListEntry(_(field['text']), field['field'], field['name']))
      
    return list
  
  def save(self, values):
    try:
      return Request().FileEdit(self.args, values).GetResponse()
    except Exception as e:
      return "Error:" + str(e), True
        