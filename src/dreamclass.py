import re, time, zipfile, tempfile, os
import boxwrapper
  
def ReadFile(filename):
  f = open(filename, "r")
  return f.read()

def GetAccess(access_flag):
  return bool(Access() & access_flag)

def getBoxKey():
  return "%x" % boxwrapper.get_mac()

class ACCESS:
  DEFAULT = 1
  REGISTERED = 2
  MARRIED = 4

def Access():
  access = ACCESS.DEFAULT
  if UserInfo().GetPrivateKey() is not False:
    access += ACCESS.REGISTERED
        
  if UserInfo().GetUid() is not None:
    access += ACCESS.MARRIED
  
  return access    
        
def GetIconPath():
  return os.path.dirname(os.path.realpath(__file__)) + '/icons/'

def GetIcon(string):
  filename = GetIconPath() + '/' + GetIconName(string)
  if os.path.exists(filename):
    return filename
  
  return GetIconPath() + 'plugin.png'


def GetIconName(string):
  if not string.endswith('.png'):
    string += '.png'
    
  return string.lower()
  
def BouqetFilesFind(bouqetfile):
    back = []

    content = ReadFile(bouqetfile)
    back[bouqetfile] = content
    
    back.append(bouqetfile)
    
    dirname = os.path.dirname(bouqetfile)
    
    if os.path.isfile(dirname + '/lamedb'):
      back.append(dirname + '/lamedb')

    for x in re.findall('FROM BOUQUET "(.*?)"', content, re.I):
      x = dirname + '/' + x
      if os.path.isfile(x):
        back[x] = ReadFile(x)
    return back
  
def Uncompress(zipfilename, delete = False):
  sourceZip = zipfile.ZipFile(zipfilename, 'r')  
  
  dest = os.path.dirname(zipfilename)
  
  for name in sourceZip.namelist():
    sourceZip.extract(name, dest)

  sourceZip.close()
  
  if delete is True:
    os.unlink(zipfilename)
  
def Compress(files):

  # open the zip file for writing, and write stuff to it
  tf = tempfile.NamedTemporaryFile(delete=False)
  tf.close()
  
  filename = tf.name + '.zip'
  
  file = zipfile.ZipFile(filename, "w")

  for name in files:
    file.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
  
  file.close()
  
  return filename
  
def BouquetsFilesFindAsArray(bouqetfile):
    back = []
    
    content = ReadFile(bouqetfile)
    back.append(bouqetfile)
    
    dirname = os.path.dirname(bouqetfile)
    
    if os.path.isfile(dirname + '/lamedb'):
      back.append(dirname + '/lamedb')
    

    for x in re.findall('1:7:1:0:0:0:0:0:0:0:(.*)', content, re.I):

      for match in re.findall('FROM BOUQUET "(.*?)"', x, re.I):
        x = match      
      
      x = dirname + '/' + x
      if os.path.isfile(x):
        back.append(x)
        
    return back    
  
def ReadFilesAsArray(ar):
    back = []
    for x in ar:
      if os.path.isfile(x):
        back[x] = ReadFile(x)
    return back
  
def format_date(unixtime, formatdate = "%m/%d/%Y %H:%M"):
  try:
    i = float(unixtime)
  except ValueError:
    return time.strftime(formatdate, time.localtime(0))
  else:
    return time.strftime(formatdate, time.localtime(i))
  
def str2bool(string):
  if isinstance(string, basestring) and string.lower() in ['0','false','no']:
    return False
  else:
    return bool(string)

def UserInfo():
  return ClassUserInfo()

class ClassUserInfo:
    """ A python singleton """
    
    class __impl:
        """ Implementation of the singleton interface """

        __privatekey = False
        __box = False
        __uid = None
          
        def SetPrivateKey(self, privatekey):
          self.__privatekey = privatekey     
          
        def GetPrivateKey(self):
          return self.__privatekey
        
        def SetBoxId(self, privatekey):
          self.__boxid = privatekey           
        
        def GetBoxId(self):
          return self.__boxid          
        
        def SetUid(self, uid):
          self.__uid = uid
          
        def GetUid(self):
          return self.__uid 
        
        def Reset(self):
          self.__privatekey = False
          self.__box = False
          self.__uid = None          

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if ClassUserInfo.__instance is None:
            # Create and remember instance
            ClassUserInfo.__instance = ClassUserInfo.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = ClassUserInfo.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

