#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json, base64, urllib2, json
import re,sys,time
from bs4 import BeautifulSoup


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
        text=e.fp.read()
        print text
        return json.JSONDecoder().decode(text)
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
            try:
               return json.JSONDecoder().decode(text)
            except ValueError as e:
                return text
        else:
            response=urllib2.urlopen(request)
            text=response.read()
            try:
               return json.JSONDecoder().decode(text)
            except ValueError as e:
                return text
    try:
        pass   
    except Exception, e:
        print 'urllib2 error:',e.fp.read()
    return None


def cleanhtml(raw_html):
  return BeautifulSoup(raw_html, "lxml").get_text()
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


def person_link(uid):
    if uid in tw2deskusers.keys():
        print tw2deskusers[uid]
        return {'href': '/api/v2/users/%d' % tw2deskusers[uid][0], 'class': 'user'}
    else:
        cust=get_cst(uid)
        return cust['_links']['self']


map_stat={'solved':'resolved','active':'open','not a ticket':'pending',
          'on-hold':'pending','information received':'pending','waitng on customer':'pending','closed':'resolved','spam':'resolved'
         }
def process_cases():
    external_id='127196'
    t=team('tickets/%s.json'% external_id)['ticket']
    for k in t:  
        if k=='threads':
            continue
        print '---->',k,'<----'
        print t[k]
    body=''
    replies=[]
    replies1=[]
    notes=[]
    if  len(t['threads'])>0:
        for tr in t['threads']:
            if tr['type'] != 'message':
                #this is not email
                sts = tr['newTicketStatus'] if tr['newTicketStatus'] else ''
                bod = tr['body'] if tr['body'] else ''
                note={
                'suppress_rules':True,
                'user': person_link(tr['createdBy']['id']),
                'body': tr['createdBy']['firstName'] + ' mark as ' + sts +' '+bod,
                'created_at': tr['createdAt'],
                'updated_at': tr['updatedAt'],
                '_links':
                    { 'user':person_link(tr['createdBy']['id'])
                        }
                }
                notes.append(note)
                continue
            #else:
            #    continue
            if not tr['to']:tr['to']='none'
            if not tr['cc']:tr['cc']='none'
            if not tr['bcc']:tr['bcc']='none'
            ats=[]
            for attr in tr['attachments']:
                content=urllib2.urlopen(urllib2.Request(tr['downloadURL'])).read()
                att={'file_name':tr['filename'],
             'content_type':'application/octet-stream',
             'content':base64.b64encode(content)
                } 
                ats.append(att)
            r={
                #'subject':tr['subject'],
                'suppress_rules':True,
                'direction':'in',
                'body_html':tr['body'],
                'body_text':cleanhtml(tr['body']),
                'body':cleanhtml(tr['body']),
                'email':tr['createdBy']['email'],
                "status": map_stat[t['status']],
                "to": tr['to'],
                "from": tr['createdBy']['email'],
                "cc": tr['cc'],
                "bcc": tr['bcc'],
                "client_type": "import",
                "created_at": tr['createdAt'],
                "created_by": person_link(tr['createdBy']['id']),
                #"updated_at": tr['updatedAt'],
                "sent_at" : None,
                'attachments':ats,
                '_links':
                    { 'user':person_link(tr['createdBy']['id'])
                    }
            }
            atts=tr['attachments']
            replies.append((r,atts))
            replies1.append(r)
            print 'REPLY from: %s to:%s cc:%s bcc:%s' % (tr['createdBy']['email'],tr['to'],tr['cc'],tr['bcc'])
            #print r
    cust=get_cst(t['customer']['id'])
    print cust
    msg=  {
            'suppress_rules':True,
            'from':t['inboxName'],
            'name':t['customer']['firstName']+' '+t['customer']['lastName'],
            'to':t['originalRecipient'],
            'cc':';'.join(t['CC']),
            'bcc':';'.join(t['BCC']),
            'direction':'in',
            'subject':t['subject'], # ???
            'body':t['subject']+'\n'+'>>> imported from teamwork <<<'
           }
    
    case={'type':'email',
          'suppress_rules':True,
          'external_id':external_id+'+'+str(time.time()),
          'subject':t['subject'],
          "priority": 4,
          'received_at':t['createdAt'],
          'opened_at':t['createdAt'],
          'created_at':t['createdAt'],
          'updated_at':t['updatedAt'],
          'resolved_at':t['updatedAt'],
          "status": map_stat[ t['status'] ],
          'assigned_user':person_link(t['assignedTo']['id']),
          '_links':{
              "customer":cust['_links']['self'],
              #"assigned_user":person_link(t['assignedTo']['id']),
              'locked_by': None
              },
          'blurb':t['preview'],
          "message":msg,
          #"replies":replies1,
          #"notes":notes
    }
    labels_addon=['spam','ignore']
    if t["tags"] > 0:
        case["labels"]=t["tags"]+labels_addon
    else:
       case["labels"]=labels_addon
    print '>> FROM TICKET:'
    print t
    print '<< TO CREATE:'
    print case
    cs=desk('cases',case)
    print 'CASE CREATED!!!!!!!!!!!!!!!'
    print cs
    #return
    for nn in notes:
        repl=desk('cases/%s/notes' % cs['id'],nn)
    #return
    for rr in replies[0:1]:
        repl=desk('cases/%s/replies' % cs['id'],rr[0])
        print 'added',repl
        repl['id']=int(repl['_links']['self']['href'].split('/')[6])
        att={'file_name':'message%s.html'%repl['id'],
             'content_type':'text/html',
             'content': base64.b64encode(rr[0]['body_html'])
            }
        print '...add content %s %s' % ( cs['id'],repl['id'] )
        a=desk('cases/%s/replies/%s/attachments' % ( cs['id'],repl['id'] ),att)
        #a=desk('cases/%s/attachments' %  cs['id'] ,att)
        print 'content ok ' +str(a)
        for at_file in rr[1]  :
            print '\n ... download %s' % at_file['downloadURL']
            content=urllib2.urlopen(urllib2.Request(at_file['downloadURL'])).read()
            att={'file_name':at_file['filename'],
             'content_type':'application/octet-stream',
             'content':base64.b64encode(content)
                }
            a=desk('cases/%s/replies/%s/attachments' % ( cs['id'],repl['id'] ),att)
            print a
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
    cs=team('customers.json')
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
    tc=team('customers/email.json',{'email':e})
    dc=tw2d_customer(tc)
    dcust=desk('customers',dc)
    email_cache[e]=dcust
    print dcust
    return email_cache[e]

cust_cache={}
def get_cst(cid):
    if cust_cache.has_key(cid):
        return cust_cache[cid]
    search=desk('customers/search?external_id=%s ' % cid )
    if search['total_entries'] >0:
        cust_cache[cid]=search['_embedded']['entries'][0]
        return email_cache[e]
    tc=team('customers/%s.json' % cid)['customer']
    print tc
    dc=tw2d_customer(tc)
    dcust=desk('customers',dc)
    if 'message' in dcust and dcust['message']=='Validation Failed':
        dcust=desk('customers/search?email=%s' % tc['email'] )['_embedded'][u'entries'][0]
    cust_cache[cid]=dcust
    print dcust
    return cust_cache[cid]


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
    
