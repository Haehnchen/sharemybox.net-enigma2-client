from Screens.Screen import Screen

from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.ActionMap import ActionMap
from Plugins.Plugin import PluginDescriptor
from Components.MenuList import MenuList

from ShareMyBoxRequets import ShareMyBoxApi as Request 
from boxwrapper import variable_set, variable_get

from Components.config import config, ConfigSubsection, configfile, ConfigPassword, ConfigText
from Screens.InputBox import InputBox
from Components.Input import Input
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest

from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_PLUGIN
from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE
from Tools.LoadPixmap import LoadPixmap
from enigma import eListboxPythonMultiContent, gFont

config.plugins.ShareIt = ConfigSubsection()
config.plugins.ShareIt.Key = ConfigText()
config.plugins.ShareIt.privatekey = ConfigText()

import boxwrapper
import ScreenLib
import dreamclass
from dreamclass import UserInfo, ACCESS
from __init__ import _

import os

#import ScreenLib.ScreenBouquets
import ScreenLib.FileList
import ScreenLib.Actions
import ScreenLib.MasterBox
import ScreenLib.DownloadChannelList
import ScreenLib.ChannellistAvailable
import ScreenLib.FileAvailable
import ScreenLib.SmbTools
import ScreenLib.SmbSettings


from skin import loadSkin, lookupScreen, dom_skins
loadSkin(os.path.dirname(os.path.realpath(__file__)) + '/skin.xml')

class Smb_MainMenu(Screen):

  def buildlist(self):
  
    private_key = variable_get('privatekey')
    if private_key is not None:
      UserInfo().SetPrivateKey(private_key)
      
    try:
      box = Request().BoxDetails().GetList()
      if box.has_key('uid'):
        UserInfo().SetUid(box['uid'])
    except Exception as e:
      UserInfo().Reset()
      self.SetMessage(str(e))

    list = []
    
    #png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/icons/plugin.png"))
    access = LoadPixmap(dreamclass.GetIcon('access'))
    #print png

    api = []
    
    if dreamclass.GetAccess(ACCESS.REGISTERED) is False:
      api.append({'name': _("Register"), 'description': _('Register your box to get access'), 'func': self.actions.RegisterBox, 'icon': 'register'})
      api.append({'name': _("Register safe"), 'description': _('Register your already married box with account name'), 'func': self.actions.RegisterBoxSafe, 'icon': 'registersafe'})
      #api.append({'name': "Debug", 'description': ' ', 'func': self.actions.DebugGetBoxkey, 'icon': 'register'})    
    
    api.append({'name': _("Your channellists"), 'description': _('Manage your Channellists'), 'func': self.actions.MyChannels, 'icon': 'channellist', 'needaccess' : ACCESS.MARRIED})
    api.append({'name': _("Friends channellists"), 'description': _('Available readonly channellists from friends'), 'func': self.actions.AvailableChannellists, 'icon': 'channellist_dl', 'needaccess' : ACCESS.REGISTERED})
    api.append({'name': _("Your Files"), 'description': _('Manage your files'), 'func': self.actions.FileList, 'icon': 'filesync', 'needaccess' : ACCESS.MARRIED})
    api.append({'name': _("Friends Files"), 'description': _('Accessable files from friends'), 'func': self.actions.AvailableFiles, 'icon': 'filesync', 'needaccess' : ACCESS.REGISTERED})
    api.append({'name': _("Friends"), 'description': _('Manager your friends'), 'func': self.actions.Masters, 'icon': 'register', 'needaccess' : ACCESS.REGISTERED})
    
    api.append({'name': _("Tools"), 'description': _('Tools and other Stuff'), 'func': self.actions.Tools, 'icon': 'tools'})
    api.append({'name': _("Settings"), 'description': _('ShareMyBox Settings'), 'func': self.actions.Settings, 'icon': 'settings', 'needaccess' : ACCESS.REGISTERED})
    
    if dreamclass.GetAccess(ACCESS.REGISTERED) is True and dreamclass.GetAccess(ACCESS.MARRIED) is False:
      api.append({'name': _("Add Account"), 'description': _('Marry box to account on mail / username'), 'func': self.actions.Marry, 'icon': 'mail', 'needaccess' : not dreamclass.GetAccess(ACCESS.MARRIED)})

    if dreamclass.GetAccess(ACCESS.REGISTERED) is True:
      api.append({'name': _("Reset"), 'description': _('Reset your keys'), 'func': self.actions.reset, 'icon': 'reset'})

    for x in api:
      png = LoadPixmap(dreamclass.GetIcon(x['icon']))
      
      obj = [
            x,
            MultiContentEntryText(pos=(60, 0), size=(335, 25), font=0, text=x['name']),
            MultiContentEntryText(pos=(62, 22), size=(335, 17), font=1, text=x['description']),
            MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png = png),
      ]
        
      if x.has_key('needaccess') and self.itemaccess(x['needaccess']) is False:
        obj.append(MultiContentEntryPixmapAlphaTest(pos=(395, 5), size=(20, 20), png = access))
      
      list.append(obj)  
    
    if dreamclass.GetAccess(ACCESS.REGISTERED) is False:
      self.SetMessage('Please register your box!')      
      
    return list 


  def reset(self):
    print 'reset'

  def __init__(self, session, args = 0):
    self.session = session
    
     
    list = []

    Screen.__init__(self, session)
    #self["myMenu"] = MenuList(list)

    self["Statusbar"] = Label('')
    
    self["myMenu"] = MenuList(self.buildlist(), False, eListboxPythonMultiContent)
    
    self["myMenu"].l.setFont(0, gFont("Regular", 20))
    self["myMenu"].l.setFont(1, gFont("Regular", 14))
    self["myMenu"].l.setItemHeight(40)   
        
    self["myActionMap"] = ActionMap(["SetupActions"],    
    {
      "ok": self.go,
      "cancel": self.cancel
    }, -1)


  def onMenuChanged1(self, item):
    obj = item[-1]
    items = {
          'Update': dreamclass.format_date(obj['updated_on']),
          'Orbitals': str(obj['orbitals']),
          'Comment': str(obj['comment']),
          }

    self.DescriptionToText(items) 

  def itemaccess(self, item):
    return dreamclass.GetAccess(item) == True

  def SetMessage(self, msg = ''):
      self["Statusbar"].text = str(msg)  

  def rebuild(self):
    self["myMenu"].setList(self.buildlist())

  def go(self):
    
    try:
      returnItems = self["myMenu"].l.getCurrentSelection()[0]
      returnValue = returnItems['func']
      
      if returnItems.has_key('needaccess') and self.itemaccess(returnItems['needaccess']) is False:
        self.SetMessage('no access')
        return    
      
      returnValue(self, returnItems)
      return
          
    except Exception, e:
      print 'Error:', e        
          
  def MsgCallback(self, back = None):
    self.SetMessage()
    if back is None:
      return
    
    self.SetMessage(str(back))
              
  def MarryCallback(self, word):
    if word is None: return
    
    try:      
      word = str(word).strip()
      if len(word) == 0: return
         
      ret = Request().BoxMarry(word).GetResponse()
      self.SetMessage(ret)
      
    except Exception as e:
      self.SetMessage(str(e))     
      
  def registered(self, keys):
      privatekey = str(keys['privatekey'])
      boxkey = str(keys['boxkey'])
      variable_set('privatekey', privatekey)
      self.myMsg(_('Box is registered. You have access now!') + '\r\n\r\nprivatekey: %s\r\nboxkey: %s' % (privatekey, boxkey))
      self.rebuild()
      self.SetMessage('Register ok')               
          
  def CallbackRegisterSafe(self, word):
    if word is None: return
    
    try:
      word = str(word).strip()
      if len(word) == 0: return
      self.registered(Request().BoxRegistersafe(word).GetList())
      
    except Exception as e:
      self.SetMessage(str(e))           
 
  def AddMasterboxCallback(self, word):
    if word is None: return
    
    try:      
      word = str(word).strip()
      if len(word) == 0: return
         
      ret = Request().SlaveboxAdd(word).GetResponse()
      self.SetMessage(ret)
      
    except Exception as e:
      self.SetMessage(str(e))  
 
  def myMsg(self, entry):
      self.session.open(MessageBox, entry, MessageBox.TYPE_INFO)
      
  def cancel(self):
    print "\n[MyMenu] cancel\n"
    self.close(None)
    
  def SendRequest(self, func):
    try:
      f = getattr(Request(), func)
      return f()
    except Exception as e:
      import traceback
      print traceback.print_exc()      
      print self.myMsg("Error:" + str(e))
      return f

  class actions(object):
    @staticmethod
    def reset(YourScreen, item):
      variable_set('privatekey', '')
      UserInfo().Reset()        
      YourScreen.rebuild()
      YourScreen.SetMessage('Reset')
      
    @staticmethod
    def Settings(YourScreen, item):
      reload(ScreenLib.SmbSettings)
      YourScreen.session.openWithCallback(YourScreen.MsgCallback, ScreenLib.SmbSettings.Smb_Settings)  
     
    @staticmethod
    def RegisterBoxSafe(YourScreen, item):
      YourScreen.session.openWithCallback(YourScreen.CallbackRegisterSafe, InputBox, title=_("Please enter Username or Mail of married account"), text=" " * 55, maxSize=55, type=Input.TEXT)
     
    @staticmethod      
    def RegisterBox(YourScreen, item):
      YourScreen.registered(YourScreen.SendRequest('BoxRegister').GetList())

    @staticmethod      
    def MyChannels(YourScreen, item):
      reload(ScreenLib.DownloadChannelList)
      YourScreen.session.open(ScreenLib.DownloadChannelList.Smb_Channellist_MainMenu)  
    
    @staticmethod      
    def AvailableChannellists(YourScreen, item):
      reload(ScreenLib.ChannellistAvailable)
      YourScreen.session.open(ScreenLib.ChannellistAvailable.Smb_ChannellistAvailable_MainMenu)  
      
    @staticmethod      
    def AvailableFiles(YourScreen, item):
      reload(ScreenLib.FileAvailable)
      YourScreen.session.open(ScreenLib.FileAvailable.Smb_FileAvailable_MainMenu)        
      
    @staticmethod      
    def Tools(YourScreen, item):
      reload(ScreenLib.SmbTools)
      YourScreen.session.open(ScreenLib.SmbTools.Smb_Tools_MainMenu)        
      
    @staticmethod      
    def DebugGetBoxkey(YourScreen, item):
      msg = 'boxkey:' + str(dreamclass.getBoxKey())
      if variable_get('privatekey') is not None: 
        msg = msg + '\nprivatekey:' + str(variable_get('privatekey')) 
      
      YourScreen.myMsg(msg)

    @staticmethod      
    def Masters(YourScreen, item):
      reload(ScreenLib.MasterBox)
      YourScreen.session.open(ScreenLib.MasterBox.MainMenu)      
      
    @staticmethod      
    def FileList(YourScreen, item):
      reload(ScreenLib.FileList)
      YourScreen.session.open(ScreenLib.FileList.MainMenu)
      
    @staticmethod      
    def ListActions(YourScreen, item):   
      reload(ScreenLib.Actions)
      YourScreen.session.open(ScreenLib.Actions.MainMenu)        
      
    @staticmethod      
    def Marry(YourScreen, item):         
      YourScreen.session.openWithCallback(YourScreen.MarryCallback, InputBox, title=_("Please enter Username or Mail of your Account"), text=" " * 55, maxSize=55, type=Input.TEXT)      
