'''
Created on Jun 25, 2012

@author: Jacky.Luh
'''

import os
import re
import datetime
import time
import logging
import urllib2, urllib
from pprint import pformat

from RuckusAutoTest import BeautifulSoup
from contrib.download import multi_threads_downloader as di

server_url_map = {'base_build':'',
                  'cur_build':''
                  }
#Chris.Wang add 2012-05-28
def get_handler(url="http://nanhu.tw.video54.local/login/j_acegi_security_check"):
    (username, password) = get_auth_user()
    hnd = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(hnd)
    values = {'j_username':username,
              'j_password':password,
              }
    p = urllib.urlencode(values)
    f = hnd.open(url, p)
    f.close()
    
    return hnd


#Jluh add 2011-01-11
def get_auth_user():   
    return 'qaauto', 'QaAuto!880'


def set_base_build(build_stream, bno):
    server_url_map['base_build'] = build_stream.split("_")[1] + "." + str(bno)
    
    
def set_cur_build(zd_ver):
    server_url_map['cur_build'] = zd_ver


def get_auth_page(theurl, username='', password=''):
    # this creates a password manager
    hnd = None
    thepage = None
    if "nanhu" in theurl:
        #Get Data  page
        hnd = get_handler()
        f = hnd.open(theurl)        
        thepage = f.read()
        f.close()
    elif "yangming" in theurl:
        (username, password) = get_auth_user()
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, theurl, username, password)   
        # create the AuthHandler
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)   
        urllib2.install_opener(opener)
        pagehandle = urllib2.urlopen(theurl)     
        thepage = pagehandle.read()
    
    return thepage
    

def get_auth_file_conn(theurl, username='', password=''):
    (username, password) = get_auth_user()
    # this creates a password manager
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, theurl, username, password)

    # create the AuthHandler
    authhandler = urllib2.HTTPBasicAuthHandler(passman)

    opener = urllib2.build_opener(authhandler)

    urllib2.install_opener(opener)

    pagehandle = urllib2.urlopen(theurl)
    
    return pagehandle

#Created by cwang@20130627
class BuildURLBuilder(object):    
    model = None#ZD3000, ZD5000
    prefix = None#0.0.0.99, 9.7.0.0
    label = None#produciton, Mainline    
    LOCAL_REPOSITORY = os.getcwd()
    SERVER_URLs = {'production': 'http://nanhu.tw.video54.local/',
                    'mainline': 'http://nanhu.tw.video54.local/',
                    'odc':'http://hq-jenkins1:8081/nexus/',
                   }
    odc = False#odc office.
   
    SAVE_REPOSITORY = { 
                        'ZD5000':{'local_path': LOCAL_REPOSITORY,
                                   'share_folder_path': '',
                                   },
                         'ZD3000':{'local_path': LOCAL_REPOSITORY,
                                   'share_folder_path': '',
                                   },
                         'ZD1100':{'local_path': LOCAL_REPOSITORY,
                                   'share_folder_path': '',
                                   },
                         'ZD1000':{'local_path': LOCAL_REPOSITORY,
                                   'share_folder_path': '',
                                   }
                         }                  

    PROJECT_LABEL = {'0.0.0.99': ['Mainline', 'OFFICIAL'],
                     '9.5.0.0': ['Xian', 'OFFICIAL'],
                     '9.6.0.0': ['Yokohama', 'OFFICIAL'],
                     '9.7.0.0': ['Zurich', 'OFFICIAL'],
                     '9.8.0.0': ['Amalfi', 'OFFICIAL'],
                     }
    
    RELEASE_NAME_INDEX  = 0#like Xian, Yokohama, Zurich
    RELEASE_TYPE_INDEX = 1#like OFFICIAL, POC
    
    def __init__(self, bstream, bno):
        self.bstream = bstream
        self.bno = bno
        self._resolve_bstream()
        self._isodc()
            
    def _isodc(self):
        oo = os.popen("ipconfig/all")
        dd = oo.read()
        if "172.24" in dd:
            self.odc = True
        
        else: 
            self.odc = False
    
    def _resolve_bstream(self):
        #ZD3000_9.3.1.0_production == > ZD3000, 9.3.1.0, production
        #ZD3000_0.0.0.99_mainline == > ZD3000, 0.0.0.99, mainline
        self.model, self.prefix, self.label = self.bstream.split("_")        
    
    #obsoleted, we don't use it from 9.4.
    def _build_yangming(self, 
                       baseurl='http://yangming.tw.video54.local:9000/'):
        tmpl = 'buildsystem/build_list?pd_name=%s&version=%s'        
        pre = re.findall(r'^(\d*\.\d*).*', self.prefix)[0]
        ver = self.prefix.replace(".", '')                    
        place = self.model + pre + ver
        
        return baseurl + tmpl % (place, self.prefix)
    
    
    def _build_nanhu(self, 
                    baseurl='http://nanhu.tw.video54.local/',
                    ):
        tmpl = 'view/ALL/job/%s_%s_%s-%s/%s/artifact/tftpboot/%s_%s/'
        if 'ZD5000' in self.model:
            label = self.label + '_internal'
        else:
            label = self.label
        try:
            rname = self.PROJECT_LABEL[self.prefix][self.RELEASE_NAME_INDEX]
            rtype = self.PROJECT_LABEL[self.prefix][self.RELEASE_TYPE_INDEX]
            
        except Exception, e:
            raise Exception('Not found release mapping in %s' % self.PROJECT_LABEL)
        
        if 'mainline' in label:
            place = tmpl % (rname, 
                            self.prefix, 
                            self.model, 
                            rtype, 
                            str(self.bno),
                            self.model, 
                           'production'
                                       )
        elif 'production' in label:
            place = tmpl % (rname, 
                            self.prefix, 
                            self.model,
                            rtype, 
                            str(self.bno), 
                            self.model, 
                            label)
        else:
            raise Exception("Unknown label %s, \
            please check your configuration" % label)
        
        return baseurl + place
        
    #For ODC
    def _build_nexus(self, baseurl='http://hq-jenkins1:8081/nexus/'):
        tmpl = 'content/groups/ruckus-public/ruckus/official/zonedirector/%s/%s/'
        version = '%s.%s' % (self.prefix, self.bno)
        place = tmpl %(self.model, version)
        filename = "%s-%s.tgz" % (self.model, version)
        return baseurl + place + filename
    
    
    def build_url(self):
        if self.odc:
            _url = self._build_nexus(self.SERVER_URLs['odc'])
            return _url
        else:
            _url = self._build_nanhu(self.SERVER_URLs[self.label])
            _webpage_str = get_auth_page(_url)
            
            if _webpage_str:
                try:
                    soup = BeautifulSoup.BeautifulSoup("".join(_webpage_str))
                    build_url = ''                    
                    cols_map = {'number': 1, 'url': 12}
                    buildtable = soup('table')[3]
                    ima_name = str(buildtable('tr')[2]('td')[cols_map['number']].contents[0]['href'])
                    if ima_name:
                        if os.path.isdir(self.SAVE_REPOSITORY[self.model]['share_folder_path']):
                            full_fname = os.path.join(self.SAVE_REPOSITORY[self.model]['share_folder_path'], ima_name)
                        else:
                            full_fname = os.path.join(self.SAVE_REPOSITORY[self.model]['local_path'], ima_name)
                        
                        if os.path.isfile(full_fname):
                            return full_fname
                        
                        build_url = buildstream_url + '/' + ima_name                    
                except Exception, e:
                    import traceback
                    logging.error(traceback.format_exc())
                    raise Exception("Image Server format is invalid, please check.")
                
                return build_url
            else:
                raise Exception('Unknown Server.') 


def get_build_url(build_stream, bno):
    builder = BuildURLBuilder(build_stream, bno)
    return builder.build_url()  

def download_build_v2(build_url, full_fname=''):
    """
    Download the target build from server base on the build url.
    """
    logging.info('The image_file[' + build_url + ']')
    logging.info('Please wait for downloading, It takes several minutes')
    fin = di.http_get(build_url, full_fname)        
    return fin

