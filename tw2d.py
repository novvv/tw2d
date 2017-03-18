#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import json, base64, urllib2, json
import re,sys,time
from bs4 import BeautifulSoup
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from mimetypes import MimeTypes
from datetime import datetime

#base='https://desk.com/api/v2/'

from settings import *

from urllib2 import Request, urlopen
#urlopen(Request(url, headers={'Authorization': b'Basic ' + base64.b64encode(credentials)})).close()

auth_u= base64.b64encode('%s:%s' % (username, password))
auth_a = base64.encodestring('%s:%s' % (User, Pass)).replace('\n', '')
auth=auth_u

ALLOW_DOUBLE=False

def desk(q,data=None,method='GET'):
    url=base_desk+q
    print url
    #User=username
    #Pass=password

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept':'application/json',
       'Accept-Charset': 'utf-8',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive',
       'Content-Type': 'application/json',
       "Authorization": "Basic %s" % auth
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
        if hasattr(e,'fp'):
            text=e.fp.read()
        else:
            text=str(e)
        #print text
        try:
               return json.JSONDecoder().decode(text)
        except ValueError as e:
            return text
        #return json.JSONDecoder().decode(text)
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
    try:
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
    except Exception, e:
        if hasattr(e,'fp'):
            text=e.fp.read()
        else:
            text=str(e)
        try:
            print 'urllib2 error:',text
            return None #json.JSONDecoder().decode(text)
        except ValueError as e:
            return text

    return None


def cleanhtml(raw_html):
  return BeautifulSoup(raw_html, "lxml").get_text()
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

tw2deskusers ={
    129474: (26501732,'Enida'),  # Enida 
    100123: (26493754,'@ Admin'),# @ Admin 
    100125: (26493754,'Alma'), #Alma
    102283: (26493754,'@ Admin'), #????
    102282: (26493754,'@ Admin'),  #????
    102284: (26493754,'@ Admin')
    }


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
def desk_attach(base,name,type,content):
    if type.split('/')[0]!='text':
        content=base64.b64encode(content)
    att={'file_name':name,
             'content_type':type,
             'content':content
        }
    desk(base+'/attachments',att)



def map_case(t):
    cust=get_cst(t['customer']['id'])
    #print cust
    cc=';'.join(t['CC']),
    bcc=';'.join(t['BCC'])
    if cc=='':cc='nobody'
    if bcc=='':bcc='nobody'

    msg=  {
            'suppress_rules':True,
            'from':t['inboxName'],
            'name':t['customer']['firstName']+' '+t['customer']['lastName'],
            'to':t['originalRecipient'],
            'cc':cc,
            'bcc':bcc,
            'direction':'in',
            'subject':t['subject'], # ???
            'body':t['subject']+'\n'+'>>> imported from teamwork ticket #% d <<<' % t['id']
           }

    case={'type':'email',
          'suppress_rules':True,
          'external_id':str(t['id']) ,#+'+'+str(time.time()),
          'subject':t['subject'],
          "priority": 4,
          'received_at':t['createdAt'],
          'opened_at':t['createdAt'],
          'created_at':t['createdAt'],
          'updated_at':t['updatedAt'],
          'resolved_at':t['updatedAt'],
          "status": map_stat[ t['status'] ],
          #'assigned_user':person_link(t['assignedTo']['id']),
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
    if t['assignedTo']:
        case['assigned_user']=person_link(t['assignedTo']['id'])
    labels_addon=['teamwork']
    if len( t["tags"] ) >  0:
        case["labels"] =  [x['name'] for x in t['tags']]+labels_addon
    else:
       case["labels"]=labels_addon
    #print '>> FROM TICKET:'
    #print t
    #print '<< TO CREATE:'
    #print case
    return case

def map_attachment(attr,download=True):
        #try:
            print attr
            if download: 
                content=urllib2.urlopen(urllib2.Request(attr['downloadURL'])).read()
                fn=attr['filename']
                file_name=''.join(fn.split('.')[0:-1])+'.'+fn.split('.')[-1]
                att={
                'file_name':file_name,
                'content_type':mimetypes.guess_type(file_name),
                'content':base64.b64encode(content)
                }
            else:
                att={'downloadURL':attr['downloadURL']
                    }
            att['original']=attr
            return att

        #except:
        #    print 'Bad attachment !\n',attr
        #    return {'file_name':None,'content_type':None,'content':''}


def map_reply(tr,download=True):
    if not tr['to']:tr['to']='nobody'
    if not tr['cc']:tr['cc']='nobody'
    if not tr['bcc']:tr['bcc']='nobody'
    createdBy=person_link(tr['createdBy']['id'])
    if not createdBy:
        createdBy=tr['createdBy']['email']
    r={
                #'subject':tr['subject'],
                'suppress_rules':True,
                'status':'draft',
                'direction':'in',
                #'body_html':tr['body'],
                #'body_text':cleanhtml(tr['body']),
                'body':cleanhtml(tr['body']),
                'email':tr['createdBy']['email'],
                "to": tr['to'],
                "from": tr['createdBy']['email'],
                "cc": tr['cc'],
                "bcc": tr['bcc'],
                "client_type": "import",
                "created_at": tr['createdAt'],
                "created_by": createdBy,
                #"updated_at": tr['updatedAt'],
                "sent_at" : None,
                'ext_attachments':[],

                '_links':
                    { 'user':person_link(tr['createdBy']['id'])
                    }
            }
    #
    #for att in tr['attachments']:
    #    a=map_attachment(att)
        #r['ext_attachments'].append(a)

    return r

def map_note(tr):
    sts = tr['newTicketStatus'] if tr['newTicketStatus'] else ''
    bod = tr['body'] if tr['body'] else ''
    bod = cleanhtml(bod)
    createdBy=person_link(tr['createdBy']['id'])
    if not createdBy:
        createdBy=tr['createdBy']['email']

    note={
                'suppress_rules':True,
                'user': createdBy,
                'body': tr['createdBy']['firstName']+' as '+tr['createdBy']['email'] + ' mark as ' + sts +' '+bod,
                'created_at': tr['createdAt'],
                'updated_at': tr['updatedAt'],
                '_links':{ 'user':person_link(tr['createdBy']['id'])}
                }
    return note

def map_email(tr):    
            #try to read orig
            text=''
            html=''
            orig=team('threads/%s/original.eml' % tr['id'] )
            print '!!!',str(orig)[0:16]
            if orig:
                msg=email.message_from_string(orig)
                payloads=msg.get_payload()

                for p in payloads: 
                    if p['Content-type']=='text/plain':
                        text=str(p)
                    if p['Content-type']=='text/html':
                        html=str(p)
            if html=='':
                html=tr['body']
            if text=='':
                text=cleanhtml(tr['body'])



def process_one_case(t):
    #external_id='127196'
    #t=team('tickets/%s.json'% external_id)['ticket']
    external_id=t['id']
    case=map_case(t)
    cs=desk('cases',case)
    if 'message' in cs and cs['message']=='Validation Failed':
        if not ALLOW_DOUBLE:
            raise Exception('Validation Failed on create case!')
        if 'external_id' in cs['errors']:
            case['external_id']=case['external_id']+'+'+str(time.time())
            #cs=desk('cases/search?external_id=%s' % external_id)
            cs=desk('cases',case)
            log( '*%s->%dcreated again....' % (t['id'], cs['id']) )
        else:
            raise Exception('Something wrong on create case!')
    print cs
    #raise
    print 'CASE %d CREATED!!!' % cs['id']

    if  len(t['threads'])>0:
        for tr in t['threads']:
            if tr['type'] != 'message':
                #this is not email
                note=map_note(tr)
                print 'CREATE note %s' % tr['id']
                repl=desk('cases/%s/notes' % cs['id'],note)
                continue
            r=map_reply(tr)
            print 'REPLY from: %s to:%s cc:%s bcc:%s' % (tr['createdBy']['email'],tr['to'],tr['cc'],tr['bcc'])
            #repl=desk('cases/%s/replies' % cs['id'],r)
            repl=desk('cases/%s/replies/draft' % cs['id'],r)
            replid=int( repl['_links']['self']['href'].split('/')[6] )
            print '...created ok...'
            try:
                orig=team('threads/%s/original.eml' % tr['id'] )
                att={'file_name':'original%d.eml' % replid ,'content_type':'message/rfc822','content':base64.b64encode(orig)}
                a=desk('cases/%s/replies/%s/attachments' % ( cs['id'],replid ),att)
                print 'original %s' % a['file_name']
            except:
                print 'no original eml...try html body...'
                #orig=tr['body']
                #att={'file_name':'original%d.html' % replid,'content_type':'text/html','content':orig}
                #a=desk('cases/%s/replies/%s/attachments' % ( cs['id'],replid ),att)
                #print 'original %s' % a['file_name']
            for arr in tr['attachments']:
                att=map_attachment(arr)
                print 'CREATE attachment'
                a=desk('cases/%s/replies/%s/attachments' % ( cs['id'],replid ),att)
                if 'file_name' in a:
                    print 'attachment created %s' % a['file_name']
                else:
                    print 'attachment created ??', a
            print 'RESET DRAFT...'
            desk('cases/%s/replies/%s?fields=body_html,body_text' % ( cs['id'],replid ),
                 {'body_html':base64.b64encode(tr['body']),
                  'body_text':cleanhtml(tr['body']),

                  } ,'PATCH')
            desk('cases/%s/replies/%s' % ( cs['id'],replid ),{'reset':1,'status':'received','updated_at':tr['updatedAt']},'PATCH')
        print 'ALL REPLIES IMPORTED'
    print 'CLOSE CASE %d' % cs['id']
    csr=desk('cases/%s' % cs['id'] ,{'status':'resolved','updated_at':t['updatedAt']},'PATCH')
    return csr

def map_customer(c):
    external_id=c['id']
    if c['email']=='':
        c['email']='@nobody'
    ret= {
  "first_name": c['firstName'],
  "last_name": c['lastName'],
   "external_id":external_id,
   #'phone_numbers':[{'type':'work','value':c['phone']},{'type':'mobile','value':c['mobile']} ],
   'title':c['jobTitle'],
   'addresses':[{'type':'work','value':c['address']}],
  'emails': [{ 'type': "work","value": c['email']}],
  "created_at":c["createdAt"],
  "updated_at":c["updatedAt"]
}
    if c['phone']: 
        ret['phone_numbers']=[{'type':'work','value':c['phone']}]
    return ret    

def process_customer(c):
    cs=team('customers.json')
    c=cs['customers'][0]
    cust=map_customer(c)
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
    dc=map_customer(tc)
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
        return cust_cache[cid]
    tc=team('customers/%s.json' % cid)['customer']
    print tc
    dc=map_customer(tc)
    dcust=desk('customers',dc)
    if 'message' in dcust and dcust['message']=='Validation Failed':
        dcusts=desk('customers/search?email=%s' % tc['email'] )['_embedded'][u'entries']
        if len(dcusts):
            dcust=dcusts[0]
        else: 
            return None 
    cust_cache[cid]=dcust
    print dcust
    return cust_cache[cid]


labels={}
def get_labels():
    ls=desk('labels')
    for l in ls['_embedded']['entries']:
        labels[l['name']]=l
    print labels


_tid=127196
_cid=204
_rid=1657556274
def test_attach():
    t=team('tickets/%d.json' % _tid)['ticket']
    att=map_attachment(t['threads'][8]['attachments'][0])
    repl=desk('cases/%d/replies/%d/attachments' % (_cid,_rid),att)
    return repl

def log(msg):
    log=open('tw2d.log','ab')
    print msg
    log.write(msg)
    log.close()

def run(page=1, n=0):
    #page=1
    log('!Start on position %d----%d-----------%s--------------------\n' %(page, n, str(datetime.now() )))
    while 1:
        search=team('tickets/search.json',{'search':'','page':page,'sortBy':'updatedAt','sortDir':'asc'})
        for ticket in search['tickets'][n:]: 
            try:
                t=team('tickets/%s.json'% ticket['id'])['ticket']
                cs=process_one_case(t)
                log('+%d>%d page %d n %d\n' % (ticket['id'],cs['id'], page, n) )
                pass
            except Exception as e:
                log('-%d>%s page %d n %d\n' % (ticket['id'],str(e).replace('\n','').replace('\r','') , page, n) )
            choice = '1' #raw_input("> ")
            n +=1
            if choice in ['q','Q', '0']:
                print 'bye'
                sys.exit(0)
        log('!------------page %d end --------------%s--------------------'% (page, datetime.now()) )
        page += 1
        n = 0
        if page>search['maxPages']:
                log('Thats all folks!\n')
                break


if __name__=='__main__':
    print 'Teamwork to Desk import tool'
    #art=desk('articles/search?text=Spam')
    if sys.argv[1]=='del':
        auth=auth_a
        desk('cases/%s' % sys.argv[2],{},'DELETE')
    if sys.argv[1]=='clear':
        auth=auth_a
        s=desk('cases/search?labels=teamwork')
        for c in s['_embedded']['entries']:
            print c['id'],c['subject']
            desk('cases/%s' % c['id'],{},'DELETE')
        pass
    if sys.argv[1]=='add':
        ticket=team('tickets/%s.json'% sys.argv[2])['ticket']
        ALLOW_DOUBLE=True
        cs=process_one_case(ticket)
        log('+%d>%d  was added manually \n' % (ticket['id'],cs['id']) )
    if sys.argv[1]=='run':
        if len(sys.argv)>2 and sys.argv[2]=='a':
            ALLOW_DOUBLE=True
        page=1
        n=0
        if len(sys.argv)>4:
            page=int(sys.argv[3])
            n=int(sys.argv[4])
        #print sys.argv
        run(page, n)     
    #get_labels()

