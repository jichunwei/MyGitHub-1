"""
    Description:
        Apply 8 WLANs to APs(SimAPs and RuckusAPs) ZoneDirector in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
    Prerequisites:
        1) All of SimAPs are running at your ENV and all of them are connected. 
    usage:
        tea.py <scaling_zd_wlans_apply key/value pair> ...
        
        where <scaling_zd_restart key/value pair> are:
          zd_ip_addr        :     'ipaddr of ZoneDirector'
          zd_username       :     'uername of ZoneDirector'
          zd_password       :     'password of ZoneDirector'
        notes:
    Examples:
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling num_of_wlans=8	
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling chk_gui=True debug=True
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
"""

import logging

from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import wlan_zd as WLAN
from RuckusAutoTest.tests.zd import libZD_TestMethods as TM 

from lib import scaling_utils as utils
from lib import scaling_zd_lib as lib

zdcfg = {'ip_addr': '192.168.0.2',
         'username': 'admin',
         'password': 'admin',
         'shell_key':'!v54!'
         }  

def do_config(**kwargs):
    utils.halt(kwargs['debug']) 
    update_zd_cfg(zdcfg, **kwargs)
    zd = utils.create_zd(**zdcfg)
    zd.remove_all_cfg()
    return zd
    
def do_test(zd,**kwargs):
    wlan_conf_list = init_wlans(**kwargs)
    expected_wlan_name_list = create_wlans(zd, wlan_conf_list)
    verify_wlans_on_webui(zd, expected_wlan_name_list)
    utils.halt(kwargs['debug']) 
    aps = lib.resolve_verify_all_aps(zd)
    
    for index in range(len(aps)):
        active_ap = RuckusAP(dict(ip_addr=aps[index]['ip_addr'], username = zd.username, password = zd.password))
        for wlan in wlan_conf_list:
            msg = TM.verify_wlan_on_aps(active_ap, wlan['ssid'])
            if not msg and msg != '':
                return {"FAIL":msg}
#            
#    for wlan in wlan_conf_list:
#        for index in range(len(aps)):
#            active_ap = RuckusAP(dict(ipaddr=aps[index]['ip_addr'],username='admin',password='admin'))
#            msg = TM.verify_wlan_on_aps(active_ap, wlan['ssid'])
#            if not msg and msg != '':
#                return {"FAIL":msg}
#            

    return {"PASS":"all of WLANs can be configured correctly against APs."}
        
        
def do_clean_up(zd):
    zd.remove_all_cfg()

def init_wlans(**kwargs):
    wlan_cfg = dict(num_of_wlans=8,wlan_conf_list=None)
    wlan_cfg.update(kwargs)
    default_wlan_conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
                         'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
                         'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None,
                         'acl_name': '', 'l3_l4_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '',
                         'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'acct_svr': '', 'interim_update': None}
    open_none = default_wlan_conf.copy()
    open_none.update({'ssid':'Open-None', 'auth':'open', 'encryption':'none'})
    wlan_conf_list = []
    if wlan_cfg.has_key('wlan_conf_list') and wlan_cfg['wlan_conf_list'] :
        wlan_conf_list = wlan_cfg['wlan_conf_list']
        
    else :
        
        for idx in range(0, wlan_cfg['num_of_wlans']):
            wlan = open_none.copy()
            wlan['ssid'] = '%s-wlan%2d' % (wlan['ssid'], idx + 1)
            wlan_conf_list.append(wlan)     
            
    return wlan_conf_list

def create_wlans(zd,wlan_conf_list=None):
    # Base on the WLAN configuration list to create WLANs on ZD WebUI
    try:
        
        WLAN.create_multi_wlans(zd, wlan_conf_list)
        expected_wlan_name_list = [wlan['ssid'] for wlan in wlan_conf_list]
        passmsg = 'The WLANs %s are created successfully' % expected_wlan_name_list
        logging.debug(passmsg)
        return expected_wlan_name_list
    
    except Exception, e:
        
        errmsg = '[WLANs creating failed] %s' % e.message
        logging.debug(errmsg)
        raise Exception(errmsg)
        

def verify_wlans_on_webui(zd,expected_wlan_name_list):
    # Verify the WLANs list show on the ZD if they are match with the expected WLANs
    wlan_list_on_zd = WLAN.get_wlan_list(zd)
    for wlan in expected_wlan_name_list:
        if wlan not in wlan_list_on_zd:
            msg = 'The WLAN[%s] are not shown on Zone Director'
            errmsg = msg % wlan
            logging.debug(errmsg)
            return {'FAIL':errmsg}
        
    passmsg = 'WLANs %s are shown on Zone Director correctly' % expected_wlan_name_list
    logging.debug(passmsg)
    
    return {'PASS':passmsg}

def update_zd_cfg(zdcfg, **kwargs):
    if kwargs.has_key('zd_ip_addr'):
        zdcfg['ip_addr']=kwargs['zd_ip_addr']
        
    if kwargs.has_key('zd_username'):
        zdcfg['username'] = kwargs['zd_username']
        
    if kwargs.has_key('zd_password'):
        zdcfg['password'] = kwargs['zd_password']
        
    if kwargs.has_key('zd_shell_key'):
        zdcfg['shell_key']=kwargs['zd_shell_key'] 
        
def usage():
    """
        Description:
            Apply 8 WLANs to APs(SimAPs and RuckusAPs) ZoneDirector in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
        Prerequisites:
            1) All of SimAPs are running at your ENV and all of them are connected. 
        usage:
            tea.py <scaling_zd_wlans_apply key/value pair> ...
            
            where <scaling_zd_restart key/value pair> are:
              zd_ip_addr        :     'ipaddr of ZoneDirector'
              zd_username       :     'uername of ZoneDirector'
              zd_password       :     'password of ZoneDirector'
            notes:
        Examples:
            tea.py scaling_zd_wlans_apply te_root=u.zd.scaling 
            tea.py scaling_zd_wlans_apply te_root=u.zd.scaling chk_gui=True debug=True
            tea.py scaling_zd_wlans_apply te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
    """
    
def main( **kwargs ):
    mycfg = dict( chk_gui=False, debug=False)
    mycfg.update(kwargs)
    zd = do_config( **mycfg ) 
    try:     
        msg = do_test( zd, **mycfg)
        if msg.has_key('FAIL'):
            logging.error(msg['FAIL'])
            do_clean_up( zd )
            return {"FAIL": msg }
        
        do_clean_up( zd )
        return {"PASS":""}
    
    finally:
        zd.s.shut_down_selenium_server()  
