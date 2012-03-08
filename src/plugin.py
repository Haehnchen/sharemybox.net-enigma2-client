from Plugins.Plugin import PluginDescriptor
import plugin_main

#import YourModule.YourScreen
 
def main(session, **kwargs):
  reload(plugin_main)
  try:
    session.open(plugin_main.Smb_MainMenu)
  except:
    print 'errr'  
    #import traceback
    #traceback.print_exc()
  
def Plugins(path,**kwargs):
    global plugin_path
    plugin_path = path
    return [
        PluginDescriptor(name="ShareMyBox", description="Cloud my Box",where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main),
        PluginDescriptor(name="ShareMyBox", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)
        ]
  
"""
def Plugins(**kwargs):
  return PluginDescriptor(name = "AYourPlugin",
        description = "Your test plugin",
        where = PluginDescriptor.WHERE_PLUGINMENU,
        fnc = main)
"""          