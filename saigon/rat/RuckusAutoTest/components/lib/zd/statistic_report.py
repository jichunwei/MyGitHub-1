'''
LIB for statistic report:
    get_xml_data == > grab xml data from ZD via http request.
    
Created on 2013-7-26
@author: cwang@ruckuswireless.com
'''
import socket
import urllib, urllib2
import sys
import time
import datetime
import gzip
from StringIO import StringIO
import socket
import logging
import os

from contrib.xml2dict import ConvertXmlToDict
from contrib.xml2dict import XmlDictObject

from xml.dom.minidom import parse, parseString

def get_xml_data(ip_addr='192.168.0.2',
                 username='admin',
                 password='admin',
                 port=443,
                 version='9.0',
                 gzip=0,
                 timeout=10,
                 ):    
    
    login_uri = '/admin/login.jsp'
    login_url = 'https://' + ip_addr + ':' + str(port) + login_uri
    logging.info('Login URL: %s' % login_url)
    
    get_url = 'https://' + ip_addr + ':' + str(port) + '/admin/_cmdstat.jsp'
    logging.info('Get URL: %s' % get_url)
    
    socket.setdefaulttimeout(timeout)
    today = datetime.datetime.today()
    start_time = datetime.datetime.now()
    this_hour = datetime.datetime(today.year,
                                  today.month,
                                  today.day,
                                  today.hour);
    now_sec = int(time.time())
    start_sec = int(time.mktime(this_hour.timetuple()))
    
    if version == '9.0':#zd
        command_xml = '<ajax-request action="getstat" comp="stamgr" updater="zd.' + str(now_sec) + '" enable-gzip="' + str(gzip) + '">'
        command_xml += '<ap LEVEL="10"  INTERVAL-STATS="yes" INTERVAL-START="' + str(start_sec) + '" INTERVAL-STOP="' + str(now_sec) + '" />'
        command_xml += '<client  LEVEL="10"  INTERVAL-STATS="yes" INTERVAL-START="' + str(start_sec) + '" INTERVAL-STOP="' + str(now_sec) + '" />'
        command_xml += '<session NUM-SESSION-BIN="8" />'
        command_xml += '<chart type="chartcpu,chartmem,chartdisk" id="-1" />'
        command_xml += '<wlan LEVEL="10"  INTERVAL-STATS="yes" INTERVAL-START="' + str(start_sec) + '" INTERVAL-STOP="' + str(now_sec) + '" />'
        command_xml += '<wlangroup />'
        command_xml += '<apgroup />'
        command_xml += '<rogue/>'
        command_xml += '<system LEVEL="10"/>'
        command_xml += '<meshview />'    
        command_xml += '</ajax-request>'
    #command_xml = '<ajax-request action="getstat" comp="stamgr" updater="zd.' + str(now_sec) + '" enable-gzip="0"><ap LEVEL="1" /></ajax-request>'
    else:
        command_xml = '<ajax-request action="getstat" comp="stamgr" updater="zd.' + str(now_sec) + '" enable-gzip="' + str(gzip) + '">'
        command_xml += '<ap LEVEL="3"/>'
        command_xml += '<meshview />'
        command_xml += '<system />'
        command_xml += '</ajax-request>'
    
    logging.info('Command Request as:')
    logging.info(command_xml)
    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)    
    params = urllib.urlencode({ 'username':username,
                                'password':password,
                                'action':'login.jsp',
                                'ok':'whatever' })
    logging.info('Command Request Parameter as:')
    logging.info(params)
    
    try:
        request = opener.open(login_url, params)
    except Exception, e:
        logging.error('login fail %s' % e.message)
        raise e
    
    data = request.read()
    request.close()
    
    try:
        request = urllib2.Request(url=get_url, data=command_xml)
        opener.addheaders = [('Content-Type' , 'text/xml')] 
        assert request.get_method() == 'POST'
        openObj = opener.open(request)
 
    except IOError, e:
        print >> sys.stderr, e
    
    data = openObj.read()
    openObj.close()
    
    filename = "tmp/result_%s" % time.strftime("%Y%m%d%H%M") 
    
    if not gzip:
        if not os.path.exists(os.path.dirname(filename+".xml")):
            os.makedirs(os.path.dirname(filename+".xml"))
            
        file = open(filename + ".xml", 'w')
        file.write(data);
        file.close()
        logging.info('Save to file as %s.xml' % filename)
#        print data
#    else:
#        if not os.path.exists(os.path.dirname(filename+".gz")):
#            os.makedirs(os.path.dirname(fname+".gz"))
#        file = open(filename + ".gz", 'w')
#        file.write(data)
#        file.close()
                
#        inbuffer = StringIO(data)
#        f = gzip.GzipFile(mode='rb', fileobj=inbuffer)
#        try:
#            rec_data = f.read(len(data))
#            print rec_data
#        finally:
#            f.close()
#        
#        logging.info('Save to file as %s.gz' % filename)
        
    end_time = datetime.datetime.now()
    logging.info('ZD XML: size=%d, time=%s\n' %\
                   (len(data), end_time-start_time))
    
    return data


def get_dom_node(xmlstr):
    node = parseString(xmlstr)
    assert node != None
    

def resolve2dict_by_node(node):
    """
    convert to dictionary via xml node.
        for example:
            node = get_dom_node(xmldata)
            wlans = node.getElementsByTagName("wlan")
            _ll = []
            for wlan in wlans:
                _ll.append(resolve2dict_by_node(wlan))
    
    """
    assert node != None
    _obj = StringIO(node.toxml())
    _dd = ConvertXmlToDict(_obj)
    assert _dd != None
    return _dd
    

def convert2dict(xmldata):    
    _obj = StringIO(xmldata)    
    _dd = ConvertXmlToDict(_obj)
    if _dd['ajax-response']['response']['apstamgr-stat'].has_key('rogue'):
        del(_dd['ajax-response']['response']['apstamgr-stat']['rogue'])
        
    return _dd['ajax-response']['response']['apstamgr-stat']

def get_wlan_stat(_dd):
    '''
    Get WLAN list.
    '''
    wlans = _dd['wlan']
    if type(wlans) is dict or type(wlans) is XmlDictObject:
        return [wlans]
    elif type(wlans) is list:
        return wlans  
    else:
        return wlans

def get_wlan_stat_by_name(_dd, name):    
    wlans = _dd['wlan']
    if type(wlans) is dict or type(wlans) is XmlDictObject:
        if wlans['name'] == name:
            return wlans
        else:
            return None
    elif type(wlans) is list:
        for wlan in wlans:
            if wlan['name'] == name:
                return wlan
    
    return None



def get_vap_stat_by_ssid(_dd, bssid):
    wlancfg = _dd['wlan']    
    wlans = []
    if type(wlancfg) is dict or type(wlancfg) is XmlDictObject:
        wlans = [wlancfg]
    else:
        wlans = wlancfg
#    import pdb
#    pdb.set_trace()
    for wlan in wlans:
        if wlan.has_key('vap'):          
            _vaps = wlan['vap']
            if type(_vaps) is not list:
                _vaps = [_vaps]
                
            for vap in _vaps:
                if vap['bssid'] == bssid:
                    return vap        
        
    return None

def get_ap_stat_by_mac(_dd, mac):
    _aps = _dd['ap']
    if type(_aps) is list:
        for ap in _aps:
            if ap['mac'] == mac:
                return ap
            
    elif type(_aps) is dict or type(_aps) is XmlDictObject:
        if _aps['mac'] == mac:
            return _aps
    
    return None
    

def get_sys_stat(_dd):
    return _dd['system']


def get_wg_stat_by_name(_dd, grpname):
    _wgs = _dd['wlangroup']
    if type(_wgs) is list:
        for wg in _wgs:
            if wg['name'] == grpname:
                return wg
    elif type(_wgs) is dict or type(_wgs) is XmlDictObject:
        if _wgs['name'] == grpname:
            return _wgs
    
    return None

def get_apg_stat_by_name(_dd, grpname):
    _grps = _dd['group']
    if type(_grps) is list:
        for grp in _grps:
            if grp['name'] == grpname:
                return grp
    elif type(_grps) is dict or type(_grps) is XmlDictObject:
        if _grps['name'] == grpname:
            return _grps
    
    return None
