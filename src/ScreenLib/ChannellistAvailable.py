import DownloadChannelList
from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest

from Components.Label import Label
from Plugins.Extensions.ShareMyBox.__init__ import _   

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
      #print x['content_updated']
      list.append([
            str(x['cid']),
            MultiContentEntryText(pos=(60, 0), size=(320, 25), font=0, text=str(x['name'])),
            MultiContentEntryText(pos=(60, 22), size=(320, 17), font=1, text=str(x.get('users_name', '') + ' - ' + dreamclass.format_date(x.get('content_updated', 0)))),
            MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png = png),
            x
    ])

    return list
  
  def build(self):
    
    super(Smb_ChannellistAvailable_MainMenu, self).build()
    
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