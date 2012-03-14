import datetime, time
from xml.etree.cElementTree import parse as cet_parse
from xml.dom.minidom import parse
from Components.TimerList import TimerList

def readxml(filename):
  configuration = cet_parse(filename).getroot()
  timers = []
  for timer in configuration.findall("timer"):
    timers.append(timer.attrib)

  return timers
  
def parser_iso_8601_date(s):
    s = s.replace('+00:00', '')
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S" )

def dif_time():
    return -(datetime.datetime.utcnow() - datetime.datetime.now())

def gmt_datetime_to_unixstamp_local(dtime):
    return int(time.mktime(dtime.timetuple())) + dif_time().seconds

def to_local_timestamp(s):
    return gmt_datetime_to_unixstamp_local(parser_iso_8601_date(s))

def convert_events_date(events):
  list = []
  for event in events:
    event['begin'] = to_local_timestamp(event['begin'])
    event['end'] = to_local_timestamp(event['end'])
    list.append(event)
    
  return list    

def sync(timer, ext):
  new = []
  for event in timer:
    if not (event.has_key('smb') and event['smb'] is "1"):
      new.append(event)

  return new + ext;
    
def remove_whitespace(txt):
    return '\n'.join([x for x in txt.split("\n") if x.strip()!=''])  
  
def formated_output(filename, dom):  
  str1 = dom.toprettyxml(indent="  ", newl = "\n", encoding = "utf-8")
  str1 = remove_whitespace(str1)
  
  f = open(filename, 'w')
  f.write(str1)
  f.close()   
  
def arraytoxml(filename, items):
  dom = parse(filename)

  main=dom.childNodes[0]
  for node in dom.getElementsByTagName('timer'):  # visit every node <bar />
    node.normalize()
    main.removeChild(node)
    
  for item in items:
    x = dom.createElement("timer")

    for key,value in item.items():
      if not isinstance(value, basestring):
        value = str(value)
      
      x.setAttribute(key, value)
      
    dom.childNodes[0].appendChild(x)
  
  formated_output(filename, dom)
  
def worker(timerfile, events):
  timer = readxml(timerfile)
  events = convert_events_date(events)
  items = sync(timer, events)
  arraytoxml(timerfile, items)
    
  