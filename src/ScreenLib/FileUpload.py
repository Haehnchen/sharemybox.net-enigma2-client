from Components.FileList import FileList
from Components.ActionMap import ActionMap

from BaseScreens import Smb_BaseScreen
from Components.Label import Label

import os

LAST_DIR = '/'

class MainMenu(Smb_BaseScreen):
  skin = """
     <screen position="center,center" size="550,400" title="Test" >
       <widget name="list" position="10,0" size="500,300" scrollbarMode="showOnDemand" />

       <widget name="red" position="10,320" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
       <widget name="green" position="140,320" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
       <widget name="yellow" position="270,320" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
       <widget name="blue" position="400,320" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
      
       <ePixmap name="pred" position="10,320" size="120,30" zPosition="0" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
       <ePixmap name="pgreen" position="140,320" size="120,30" zPosition="0" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on"/>
       <ePixmap name="pyellow" position="270,320" size="120,30" zPosition="0" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on"/>
       <ePixmap name="pblue" position="400,320" size="120,30" zPosition="0" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on"/>
      
     </screen>
     """

  max_filesize = 209715
    
  def build(self):
    self["list"] = FileList("/")
    self["red"] = Label("/var")
    self["green"] = Label("/var")
    self["yellow"] = Label("/etc/enigma2")
    self["blue"] = Label("/var/keys")    
    

    self.actions['red'] = lambda: self.changedir('/')
    self.actions['green'] = lambda: self.changedir('/var')
    self.actions['yellow'] = lambda: self.changedir('/etc/enigma2')
    self.actions['blue'] = lambda: self.changedir('/var/keys')
    
    self.context = ["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"]
          
  def ok(self):
    # from Plugin: Filebrowser
    self.SOURCELIST = self["list"]
    if self.SOURCELIST.canDescent(): # isDir
      self.SOURCELIST.descent()
      global LAST_DIR
      LAST_DIR = self.SOURCELIST.getCurrentDirectory()
      if self.SOURCELIST.getCurrentDirectory(): #??? when is it none
        self.setTitle(self.SOURCELIST.getCurrentDirectory())
    else:
      filename = str(self.SOURCELIST.getCurrentDirectory() + self.SOURCELIST.getFilename())
      self.onFileAction(filename)    
    
  def onFileAction(self, filename):
    try:
      if os.path.getsize(filename) > self.max_filesize:
        self.myMsg(_("File is too big"))
        #self.close(False)
        return
      
      #test = Request()
      #resp = str(test.UploadFile(filename))    
      
      #self.myMsg(resp)
      self.close(filename)
    
    except Exception as e:
      #print self.myMsg("Error:" + str(e))
      #self.close(False, "Error:" + str(e))
      pass      
    
  def layoutFinished(self):
    self.changedir(LAST_DIR)
    
  def changedir(self, dirname):
    if not os.path.exists(dirname):
      self.myMsg('dir %s not found' % dirname)
      return
      
    self["list"].changeDir(dirname)
