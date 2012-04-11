from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox

from Components.Label import Label

import os,inspect
from Plugins.Extensions.ShareMyBox.__init__ import _


class Smb_BaseScreen(Screen):
  actions = None
  session = None
  context = ["SetupActions"]
  args = 0
  title = None
 
  skin = """
    <screen position="center,center" size="460,400" title="MainMenu" >
      <widget name="myMenu" position="10,10" size="420,380" scrollbarMode="showOnDemand" />
      <widget name="Statusbar" position="10,390" size="530,20" font="Regular;12"/>      
    </screen>"""
  
  def __init__(self, session, args = 0):
    self.session = session
    self.args = args

    self.actions = {
      "ok": self.ok,
      "cancel": self.cancel,
      "back": self.cancel,
    }
      
    # load xml skin on file
    classparentmodule = os.path.splitext(os.path.basename(inspect.getsourcefile(self.__class__)))[0]
    filename = os.path.dirname(os.path.realpath(__file__)) + "/" + classparentmodule + self.__class__.__name__ + ".xml"
    if os.path.exists(filename):
      self.skin = open(filename, "r").read()

    self.build()
    self.run()
  
  def ErrorException(self, exception):
    #print str(exception)
    self.SetMessage(str(exception))
    #print str(exception)
    #self.myMsg(str(exception))
  
  def __MenuChanged(self):
    item = self["myMenu"].l.getCurrentSelection()
    if item is None: return
    self.onMenuChanged(item)
  
  def run(self):
    self.actions = ActionMap(self.context, self.actions, -1)       
    self["myActionMap"] = self.actions
    
    if not self.has_key("Statusbar"):
      self["Statusbar"] = Label("")
    
    Screen.__init__(self, self.session)

    if hasattr(self.__class__, 'onMenuChanged'):
      self["myMenu"].onSelectionChanged = [self.__MenuChanged]
      self.__MenuChanged()
    
    self.onLayoutFinish.append(self.__layoutFinished)
  
  def __layoutFinished(self):
    title = "ShareMyBox"
    if self.title is None: 
      self.setTitle(title + " - " + self.__class__.__name__)
    else:
      self.setTitle(title + " - " + self.title)

    if hasattr(self.__class__, 'layoutFinished'):
      self.layoutFinished()

  def build(self):
    pass
  
  def ok(self):
    pass
  
  def rebuild(self):
    self["myMenu"].setList(self.buildlist())
      
  def Id(self):
    selc = self.CurrentSelection()
    if selc is None:
      return None
    
    return selc[0]
  
  def is_selected(self):
    if self.Id() is None:
      self.SetMessage(_('Please select one item'))
      return False
    
    return True
  
  def CurrentSelection(self):
    return self["myMenu"].l.getCurrentSelection()    
  
  def myMsg(self, entry):
    self.session.open(MessageBox, entry, MessageBox.TYPE_INFO)  

  def cancel(self):
    self.close()

  def SetMessage(self, msg):
    if not self.has_key("Statusbar"):
      self["Statusbar"] = Label("")    

    self["Statusbar"].text = str(msg)
    
    
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen, ConfigList

class Smb_BaseEditScreen(ConfigListScreen, Screen):
  keyid = None
  args = None
  
  skin = """
    <screen name="ConfigListScreen" position="center,center" size="560,400" title="ShareMyBox - Settings">
      <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
      <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
      <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
      <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
      <widget name="config" position="5,50" size="550,360" scrollbarMode="showOnDemand" zPosition="1"/>
    </screen>"""

  def __init__(self, session, args=None):
    Screen.__init__(self, session)
    ConfigListScreen.__init__(self, [])    
    self.args = args
        
    self["key_red"] = StaticText(_("Cancel"))
    self["key_green"] = StaticText(_("OK"))
    # SKIN Compat HACK!
    self["key_yellow"] = StaticText("")
    # EO SKIN Compat HACK!
    self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
    {
      "red": self.cancel,
      "green": self.__SaveValues,
      "save": self.__SaveValues,
      "cancel": self.cancel,
      "ok": self.__SaveValues,
    }, -2)
        
    self.build()
    self.run()    
  
  def run(self):
    try:
      mylist = self.buildlist()
      self["config"].list = mylist;
    except Exception as e:
      print str(e)
      self.close(str(e))
      return      

  
  def keyLeft(self):
    ConfigListScreen.keyLeft(self)
    #self.createSetup()

  def keyRight(self):
    ConfigListScreen.keyRight(self)
    #self.createSetup()
    
  def build(self):
    pass    
    
  def buildlist(self):
    pass
    
  def layoutFinished(self):
    pass
    #self.setTitle(_("Webinterface: Main Setup"))
    
  def save(self):
    pass

  def __SaveValues(self):
    values = {}
    for x in self["config"].list:
      values[x[2]] = x[1].getValue()

    result = self.save(values)
    self.close(result) 

  def cancel(self):
    self.close() 
    
  def SetId(self, value):
    self.keyid = value         

    
class Smb_BaseListScreen(Smb_BaseScreen):
  skin ="""
       <screen position="center,center" size="630,450" title="">
            <widget name="myMenu" enableWrapAround="1" position="10,10" size="370,380" scrollbarMode="showOnDemand" />

            <widget name="Description" position="402,10" size="230,380" font="Regular;18"/>
      
                    
            <widget name="red" position="10,394" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
            <widget name="green" position="140,394" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
            <widget name="yellow" position="270,394" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>
            <widget name="blue" position="400,394" size="120,30" valign="center" halign="center" zPosition="1" transparent="1" foregroundColor="white" font="Regular;18"/>

            <ePixmap name="pred" position="10,392" size="120,30" zPosition="0" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
            <ePixmap name="pgreen" position="140,392" size="120,30" zPosition="0" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on"/>
            <ePixmap name="pyellow" position="270,392" size="120,30" zPosition="0" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on"/>
            <ePixmap name="pblue" position="400,392" size="120,30" zPosition="0" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on"/>
            
            <ePixmap name="padd" position="530,397" size="120,30" zPosition="0" pixmap="skin_default/buttons/key_0.png" transparent="1" alphatest="on"/>
            <eLabel name="padd_label" text="Add" position="570,397" size="50,25" font="Regular;19" transparent="1" />
            
            <widget name="Statusbar" position="10,433" size="610,20" font="Regular;14"/>
            
            <eLabel backgroundColor="#808080" position="391,0" size="1,390" />            
            <eLabel backgroundColor="#808080" position="0,390" size="630,1" />
            <eLabel backgroundColor="#808080" position="0,428" size="630,1" />         
        </screen>  
  """    
  
  def DescriptionToText(self, items):
    text = ""
    for key, value in items.items():
      value = str(value)
      if len(value) > 0 and not value is "None":
        text = text + "%s:\n%s\n\n" % (key, value)

    self["Description"].setText(text)   