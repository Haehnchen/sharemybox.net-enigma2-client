from Screens.Screen import Screen
#from dreamclass import UserInfo, ACCESS
#from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
#from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request 
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop

from BaseScreens import Smb_BaseScreen
from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont
from Components.MenuList import MenuList
from enigma import eConsoleAppContainer
from Tools.LoadPixmap import LoadPixmap
#import Plugins.Extensions.ShareMyBox.ShareMyBoxTimer
from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request 
#from Plugins.Extensions.ShareMyBox.ShareMyBoxTimer import ShareMyBoxTimerWorker
from Tools.Notifications import AddPopup
from ServiceReference import ServiceReference

#from RecordTimer import RecordTimerEntry, RecordTimer, AFTEREVENT, parseEvent


import Screens.Ipkg 
import re

UPDATE_URL = "http://sharemybox.net/client/sharemybox_lastest_all.ipk"


class Smb_Tools_MainMenu(Smb_BaseScreen):
  title = 'Tools'

  def build(self):
     
    self["myMenu"] = MenuList(self.buildlist(), False, eListboxPythonMultiContent)
    self["myMenu"].l.setFont(0, gFont("Regular", 20))
    self["myMenu"].l.setFont(1, gFont("Regular", 14))
    self["myMenu"].l.setItemHeight(40)   

    self.context = ["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"]

  def buildlist(self):
    
    list = []

    png = boxwrapper.Icon("channellist_list")
    
    api = []
    api.append({'name': "Update Client", 'description': 'Upload ShareMyBox Client', 'func': self.msgUpdate, 'icon': 'update'})
    #api.append({'name': "Sync Records", 'description': 'Download managed Records', 'func': self.records, 'icon': 'records'})

    for x in api:
      png = LoadPixmap(dreamclass.GetIcon(x['icon']))
      
      obj = [
            x,
            MultiContentEntryText(pos=(60, 0), size=(320, 25), font=0, text=x['name']),
            MultiContentEntryText(pos=(62, 22), size=(320, 17), font=1, text=x['description']),
            MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png = png),
      ]
        
      #if x.has_key('needaccess') and self.itemaccess(x['needaccess']) is False:
      #  obj.append(MultiContentEntryPixmapAlphaTest(pos=(395, 5), size=(20, 20), png = access))
      
      list.append(obj)      
    
    return list
    
  def ok(self):
    
    try:
      
      returnItems = self["myMenu"].l.getCurrentSelection()[0]
      returnValue = returnItems['func']
          
      if returnItems.has_key('needaccess') and self.itemaccess(returnItems['needaccess']) is False:
        self.SetMessage('no access')
        return    
          
      returnValue(returnItems)
      
    except Exception as e:
      self.SetMessage(str(e))
    
   
  def msgUpdate(self, item = None):
    self.session.openWithCallback(self.EventStartUpdate,MessageBox,_("Update Client now:\nDo you want to download and install now?"), MessageBox.TYPE_YESNO)
      
  def itemaccess(self, item):
    return dreamclass.GetAccess(item) == True      
    
  def records(self, item = None):
    pass
    #recordtimer = ShareMyBoxTimerWorker(self.session.nav.RecordTimer).run()
    #self.SetMessage(str(recordtimer))
      
  def EventStartUpdate(self, result = False):
    if result is False: return
     
    # @TODO: internal funcs?
    cmd = "opkg install --force-overwrite " + UPDATE_URL  + "; killall -9 enigma2"
    print cmd
    
    container = eConsoleAppContainer()
    container.appClosed.append(self.EventUpdated)
    container.execute(cmd)
  

  def EventUpdated(self):
    self.session.openWithCallback(self.restartGUI, MessageBox, _("Plugin successfully updated!\nDo you want to restart Enigma2 GUI now?"), MessageBox.TYPE_YESNO)


"""
  def restartGUI(self, result):
    if result is None: return
    self.session.open(TryQuitMainloop, 3)        
    args = []
    args.append(['name', ['cmd']])
    
    self.session.open(Screens.Ipkg.Ipkg, args)
    print "test"
"""    
    
    
      