#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json, base64, urllib2, json
import re,sys,time



#base='https://desk.com/api/v2/'

from settings import *

from urllib2 import Request, urlopen
#urlopen(Request(url, headers={'Authorization': b'Basic ' + base64.b64encode(credentials)})).close()

base64string = base64.b64encode('%s:%s' % (username, password))

def desk(q,data=None,method='GET'):
    url=base_desk+q
    print url
    

    #User=username
    #Pass=password
    base64string = base64.encodestring('%s:%s' % (User, Pass)).replace('\n', '')
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
    if data and method=='GET':
        method='POST'
    request.get_method = lambda: method
    try:
        if data:
            response=urllib2.urlopen(request, json.JSONEncoder().encode(data))
            text=response.read()
            return json.JSONDecoder().decode(text)
        else:
            response=urllib2.urlopen(request)
            text=response.read()
            return json.JSONDecoder().decode(text)
    #try:
     #   pass
    except Exception as e: #urllib2.HTTPError, e:
        print e.fp.read()
    return None

def team(q,data=None):
    url=base_team+q
    print url
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept':'application/json',
       'Accept-Charset': 'utf-8',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive',
       'Content-Type': 'application/json',
       #"Authorization": "Basic %s" % base64string
       "Authorization": "BASIC " + base64.b64encode(api_key + ":xxx")
       }    
    request=urllib2.Request(url,headers=hdr)
    if 1:
        if data:
            response=urllib2.urlopen(request, json.JSONEncoder().encode(data))
            text=response.read()
            return json.JSONDecoder().decode(text)
        else:
            response=urllib2.urlopen(request)
            text=response.read()
            return json.JSONDecoder().decode(text)
    try:
        pass
    
    except Exception, e:
        print 'urllib2 error:',e.fp.read()
    return None




def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def process_cases():
    external_id='127196'
    t=team('desk/v1/tickets/%s.json'% external_id)['ticket']
    for k in t:
        if k=='threads':
            continue
        print '---->',k,'<----'
        print t[k]
    body=''
    replies=[]
    if  len(t['threads'])>0:
        for tr in t['threads']:
            r={
                #'subject':tr['subject'],
                'direction':'in',
                'body_html':tr['body'],
                'body':cleanhtml(tr['body']),
                'email':tr['createdBy']['email'],
                "status": "received",
                "to": tr['to'],
                "from": tr['createdBy']['email'],
                "cc": tr['cc'],
                "bcc": tr['bcc'],
                "client_type": "import",
                "created_at": tr['createdAt'],
                "updated_at": tr['updatedAt'],
                "sent_at" : None
            }
            atts=r['attachments']
            replies.append((r,atts))
            print 'REPLY'
            #print r
    cust=get_cust(t['customer']['email'])
    print cust
    msg=  {
            'from':t['inboxName'],
            'name':t['customer']['firstName']+' '+t['customer']['lastName'],
            'to':t['originalRecipient'],
            'cc':';'.join(t['CC']),
            'bcc':';'.join(t['BCC']),
            'direction':'in',
            'subject':t['subject'], # ???
            'body':'>>> imported from teamwork <<<'
           }
    stat={'solved':'resolved','active':'open','not a ticket':'pending',
          'on-hold':'pending','information received':'pending','waitng on customer':'pending','closed':'resolved','spam':'resolved'
         }
    case={'type':'email',
          'external_id':external_id+'+'+str(time.time()),
          'subject':t['subject'],
          "priority": 4,
          'received_at':t['createdAt'],
          'opened_at':t['createdAt'],
          'created_at':t['createdAt'],
          'updated_at':t['updatedAt'],
          "status": stat[ t['status'] ],
          '_links':{
              "customer":cust['_links']['self'],
              #"assigned_user":t['assignedTo']['email'],
              'locked_by': None
              },
          'blurb':t['preview'],
          "message":msg
    }
    if t["tags"] > 0:
        case["labels"]=t["tags"]
    
    print case
    cs=desk('cases',case)
    print 'CASE CREATED!!!!!!!!!!!!!!!'
    print cs
    
    for r in replies:
        repl=desk('cases/%s/replies' % cs['id'],r[0])
        att={'file_name':'original message',
             'content_type':'text/html',
             'content':base64.b64encode(r[0]['body_html'])
            }
        a=desk(('cases/%s/replies/%s/attachments' % cs['id'],repl['id'],att)
        for at in r[1]:
            print '\n ... download %s' % at['downloadURL']
            content=urllib2.urlopen(urllib2.Request(at['downloadURL'])).read()
            att={'file_name':at['file_name'],
             'content_type':'text/html',
             'content':base64.b64encode(content)
                }
            a=desk(('cases/%s/replies/%s/attachments' % cs['id'],repl['id'],att)            
        print repl
    
def tw2d_customer(c):
    external_id=c['id']
    return {
  "first_name": c['firstName'],
  "last_name": c['lastName'],
   "external_id":external_id,
  "emails": [
    {
      "type": "work",
      "value": c['email']
    }
  ],
  "created_at":c["createdAt"],
  "updated_at":c["updatedAt"]
}
def process_customer(c):
    cs=team('desk/v1/customers.json')
    c=cs['customers'][0]
    cust=tw2d_customer(c)
    #print cust
    #search=desk('customers/search?email=%s ' % c['email'] )
    print search
    dcust=desk('customers',cust)
    #print dcust

email_cache={}
def get_cust(e):
    if email_cache.has_key(e):
        return email_cache[e]
    search=desk('customers/search?email=%s ' % e )
    if search['total_entries'] >0:
        email_cache[e]=search['_embedded']['entries'][0]
        return email_cache[e]
    tc=team('desk/v1/customers/email.json',{'email':e})
    dc=tw2d_customer(tc)
    dcust=desk('customers',dc)
    email_cache[e]=dcust
    print dcust
    return email_cache[e]

labels={}
def get_labels():
    ls=desk('labels')
    for l in ls['_embedded']['entries']:
        labels[l['name']]=l
    print labels

    
if __name__=='__main__':
    print 'Teamwork to Desk import tool'
    #art=desk('articles/search?text=Spam')
    if sys.argv[1]=='del':
        desk('cases/%s' % sys.argv[2],{},'DELETE')
    if sys.argv[1]=='go':
        process_cases()
    #get_labels()
    
