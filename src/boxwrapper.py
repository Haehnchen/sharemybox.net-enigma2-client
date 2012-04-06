#from ShareMyBoxRequets import ShareMyBoxApi as Request
#from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request  
#

import ShareMyBoxRequets 

from Screens.Screen import Screen

from Screens.MessageBox import MessageBox

from Components.config import config, ConfigSubsection, configfile, ConfigPassword, ConfigText, ConfigYesNo, ConfigInteger 

import os, enigma
import dreamclass
from dreamclass import UserInfo

import socket, fcntl, struct

from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_PLUGIN
from Tools.LoadPixmap import LoadPixmap

#config.plugins.ShareIt = ConfigSubsection()
#config.plugins.ShareIt.Key = ConfigText()
#config.plugins.ShareIt.privatekey = ConfigText()

config.plugins.ShareMyBox = ConfigSubsection()
#config.plugins.ShareMyBox.autosync_timers = ConfigYesNo()
#config.plugins.ShareMyBox.autosync_last = ConfigInteger(0)
config.plugins.ShareMyBox.privatekey = ConfigText()

#config.plugins.ShareMyBox.autosync_last.setValue(value)

def GetConfigDir():
  return os.path.dirname(configfile.CONFIG_FILE)
 
def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

def Icon(name):
    return LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, "Extensions/ShareMyBox/icons/" + name + ".png"))

def get_mac():
  ifnames = ["eth0", "eth1"]
  
  # tricky how to get mac
  # "from uuid import getnode as get_mac" doesnt work on newest enigma2 version because of bug during uuid import  
  for ifname in ifnames:
    try:
      return int(str(getHwAddr(ifname)).replace(':', ''), 16)
    except:
      pass
 
  return "" 

def Restart(num = 3):
  # @TODO: How reload channellist. simple quit enigma2 will replace lamedb with last backup!
  os.system('killall -9 enigma2')
  #enigma.quitMainloop(num)

def DownloadBouquetFiles(file):
  zip = GetConfigDir() + "/bouquets.zip"
  ret = ShareMyBoxRequets.ShareMyBoxApi().ChannellistGet(zip)
  dreamclass.Uncompress(zip)

def variable_get(name, default = None):
  vals = config.plugins.ShareMyBox.getSavedValue()
  if name in vals:
    return vals[name]

  return default
 
def variable_set(name, value):
  getattr(config.plugins.ShareMyBox, name).setValue(value)
  config.plugins.ShareMyBox.save()
  configfile.save()    

def RegisterMe(session, mail):
  try:  
    
    args = {}
    if mail:
      args['mail'] = mail
  
    key = SendRequest('RegisterBox', args).GetList()
    
    privatekey = str(key['privatekey'])
    boxkey = str(key['boxkey'])
    config.plugins.ShareIt.privatekey.value = privatekey
    config.plugins.ShareIt.save()
    configfile.save()  
    session.open(MessageBox, 'privatekey: %s\r\nboxkey: %s' % (privatekey, boxkey), MessageBox.TYPE_INFO)
      
  except Exception as e:
    import traceback
    print traceback.print_exc()  
  
    session.open(MessageBox, "Error:" + str(e), MessageBox.TYPE_INFO)    

def SendRequest(func, args = {}):
  #try:
  f = getattr(ShareMyBoxRequets.ShareMyBoxApi(args), func)
  return f()
  #except Exception as e:
  # import traceback
  #  print traceback.print_exc()      
  # print self.myMsg("Error:" + str(e))
  #  return f
  
 
def SendRequestAuth(func, args = {}):
  
  auth = {}
  if UserInfo().GetPrivateKey():
    auth = {'privatekey': config.plugins.ShareIt.privatekey.value}
  
  keys = dict(auth, **args)
  
  f = getattr(ShareMyBoxRequets.ShareMyBoxApi(keys), func)
  return f()
  #except Exception as e:
  # import traceback
  #  print traceback.print_exc()      
  # print self.myMsg("Error:" + str(e))
  #  return f
  
