from Components.MenuList import MenuList

from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request
 
from BaseScreens import Smb_BaseScreen


from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_PLUGIN
from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE
from Components.Label import Label

from Screens.MessageBox import MessageBox

from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont
from Tools.LoadPixmap import LoadPixmap

import time
    
class MainMenu(Smb_BaseScreen):
  backToMainMenu = True

  skin = """
        <screen position="110,83" size="530,450" title="">
            <widget name="myMenu" position="10,10" size="380,380" scrollbarMode="showOnDemand" />
            
            <widget name="Statusbar" position="10,430" size="530,20" font="Regular;12"/>
            <widget name="Description" position="390,10" size="50,380" font="Regular;12"/>
            
            <widget name="red" position="10,390" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
            <widget name="green" position="140,390" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
            <widget name="yellow" position="270,390" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
            <widget name="blue" position="400,390" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>

            <ePixmap name="pred" position="10,390" size="120,30" zPosition="0" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
            <ePixmap name="pgreen" position="140,390" size="120,30" zPosition="0" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on"/>
            <ePixmap name="pyellow" position="270,390" size="120,30" zPosition="0" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on"/>
            <ePixmap name="pblue" position="400,390" size="120,30" zPosition="0" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on"/>
        </screen>
        """
      
  def build(self):
     
    self["myMenu"] = MenuList(self.buildlist(), False, eListboxPythonMultiContent)
    self["myMenu"].onSelectionChanged = [self.Changed]
    
    self["myMenu"].l.setFont(0, gFont("Regular", 20))
    self["myMenu"].l.setFont(1, gFont("Regular", 14))
    self["myMenu"].l.setItemHeight(40)
    
    
    self["Description"] = Label("/var")
    
    self["red"] = Label("")
    self["green"] = Label("")
    self["yellow"] = Label("")
    self["blue"] = Label("Delete")    
    
    self.actions['red'] = lambda: self.action('create')
    self.actions['green'] = lambda: self.action('upload')
    self.actions['yellow'] = lambda: self.action()
    self.actions['blue'] = lambda: self.action('delete')
    self.actions['ok'] = lambda: self.action('ok')
    #self.actions["up"] = lambda: self.Changed('up')
    #self.actions["down"] = self.Changed('down')
    
    self.context = ["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"]

  def Changed(self):
    item = self["myMenu"].l.getCurrentSelection()
    if item is None: return
            
    action = item[3]
    self["Description"].setText(str(action['actionkey']))

  def buildlist(self):
    
    list = []
    
    png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/icons/plugin.png"))
        
    api = boxwrapper.SendRequestAuth('ActionList').GetList()
    for x in api:
      list.append([
            str(x['actionkey']),
            MultiContentEntryText(pos=(120, 0), size=(320, 25), font=0, text=str(x['callback'])),
            #MultiContentEntryText(pos=(120, 26), size=(320, 17), font=1, text=time.strftime("%m/%d/%Y %H:%M",time.localtime(float(x['updated_on'])))),
            MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(100, 50), png = png),
            x
    ])
      
    return list  
  
  def action(self, actiontype):
    selected = self["myMenu"].l.getCurrentSelection()
    if selected is None: return     

    if actiontype == "delete":
      self.session.openWithCallback(self.delete, MessageBox, _("Do you want delete this item?"), MessageBox.TYPE_YESNO)  
      
    if actiontype == "ok":
      self.session.openWithCallback(self.performaction, MessageBox, _("Do you want delete this item?"), MessageBox.TYPE_YESNO)         

  def performaction(self, result):
    if result is False: return
       
    try:
      obj = self["myMenu"].l.getCurrentSelection()[3]
      msg = Request().ActionPerform(str(obj['actionkey'])).GetResponse()
      self.SetMessage(str(msg))
      self.rebuild()
          
    except Exception as e:
      self.SetMessage("Error:" + str(e))       

  def rebuild(self):
    self["myMenu"].setList(self.buildlist())
    
  def delete(self, result):
    if result is False: return
       
    try:
      obj = self["myMenu"].l.getCurrentSelection()[3]
      msg = Request().ActionDelete(str(obj['actionkey'])).GetResponse()
      self.SetMessage(str(msg))
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

