'''
Created on 2012-5-18
@author: cwang@ruckuswireless.com
'''
try:
    #SSL verification is introduced after python 2.7.9
    #The following code is to disable that feature
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass
import time
import logging

from urllib import urlopen
from xml.dom.minidom import parseString
from string import Template

import sys
import os,subprocess

#----------Commands------------------#
#For Hotspot senario#
locators = dict(check_nb = r"//input[@id='nbportal']",
                input_nb_passwd = r"//input[@id='nbportal-passwd']",
                btn_nb_apply = "//input[@id='apply-nbportal']" ,  
                ##zj 2014-0207 fix ZF-7360
                network_mgmt_icon_collapse = r"//tr[@id='cat-network-mgmt']//img[@id='mgmt-icon' and @src='images/collapse.png']",
                network_mgmt_icon_expand = r"//tr[@id='cat-network-mgmt']//img[@id='mgmt-icon' and @src='images/expand.png']",
                network_mgmt_click = r"//tr[@id='cat-network-mgmt']//a",                          
                )

USER_AUTHENTICATE = "user-authenticate"
CHECK_USER_STATUS = "check-user-status"
DEL_USER = "del-user"
UNRESTRICTED = "unrestricted"
GENERATE_DPSK = "generate-dpsk"
GET_DPSK = "get-dpsk"

def enable(zd, password="1234"):
    xloc = locators
    _nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(0.5)
    zd.s.click_if_not_checked(xloc['check_nb'])
    zd.s.type_text(xloc['input_nb_passwd'], password)
    zd.s.click_and_wait(xloc['btn_nb_apply'])
    

def disable(zd):
    xloc = locators
    _nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(0.5)
    zd.s.click_if_checked(xloc['check_nb'])
    zd.s.click_and_wait(xloc['btn_nb_apply'])
    

def notify(req="https://192.168.0.2/admin/_portalintf.jsp", 
           cmd = USER_AUTHENTICATE,
           **kwargs
           ):
    '''
    @param req:  url to northbound interface from ZoneDirector.
    @param data: xml-based, interact with northbound service.
    @return: XML-based dom. 
    '''
    _dd={'user-authenticate':_build_authenication_data,
         'check-user-status':_build_check_user_status_data,
         'del-user':_build_terimate_user_data,
         'unrestricted':_build_unrestricted_data,
         'generate-dpsk':_build_generate_dpsk_data,
         'get-dpsk':_build_get_dpsk_data
         }
    #Make sure if ZD enable mgmt VLAN 
    if kwargs.get('zd_ip_addr'):#chen.tao 2015-03-18, using flexible zd ip address
        req = "https://%s/admin/_portalintf.jsp"%kwargs['zd_ip_addr']
        kwargs.pop('zd_ip_addr')
    elif ping_win32("192.168.128.2"):
        req = "https://192.168.128.2/admin/_portalintf.jsp"
        
    data = _dd[cmd](**kwargs)
    data = data.strip()
    request = urlopen(req, data)
    info = request.read()
    return parseString(info)

def request(req = "https://192.168.0.2/admin/_portalintf.jsp",
            data = None,#XML request file.
            **kwargs
            ):
    #Make sure if ZD enable mgmt VLAN 
    if kwargs.get('zd_ip_addr'):#chen.tao 2015-03-18, using flexible zd ip address
        req = "https://%s/admin/_portalintf.jsp"%kwargs['zd_ip_addr']
        kwargs.pop('zd_ip_addr')
    elif ping_win32("192.168.128.2"):
        req = "https://192.168.128.2/admin/_portalintf.jsp"
        
    request = urlopen(req, data)
    info = request.read()
    return parseString(info)

def get_response_code(node):
    code_elem = node.getElementsByTagName("response-code")[0]
    return code_elem.childNodes[0].nodeValue

def get_response_msg(node):
    msg_elem = node.getElementsByTagName("message")[0]
    return msg_elem.childNodes[0].nodeValue


def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)

def _build_authenication_data(req_password="1234",                                
                              ipaddr = "192.168.0.116",
                              macaddr="00:15:af:ed:94:60",
                              name = "ras.local.user",
                              password = "ras.local.user"
                              ):
    """
    @param req_password: 
    @param ipaddr: ipaddr of client
    @param macaddr: macaddr of client
    @param name: username to authenticate from radius server
    @param password: password to authenticate from radius server    
    """
    
    data = """
    <ruckus>
        <req-password>$req_password</req-password>
        <version>1.0</version>
        <command cmd="user-authenticate" ipaddr="$ipaddr" macaddr="$macaddr"
        name="$name"
        password="$password"/>
    </ruckus>
    """
    obj = Template(data)
    return obj.substitute(dict(req_password = req_password,
                        ipaddr = ipaddr,
                        macaddr = macaddr,
                        name = name,
                        password = password))
    


def _build_check_user_status_data(password = '', #zj 2014-0210 fix lack of parameter,def notify  
                                  req_password="1234",
                                  ipaddr = "192.168.0.116",
                                  macaddr = "00:15:af:ed:94:60",
                                  name = '',                                  
                                  ):
    """
    @param req_password:
    @param ip_addr:ipaddr of client
    @param macaddr:macaddr of client
    """
    data = """
    <ruckus>
        <req-password>$req_password</req-password>
        <version>1.0</version>
        <command cmd="check-user-status" ipaddr="$ipaddr" macaddr="$macaddr"/>
    </ruckus>
    """
    obj = Template(data)
    return obj.substitute(dict(req_password = req_password,
                               ipaddr = ipaddr,
                               macaddr = macaddr,                               
                               ))
    
def _build_terimate_user_data(req_password = '1234',
                              ipaddr = '192.168.0.116',
                              macaddr = '00:15:af:ed:94:60'
                              ):
    data = """
    <ruckus>
        <req-password>$req_password</req-password>
        <version>1.0</version>
        <command cmd="del-user" ipaddr="$ipaddr" macaddr="$macaddr"/>
    </ruckus>
    """
    obj = Template(data)
    return obj.substitute(dict(req_password = req_password,
                               ipaddr = ipaddr,
                               macaddr = macaddr,                               
                               ))


def _build_unrestricted_data(req_password = '1234',
                             macaddr = '00:15:af:ed:94:60',
                             name = 'ras.local.user'
                             ):
    data = """
    <ruckus>
        <req-password>$req_password</req-password>
        <version>1.0</version>
        <command cmd="unrestricted"  macaddr="$macaddr" name="$name"/>
    </ruckus>
    """
    obj = Template(data)
    return obj.substitute(dict(req_password = req_password,                               
                               macaddr = macaddr,          
                               name = name,                     
                               ))


def _build_generate_dpsk_data(req_password = '1234',
                              macaddr = '00:15:af:ed:94:60',
                              user = 'ras.local.user',
                              vlan_id = "1",
                              wlan = "rat-nb-testing",
                              expiration = "24",
                              key_length = "20"
                              ):
    
    data = """
    <ruckus>
        <req-password>$req_password</req-password>
        <version>1.0</version>
        <command cmd="generate-dpsk"> 
            <dpsk expiration="$expiration" key-length="$key_length"            
            mac="$macaddr" user="$user" vlan-id="$vlan_id" wlan="$wlan"/>
        </command>
    </ruckus>
    """
    obj = Template(data)
    return obj.substitute(dict(req_password = req_password,
                               macaddr = macaddr,
                               user = user,
                               vlan_id = vlan_id,
                               wlan = wlan,
                               expiration = expiration,
                               key_length = key_length
                               ))


def _build_get_dpsk_data(req_password = '1234',
                         macaddr = '00:15:af:ed:94:60',
                         wlan = 'rat-nb-testing',
                         user = 'ras.local.user',
                         ):
    data = """
    <ruckus>
        <req-password>$req_password</req-password>
        <version>1.0</version>
        <command cmd="get-dpsk"> 
            <dpsk mac="$macaddr" user="$user" wlan="$wlan"/>
        </command>
    </ruckus>
    """
    obj = Template(data)
    return obj.substitute(dict(req_password = req_password,
                               macaddr = macaddr,
                               wlan = wlan,
                               user = user
                               ))


def ping_win32(target_ip, num=4, length=64, timeout_ms=1000):

    """ping the target and return a list of successful result times in milliseco                                                                              nds"""
    cmd = "ping %s -n %d -l %d -w %d" % (target_ip, num, length, timeout_ms)
    #print cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    err = p.wait()
    res = p.stdout.readlines()
    # extract time from ping results
    res = [x.split(' ') for x in res if x.startswith('Reply from')]
    res = [[t for t in x if t.startswith('time')][0] for x in res]
    # XXX TODO deal with pings that dont return the same number 
    # of bytes as transmitted !
    # normalize "<1ms" result to be same as "=1ms"
    res = [x.replace('<','=') for x in res]
    res = [int(x.split('=')[1].replace('ms','')) for x in res]
    return res

