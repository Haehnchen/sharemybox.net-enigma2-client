import FileList
from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont

class Smb_FileAvailable_MainMenu(FileList.MainMenu):
  
  title = 'Friends Files'  
  
  def buildlist(self):
    
    list = []

    png = boxwrapper.Icon("channellist_list")

    try:
      api = boxwrapper.SendRequestAuth('FileAvailable').GetList()
    except Exception as e:
      self.ErrorException(e)
      return
    
    
    return self.buildlist_ext(api)
