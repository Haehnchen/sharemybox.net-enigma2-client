from Plugins.Extensions.ShareMyBox import boxwrapper, dreamclass
from Plugins.Extensions.ShareMyBox.boxwrapper import variable_set, variable_get
from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request 

from BaseScreens import Smb_BaseScreen, Smb_BaseEditScreen, Smb_BaseListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSelection


#config.plugins.ShareMyBox = ConfigSubsection()
#config.plugins.ShareMyBox.autosync_timers = ConfigYesNo()


class Smb_Settings(Smb_BaseEditScreen):
  __description = ''
  
  def buildlist(self):
    
    ret = Request().BoxDetails().GetList()
    if ret.has_key('description'):
      self.__description = str(ret['description'])
    
    fields = [
       #{'description': 'description', 'field': ConfigText(fixed_size = False), 'text': 'Box Description', 'value': ''},
       #{'name': 'comment', 'field': ConfigText(fixed_size = False), 'text': 'Comment', 'value': str(ret['comment'])},
       {'name': 'description', 'field': ConfigText() , 'text': 'Box Description', 'value': self.__description},
       #{'name': 'autosync_timers', 'field': ConfigYesNo() , 'text': 'Sync Timers', 'value': bool(variable_get("autosync_timers"))},       
      ]
    
    list = []
    for field in fields:
      field['field'].setValue(field['value'])
      list.append(getConfigListEntry(_(field['text']), field['field'], field['name']))
      
    return list
  
  def save(self, values):
    try:
      if(values['description'] != self.__description):
        print Request().BoxEdit({'description': values['description']})
        
      #if(variable_get("autosync_timers") != values['autosync_timers']):
      #  variable_set('autosync_timers', values['autosync_timers'])
      #  config.plugins.ShareMyBox.save()
      #  configfile.save()
      
      return _('Settings saved')
    
    except Exception as e:
      return "Error:" + str(e)
          
