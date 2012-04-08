import FileList
from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass

from Components.Label import Label
from Plugins.Extensions.ShareMyBox.__init__ import _    

class Smb_FileAvailable_MainMenu(FileList.MainMenu):
  
  title = _('Friends Files')
  
  def buildlist(self):
    
    list = []

    png = boxwrapper.Icon("channellist_list")

    try:
      api = boxwrapper.SendRequestAuth('FileAvailable').GetList()
    except Exception as e:
      self.ErrorException(e)
      return
    
    
    return self.buildlist_ext(api)

  def build(self):
    
    super(Smb_FileAvailable_MainMenu, self).build()
    
    self["red"] = Label("Download")
    self["green"] = Label("")
    self["yellow"] = Label("")
    self["blue"] = Label("")
    self["0"] = Label("")
    
    self.actions['yellow'] = self.no_access
    self.actions['green'] = self.no_access
    self.actions['blue'] = self.no_access
    self.actions['0'] = self.no_access
    
  def no_access(self):
    self.SetMessage(_('no access'))
    