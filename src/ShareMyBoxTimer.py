import datetime, time, re
from xml.etree.cElementTree import parse as cet_parse
from xml.dom.minidom import parse

from ServiceReference import ServiceReference
from RecordTimer import RecordTimerEntry, RecordTimer, AFTEREVENT, parseEvent

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
        self.log.append(self.addTimer(ext_timer))
        

  def worker(self):
    self.cleanup()
    self.sync()
    return self.updated
    
  def addTimer(self, timer):
    try:
      name = str(timer['name'])
      description = str(timer['description'])
      begin = int(timer['begin'])
      end = int(timer['end'])
      serviceref = ServiceReference(str(timer['serviceref']))
      eit = "54618"

      begin = "1332621900"
      end = "1332622200"
      name = "Ziehung der Lottozahlen"
      serviceref = ServiceReference("1:0:19:2B5C:3F3:1:C00000:0:0:0:")
    
    #afterevent="auto" eit="54618" location="/hdd/movie/" tags="" disabled="0" justplay="0">


      timer = RecordTimerEntry(serviceref, begin, end, name, description, eit)
      timer.repeated = 0
      
      conflicts = self.__recordtimer.record(timer, ignoreTSC=True)
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
      return ( False, "Could not add timer '%s'!" % e )

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