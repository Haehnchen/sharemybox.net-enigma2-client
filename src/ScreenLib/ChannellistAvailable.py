import DownloadChannelList
from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont

class Smb_ChannellistAvailable_MainMenu(DownloadChannelList.Smb_Channellist_MainMenu):
  def buildlist(self):
    
    list = []

    png = boxwrapper.Icon("channellist_list")

    try:
      api = boxwrapper.SendRequestAuth('ChannellistAvailable').GetList()
    except Exception as e:
      self.ErrorException(e)
      return
    
    for x in api:
      list.append([
            str(x['cid']),
            MultiContentEntryText(pos=(60, 0), size=(320, 25), font=0, text=str(x['name'])),
            MultiContentEntryText(pos=(60, 22), size=(320, 17), font=1, text=str(x['users_name'] + ' - ' + dreamclass.format_date(x['updated_on']))),
            MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png = png),
            x
    ])

    return list    