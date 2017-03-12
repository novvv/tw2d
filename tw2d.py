import json, base64, urllib2, json
import requests

from_url='https://usalaunchpad.teamwork.com/desk/#settings/users/100123/apikeys'
api_key='9Af3HSxEgkmEXNKIjAH5sgM5cUpHcrlqVDtlEqmuTKza3XVqP'
up='admin@terranovalaunchpad.com:Werbert456!'

#base='https://desk.com/api/v2/'
base_desk='https://clientsupport.desk.com/api/v2/'
base_team='https://usalaunchpad.teamwork.com/'
username='admin@terranovalaunchpad.com'
password='Werbert456!'
#url=base+'groups'
site='294095'
credentials = '{username}:{password}'.format(**vars()).encode()
from urllib2 import Request, urlopen
#urlopen(Request(url, headers={'Authorization': b'Basic ' + base64.b64encode(credentials)})).close()

art1='https://clientsupport.desk.com/api/v2/articles'
base64string = base64.b64encode('%s:%s' % (username, password))

def desk(q,data=None):
    url=base_desk+q
    print url
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept':'application/json',
       'Accept-Charset': 'utf-8',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive',
       'Content-Type': 'application/json',
       "Authorization": "Basic %s" % base64string
       }    
    request=urllib2.Request(url,headers=hdr)
    try:
        if data:
            response=urllib2.urlopen(request, json.JSONEncoder().encode(data))
            text=response.read()
            return json.JSONDecoder().decode(text)
        else:
            response=urllib2.urlopen(request)
            text=response.read()
            return json.JSONDecoder().decode(text)
    except urllib2.HTTPError, e:
        print e.fp.read()
    return None

def team(q,data=None):
    url=base_team+q
    print url
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept':'application/json',
       'Accept-Charset': 'utf-8',
       'Content-Type': 'application/json',
       "Authorization": "BASIC " + base64.b64encode(api_key + ":xxx")
       }    
    request=urllib2.Request(url,headers=hdr)
    try:
        if data:
            response=urllib2.urlopen(request, json.JSONEncoder().encode(data))
            text=response.read()
            return json.JSONDecoder().decode(text)
        else:
            response=urllib2.urlopen(request)
            text=response.read()
            return json.JSONDecoder().decode(text)
    except urllib2.HTTPError, e:
        print e.fp.read()
    return None

if __name__=='__main__':
    print 'Teamwork to Desk import tool'
    
    print team('projects.json')
    
    
    print desk('users/current')
    email="novvvster@gmail.com"
    case= { "type":"email","subject":"Phone Case Subject","priority":4,"status":"open","labels": ["Spam", "Ignore"],"message":{"from":"novvvster@gmail.com","to":username,"cc":username,"bcc":username,"direction": "in", "body": "Example body"},"_links":{"assigned_group":{"class":"group","href":"/api/v2/groups/1"}}
    }
    print desk('cases',case)
    
    
    


