import sys, re, pymongo, json
import requests

jsonDict = {}

client = pymongo.MongoClient (host="da0.eecs.utk.edu")
# Get a reference to a particular database
db = client ['bitbucket']
# Reference a particular collection in the database
coll = db ['repos']


#do for forks, watchers, commits, clone, pullrequests
collName = 'pullrequests'
if (len (sys .argv) > 1): 
  collName = sys .argv [1] 

def chunks(l, n): 
  if n < 1: n = 1 
  return [l[i:i + n] for i in range(0, len(l), n)] 

f = open ('repos5.todo')
coll1 = db [collName]
for n in f:    
  n = n .rstrip ()
  r = coll .find_one ({ "full_name" : n },  { "links" : 1 })
  if r == None:
    continue
  id = r ['_id']
  url = r ['links'][collName]['href']
  url1 = url + "/?pagelen=50"
  v = []
  size = 0 
  while True:
    try: 
      r = requests.get (url1)
      t = r.text
      jsonDict = json.loads (t) 
      if ('values' in jsonDict):
        for el in jsonDict ['values']:
          v. append (el)
          size += sys .getsizeof (el)
      if 'next' not in jsonDict: 
        print str (len (v)) + ';' + str (size) + ';' + url1
        sys .stdout .flush ()
        break
      else: url1 = jsonDict['next']
      print str (len (v)) + ';' + str (size) + ';' + url1
      sys .stdout .flush ()
    except Exception as e:
      print "Could not get:" 
      print url 
      print e
      sys .stdout .flush ()
      break
  if len (v) > 0:
    # size may be bigger in bson, factor of 2 doesnot always suffice    
    if (size < 16777216/3):
      coll1.insert ( { 'url': url, 'parent': id, 'values': v } ) 
    else:
      s = size;
      n = 3*s/16777216
      i = 0 
      for ch in chunks (v, n): 
        coll1.insert ( { 'chunk': i, 'url': url, 'parent': id, 'values': ch } ) 
        i = i + 1 

