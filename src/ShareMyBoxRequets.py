import urllib, urllib2
import simplejson as json
import os
import base64

import locale

import re
import sys

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from boxwrapper import get_mac
from dreamclass import UserInfo

API_PATH = 'http://api.sharemybox.net/'

VERSION = "1.0"

class ShareMyBoxApi(object):
  __auth = {}
  __base_url = API_PATH
  __reg = None

  # old one  
  __ops = {
    #'GetPrivateKey': 'user/GetPrivateKey',
  }
  
  def __init__(self, autharray = {}):
    self.__auth = dict(autharray, **self.__auth)
    self.__reg = ShareMyBoxApiRequest(self.__auth)
    
  def AddAuthData(self, variable, value):
    self.__auth[variable] = value

  def GeneratePrivateKey(self): return self.Call()
  def FileList(self): return self.Call()   
  def FileAvailable(self): return self.Call()
  def ActionList(self): return self.Call()
  def FriendList(self): return self.Call()
  def ChannellistAvailable(self): return self.Call()
  def BoxDetails(self): return self.Call()
  def ChannellistList(self): return self.Call()
  def RecordGet(self): return self.Call()
  def RecordDetails(self): return self.Call()
  def BoxRegister(self): return self.Call(False)

      
  def GetPrivateKey(self):
    if self.__auth.has_key('user') and self.__auth.has_key('password'):
      return self.Call()

  def BoxMarry(self, search):
    self.__reg.AddVariable("search", search)
    return self.Call()
  
  def BoxRegistersafe(self, search):
    self.__reg.AddVariable("search", search)
    return self.Call()  

  def FriendAdd(self, search):
    self.__reg.AddVariable("search", search)
    return self.Call()

  def FriendDelete(self, sid):
    self.__reg.AddVariable("sid", sid)
    return self.Call()

  def FileDetails(self, fid):
    self.__reg.AddVariable("fid", fid)
    return self.Call()
  
  def FileAdd(self, files):
    self.__reg.AddVariable('filename', files[0])
    self.__reg.AddFiles(files)
    return self.Call()     
  
  def FileDelete(self, fid):
    self.__reg.AddVariable("fid", fid)    
    return self.Call()    
  
  def FileEdit(self, fid, values):
    self.__reg.AddVariables(values)
    self.__reg.AddVariable("fid", fid)    
    return self.Call()  
  
  def BoxEdit(self, values):
    self.__reg.AddVariables(values)
    return self.Call()    
  
  def ChannellistUpload(self, oid, files):
    self.__reg.AddFiles(files)
    self.__reg.AddVariable("cid", oid)    
    return self.Call()     
  
  def FileUpload(self, fid, files):
    self.__reg.AddVariable('filename', files[0])    
    self.__reg.AddFiles(files)
    self.__reg.AddVariable("fid", fid)    
    return self.Call()    
  
  def FileDownload(self, fid):
    url = self.__GetOpBy(sys._getframe(0).f_code.co_name)
    info = self.FileDetails(fid).GetList()
    to = info['name']
    
    if not os.path.isdir(os.path.dirname(to)):
      os.makedirs(os.path.dirname(to))
    
    return self.__reg.Download(url = url, to = to)        
  
  def ChannellistDownload(self, cid, to):
    url = self.__GetOpBy(sys._getframe(0).f_code.co_name)
    print url
    #url += "/" + file
    
    self.__reg.AddAuth()    

    self.__reg.AddVariable("cid", cid)
    return self.__reg.Download(url = url, to = to)    
  
  def BouquetGetfile(self, cid, file, to):
    url = self.__GetOpBy(sys._getframe(0).f_code.co_name)
    url += "/" + file
    
    self.__reg.AddAuth()    

    self.__reg.AddVariable("cid", cid)
    self.__reg.AddVariable("file", file)
    return self.__reg.Download(url = url, to = to)   
  
  def ChannellistEdit(self, oid, values):
    self.__reg.AddVariables(values)
    self.__reg.AddVariable("cid", oid)    
    return self.Call() 
  
  def ChannellistDelete(self, cid):
    self.__reg.AddVariable("cid", cid)    
    return self.Call()   

  def BouquetListfiles(self, cid):
    self.__reg.AddVariable("cid", cid)    
    return json.loads(self.Call().GetList()) 

  def ChannellistAdd(self, name):
    self.__reg.AddVariable("name", name)
    return self.Call()

  def ChannellistDetails(self, oid):
    self.__reg.AddVariable("cid", oid)    
    return self.Call()   
  
  def BouquetAdd(self, name):
    self.__reg.AddVariable("name", name)
    return self.Call()
  
  def BouquetDelete(self, oid):
    self.__reg.AddVariable("oid", oid)
    return self.Call()  
  
  def UploadBouquets(self, bid, filesarray):
    self.__reg.AddFiles(filesarray)
    self.__reg.AddVariable('oid', bid)
    return self.Call() 
  
  def AddParentBox(self, args):
    self.__reg.AddVariables(args)
    return self.Call()

  def ActionPerform(self, actionkey):
    self.__reg.AddVariable('actionkey', actionkey)
    return self.Call() 
  
  def ActionDelete(self, actionkey):
    self.__reg.AddVariable('actionkey', actionkey)
    return self.Call()   
  
  def UploadFile(self, filename, base64decode = 0):
    self.__reg.AddFile(filename)
    return self.Call()   
  
  
  def Call(self, auth = True):
    url = self.__GetOpBy(sys._getframe(1).f_code.co_name)
    print url
    if(auth == True):
      self.__reg.AddAuth()
      
    return self.__reg.Request(url)
  
  def Debug(self, filename, base64decode = 0):
    self.__reg.AsMultipart()
    self.__reg.AddFile("bouquets.tv")
    self.__reg.AddFile(filename)

    return self.Call()  
   
  def __GetOpBy(self, func):
    if self.__ops.has_key(func):
      url = self.__ops[func]
    else:
      url = re.sub('[A-Z]', '/\g<0>', func).strip('/').lower()
    return self.__base_url + url

class ShareMyBoxApiRequest(object):
  __request = {}
  __debug_url = API_PATH
  __headers = {}
  __multipart = False

  debug = 1 

  def __init__(self, request = {}, auth = 0):
    mac = get_mac()
    if mac is None:
      raise Exception("Can not get your box mac")

    self.__boxid = "%x" % mac
    self.__request['boxid'] = self.__boxid
    self.__GetUserAgent()
    self.__GetLanguage()
    self.__request  = dict(request, **self.__request)
    self.__response = ''

    if auth == 1:
      self.AddAuth()
      
  def GetBoxId(self):
    return self.__boxid
  
  def GetResponse(self):
    return str(self.__response['response'])
  
  def GetList(self):
    return self.__response['response']
  
  def Debug(self, string):
    print string  
  
  def __str__(self):
    return self.GetResponse();
  
  def AsMultipart(self):
    self.__multipart = True
    return self   
  
  def DebugRequest(self):
    params = urllib.urlencode(self.__request)    
    req = urllib2.Request(self.__debug_url, params, self.__headers)

    return urllib2.urlopen(req).read()
  
  def Request(self, url, paramter = {}):
    params = dict(paramter, **self.__request)
             
    if self.__multipart == True:
      register_openers()
      #pprint.pprint(params)
      datagen, headers = multipart_encode(params)
      req = urllib2.Request(url, datagen, dict(headers, **self.__headers))
    else:
      req = urllib2.Request(url, urllib.urlencode(params), self.__headers)

    ## read http error codes
    content = str(urllib2.urlopen(req).read())
    
    #content = content.encode("utf-8")
    
    if self.debug == 1:
      self.Debug(content) 
            
    self.__response = json.loads(content)

    if self.__response['code'] != 0:
      raise Exception(self.__response['response'])
    
    if self.__response['type'] == 'list':
      self.__response['response'] = json.loads(self.__response['response'])

    return self
  
  def Download(self, url, paramter = {}, to = None):
    params = dict(paramter, **self.__request)
             
    req = urllib2.Request(url, urllib.urlencode(params), self.__headers)

    fout = open(to, "wb")
    fout.write(urllib2.urlopen(req).read())
    fout.close()

    return self  
  
  def AddFile(self, filename, as_multipart = True):
    if as_multipart == False and self.__multipart == False:
      self.__request['files'] = json.dumps({filename: open(filename, "r").read()})
    else:
      self.__multipart = True
      self.__request.setdefault('path', []).append({os.path.basename(filename): filename})
      #self.__request.setdefault('filename', []).append([filename])
      self.__request[filename] = open(filename, "rb")
        
  
  def AddFiles(self, filesarray, as_multipart = True):
    for file in filesarray:
      self.AddFile(file, as_multipart)
    
  def AddFilePut(self, filename, base64decode = 0):
    array = {'content': open(filename, "r").read()}
    if (base64decode == 1):
      array['content'] = base64.encodestring(array['content'])
      array['base64'] = 1
      
  def AddAuth(self):
    if UserInfo().GetPrivateKey():
      self.AddVariable('privatekey', UserInfo().GetPrivateKey())
    
  def AddVariable(self, variable, value):
    if isinstance(value, dict):
      value = json.dumps(value)

    self.__request[variable] = value

  def AddVariables(self, array):
    self.__request = dict(array, **self.__request)
    
  def __GetUserAgent(self):
    
    agents = {}
    agents["ShareMyBox"] = VERSION

    
    if hasattr(os,'uname'):
      agents["ShareMyBox"] += ' (%s)' % str(os.uname()).replace('(','').replace(')','')
      
    try:
      from Components.About import about
      agents["Enigma2"] = about.getEnigmaVersionString()
      agents["Image"] = about.getImageVersionString()
    except:
      pass      

    self.__headers['User-Agent'] = ''      
    for key, value in agents.iteritems():
      self.__headers['User-Agent'] += '%s/"%s" ' % (key, value)
      
    self.__headers['User-Agent'] = self.__headers['User-Agent'].strip()

  def __GetLanguage(self):
    self.__headers['Accept-Language'] = "en-US"
    loc, enc = locale.getdefaultlocale()
    if not loc is None:
      self.__headers['Accept-Language'] = loc    
      
      

    

    
    
      
    
    
    
    
    