import datetime, time, re
from xml.etree.cElementTree import parse as cet_parse
from xml.dom.minidom import parse

from ServiceReference import ServiceReference
from RecordTimer import RecordTimerEntry, RecordTimer, AFTEREVENT, parseEvent
from Components.UsageConfig import preferredInstantRecordPath, preferredTimerPath

from Components.UsageConfig import preferredInstantRecordPath, preferredTimerPath
from time import time, strftime, localtime, mktime
from xml.sax.saxutils import unescape

from Plugins.Extensions.ShareMyBox.ShareMyBoxRequets import ShareMyBoxApi as Request 
from Plugins.Extensions.ShareMyBox.boxwrapper import variable_set, variable_get

class ShareMyBoxTimerWorker(object):
  
  __recordtimer = None
  
  def __init__(self, recordtimer):
    self.__recordtimer = recordtimer
  
  def run(self):
   
    if self.need_update() is False:
      self.__updated()
      return 'No external changes'

    ext_timer = Request().RecordGet().GetList()
    recordtimer = ShareMyBoxTimer(self.__recordtimer, ext_timer)

    if recordtimer.worker() is True:
      self.__updated()
      return 'Updated'

    self.__updated()
    return 'Nothing updated'
      
  def __updated(self):
    variable_set("autosync_last", int(time()))
          
  def need_update(self):

    old = Request().RecordDetails().GetList()
    if int(old['updated_on']) == 0:
      return True

    
    last_update = int(variable_get("autosync_last", 0))
    if last_update == 0:
      return True
    
    if int(last_update - int(old['updated_on'])) <= 0:
      return True
    
    return False

class ShareMyBoxTimer(object):
  
  __recordtimer = None
  __external_timers = None
  updated = False
  log = []
  
  def __init__(self, recordtimer, external_timers):
    self.__recordtimer = recordtimer
    self.__external_timers = self.prepare_events(external_timers)
  
  def prepare_events(self, events):
    list = []
    for event in events:
      #event['begin'] = self.to_local_timestamp(event['begin'])
      #event['end'] = self.to_local_timestamp(event['end'])

      #event['begin'] = int(event['begin']) + int(self.dif_time().seconds)
      #event['end'] = int(event['end']) + int(self.dif_time().seconds)

      event['name'] = event['name'].encode('ascii', 'ignore')

      # append whitespace in description is in use
      if (event.get('description', '') != ""):
        event['description'] = event['description'] + ' '
        
      event['description'] = event.get('description', '') + '[' + event['rid'] + ']'
      list.append(event)
      
    return list  
  
  def current_ids(self):
    return self.__getids(self.timers())
  
  def external_ids(self):
    return self.__getids(self.__external_timers)  
  
  def __getids(self, timers):
    ids = []
    for event in timers:
      id = self.getid(event)
      if id != False:
        ids.append(int(id))
              
    return set(ids)  
  
  def timers(self):
    return self.__recordtimer.timer_list
  
  def is_in(self, event):
    for timer in self.__recordtimer.timer_list:
      
      if event.has_key('rid') and self.getid(timer) == event['rid']:
        return True
      
      if str(event['begin']) == str(timer.begin) and str(event['end']) == str(timer.end) and str(event['serviceref'].upper()) == str(timer.service_ref).upper():
        return True
      
    return False    
  
    
    
  def is_in_new(self, timers, timer_item):
    for timer in timers:
      if str(timer.begin) == str(timer_item['begin']):
        if str(timer.end) == str(timer_item['end']):
          if str(timer.service_ref).upper() == str(timer_item['serviceref'].upper()):
            return True
    
    return False
        
    
  
  def cleanup(self):
    newid = self.external_ids()
    oldid = self.current_ids()

    diff = list(set(oldid) - set(newid))
    
    if len(diff) == 0:
      return

    for rid in diff:
      self.__recordtimer.removeEntry(self.find_on_id(rid))
      self.updated = True
  
  def find(self, event):
    for timer in self.timers():
      
      if self.getid(timer) == timer['rid']:
        return event
      
      if str(event['begin']) == str(timer.begin) and str(event['end']) == str(timer.end) and str(event['serviceref'].upper()) == str(timer.service_ref).upper():
        return event
      
    return False     
  
  def find_on_id(self, rid):
    for timer in self.timers():
      if self.getid(timer) == rid:
        return timer
      
    return False     
  
  def getid(self, event):
    description = ''
    if isinstance(event, dict) and event.has_key('description'):
      description = event['description']
    elif hasattr(event, 'description'):
      description = event.description   
    
    matches = re.compile('\[(\d+)\]$').findall(description)
    if matches != []:
      return int(matches[0])
        
    return False    

  def sync(self):
    for ext_timer in self.__external_timers:
      if not self.is_in(ext_timer):
        self.updated = True
        self.log.append(self.editTimer(ext_timer))
        

  def worker(self):
    self.cleanup()
    self.sync()
    return self.updated
    
  def editTimer(self, param):
    print "[WebComponents.Timer] editTimer"

    #OK first we need to parse all of your Parameters
    #For some of them (like afterEvent or justplay) we can use default values
    #for others (the serviceReference or the Begin/End time of the timer
    #we have to quit if they are not set/have illegal values

    if 'serviceref' in param:
      param['sRef'] = str(param['serviceref'])

    if 'sRef' not in param:
      return ( False, "Missing Parameter: sRef" )
    service_ref = ServiceReference(param['sRef'])

    repeated = int(param.get('repeated') or 0)

    if 'begin' not in param:
      return ( False, "Missing Parameter: begin" )
    begin = int(float(param['begin']))

    if 'end' not in param:
      return ( False, "Missing Parameter: end" )
    end = int(float(param['end']))

    tm = time()
    if tm <= begin:
      pass
    elif tm > begin and tm < end and repeated == 0:
      begin = time()
    elif repeated == 0:
      return ( False, "Illegal Parameter value for Parameter begin : '%s'" % begin )

    if 'name' not in param:
      return ( False, "Missing Parameter: name" )
    name = param['name']

    if 'description' not in param:
      return ( False, "Missing Parameter: description" )
    description = param['description'].replace("\n", " ")

    disabled = False #Default to: Enabled
    if 'disabled' in param:
      if param['disabled'] == "1":
        disabled = True
      else:
        #TODO - maybe we can give the user some useful hint here
        pass

    justplay = False #Default to: Record
    if 'justplay' in param:
      if param['justplay'] == "1":
        justplay = True

    afterEvent = 3 #Default to Afterevent: Auto
    if 'afterevent' in param:
      if (param['afterevent'] == "0") or (param['afterevent'] == "1") or (param['afterevent'] == "2"):
        afterEvent = int(param['afterevent'])

    dirname = preferredTimerPath()
    if 'dirname' in param and param['dirname']:
      dirname = param['dirname']

    tags = []
    if 'tags' in param and param['tags']:
      tags = unescape(param['tags']).split(' ')

    delold = 0
    if 'deleteOldOnSave' in param:
      delold = int(param['deleteOldOnSave'])

    #Try to edit an existing Timer
    if delold:
      if 'channelOld' in param and param['channelOld']:
        channelOld = ServiceReference(param['channelOld'])
      else:
        return ( False, "Missing Parameter: channelOld" )
      # We do need all of the following Parameters, too, for being able of finding the Timer.
      # Therefore so we can neither use default values in this part nor can we
      # continue if a parameter is missing
      if 'beginOld' not in param:
        return ( False, "Missing Parameter: beginOld" )
      beginOld = int(param['beginOld'])

      if 'endOld' not in param:
        return ( False, "Missing Parameter: endOld" )
      endOld = int(param['endOld'])

      #let's try to find the timer
      try:
        for timer in self.__recordtimer.timer_list + self.__recordtimer.processed_timers:
          if str(timer.service_ref) == str(channelOld):
            if int(timer.begin) == beginOld:
              if int(timer.end) == endOld:                
                #we've found the timer we've been searching for                
                
                #Delete the old entry
                self.__recordtimer.removeEntry(timer)
                old = timer
                
                timer = RecordTimerEntry(service_ref, begin, end, name, description, 0, disabled, justplay, afterEvent, dirname=dirname, tags=tags)
                timer.repeated = repeated
                timer.log_entries = old.log_entries                
                
                timer.processRepeated()                
                #send the changed timer back to enigma2 and hope it's good
                
                conflicts = self.__recordtimer.record(timer)
                if conflicts is None:
                  print "[WebComponents.Timer] editTimer: Timer changed!"
                  return ( True, "Timer '%s' changed" %(timer.name) )
                else:
                  print "[WebComponents.Timer] editTimer conflicting Timers: %s" %(conflicts)
                  msg = ""
                  for timer in conflicts:
                    msg = "%s / %s" %(msg, timer.name)        
                    
                  return (False, "Conflicting Timer(s) detected! %s" %(msg)) 

      except Exception:
        #obviously some value was not good, return an error
        return ( False, "Changing the timer for '%s' failed!" % name )

      return ( False, "Could not find timer '%s' with given start and end time!" % name )

    #Try adding a new Timer

    try:
      #Create a new instance of recordtimerentry
      timer = RecordTimerEntry(service_ref, begin, end, name, description, 0, disabled, justplay, afterEvent, dirname=dirname, tags=tags)
      timer.repeated = repeated
      #add the new timer
      conflicts = self.__recordtimer.record(timer)
      if conflicts is None:
        return ( True, "Timer '%s' added" %(timer.name) )
      else:
        print "[WebComponents.Timer] editTimer conflicting Timers: %s" %(conflicts)
        msg = ""
        for timer in conflicts:
          msg = "%s / %s" %(msg, timer.name)        
          
        return (False, "Conflicting Timer(s) detected! %s" %(msg)) 
        
    except Exception, e:
      #something went wrong, most possibly one of the given paramater-values was wrong
      print "[WebComponents.Timer] editTimer exception: %s" %(e)
      return ( False, "Could not add timer '%s'!" % name )

    return ( False, "Unexpected Error" )

class ShareMyBoxTimerOld(object):
  
  __timer_filename = ''
  __requested_items = []
  __items_convert = []
  __timers = []
  
  def __init__(self, timer_filename, requested_items):
    self.__timer_filename = timer_filename
    self.__requested_items = requested_items
    
    self.__items_convert = self.prepare_events()
    self.__timers = self.read_timers()

  def read_timers(self):
    configuration = cet_parse(self.__timer_filename).getroot()
    timers = []
    for timer in configuration.findall("timer"):
      timers.append(timer.attrib)
  
    return timers
    
  def parser_iso_8601_date(self, s):
      # @TODO: handle hour diff
      s = s.replace('+00:00', '')
      return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S" )
  
  def dif_time(self):
      return -(datetime.datetime.utcnow() - datetime.datetime.now())
  
  def gmt_datetime_to_unixstamp_local(self, dtime):
      return int(time.mktime(dtime.timetuple())) + self.dif_time().seconds
  
  def to_local_timestamp(self, s):
      return self.gmt_datetime_to_unixstamp_local(self.parser_iso_8601_date(s))
  
  def prepare_events(self):
    list = []
    for event in self.__requested_items:
      #event['begin'] = self.to_local_timestamp(event['begin'])
      #event['end'] = self.to_local_timestamp(event['end'])

      event['begin'] = int(event['begin']) + int(self.dif_time().seconds)
      event['end'] = int(event['end']) + int(self.dif_time().seconds)

      if (event.get('description', '') != ""):
        event['description'] = event['description'] + ' '
        
      event['description'] = event.get('description', '') + '[' + event['rid'] + ']'
      list.append(event)
      
    return list
  
  def sync(self):
    new = []
    for event in self.__items_convert:
      if self.is_in(event) is False:
        self.__timers.append(event)
  
  def cleanup(self):
    newid = self.getids(self.__items_convert)
    oldid = self.getids(self.__timers)

    diff = list(set(oldid) - set(newid))
    
    if len(diff) == 0:
      return

    for id in diff:
      self.deleteid(id)
  
  def deleteid(self, id):
    for index, event in enumerate(self.__timers):
      eid = self.getid(event)
      if eid != False and id == eid:
        del self.__timers[index]
  
  def need_update(self):
    
    newid = self.getids(self.__items_convert)
    oldid = self.getids(self.__timers)
    
    ids = set(set(newid) & set(newid))
    if len(ids) != len(oldid):
      return True
    
    for event in self.__items_convert:
      if self.is_in(event) is False:
        return True
  
    return False
  
  def is_in(self, timer):
    for event in self.__timers:
      
      # no used; timer worker filter out unknown attributes
      if timer.has_key('rid') and event.has_key('rid') and event['rid'] == timer['rid']:
        return True
      
      if str(event['begin']) == str(timer['begin']) and str(event['end']) == str(timer['end']) and str(event['serviceref'].upper()) == str(timer['serviceref'].upper()):
        return True
      
    return False
      
  def remove_whitespace(self, txt):
      return '\n'.join([x for x in txt.split("\n") if x.strip()!=''])
    
  def formated_output(self, dom):
    str1 = dom.toprettyxml(indent=" ", newl = "\n", encoding = "utf-8")
    str1 = self.remove_whitespace(str1)
    
    f = open(self.__timer_filename, 'w')
    f.write(str1)
    f.close()
    
  def arraytoxml(self):
    dom = parse(self.__timer_filename)
  
    main=dom.childNodes[0]
    # @TODO: remove clean old timer list; or use enigma Timer funcs
    for node in dom.getElementsByTagName('timer'):
      node.normalize()
      main.removeChild(node)
      
    for item in self.__timers:
      x = dom.createElement("timer")
  
      for key,value in item.items():
        if not isinstance(value, basestring):
          value = str(value)
        
        x.setAttribute(key, value)
        
      dom.childNodes[0].appendChild(x)
    
    self.formated_output(dom)
    
  def getids(self, timers):
    ids = []
    for event in timers:
      id = self.getid(event)
      if id != False:
        ids.append(int(id))
              
    return ids

  def getid(self, event):
      matches = re.compile('\[(\d+)\]$').findall(event['description'])
      if matches != []:
        return int(matches[0])
      elif event.has_key('rid'):
        return int(event['rid'])
        
      return False    
    
  def worker(self):
    if self.need_update() is True:
      self.cleanup()
      self.sync()
      self.arraytoxml()
      
      print "New timer added"
      return True
    
    return False