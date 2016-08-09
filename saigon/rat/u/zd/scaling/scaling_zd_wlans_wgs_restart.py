"""
    Description:
        Configure 32 WLANs and 32 WLANGroups to ZoneDirector and restart in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
    Prerequisites:
        1) All of SimAPs are running at your ENV and all of them are connected. 
    usage:
        tea.py <scaling_zd_wlans_apply key/value pair> ...
        
        where <scaling_zd_restart key/value pair> are:
          zd_ip_addr        :     'ipaddr of ZoneDirector'
          zd_username       :     'uername of ZoneDirector'
          zd_password       :     'password of ZoneDirector'
          num_of_wlans      :     'number of wlans want to create'
          num_of_wgs        :     'number of wlan groups want to create'
          zd_shell_key      :     'enter key of super mode against ZD.'
          chk_gui           :     'True then will verify from ZoneDirector GUI'
        notes:
    Examples:
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling num_of_wlans=2 zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling num_of_wlans=2 num_of_wgs=2 zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling chk_gui=True debug=True
        tea.py scaling_zd_wlans_apply te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
"""
import logging, time

from RuckusAutoTest.components.lib.zd import wlan_groups_zd as WGS
from RuckusAutoTest.components.lib.zd import wlan_zd as WLAN

from lib import scaling_utils as utils
from lib import scaling_zd_lib as lib
from RuckusAutoTest.common.Ratutils  import ping


zdcfg = {'ip_addr': '192.168.0.2',
         'username': 'admin',
         'password': 'admin',
         'shell_key':'!v54!'
         }  
time_cfg = {'gui_timeout':120 * 10,
          'cli_timeout':120 * 10,
          }
loc_admin_restart_btn = r"//input[@id='restart']"

def do_config(**kwargs):
    utils.halt(kwargs['debug'])
    update_zd_cfg(zdcfg, **kwargs)
    zd = utils.create_zd(**zdcfg)
    zd.remove_all_cfg()
    return zd

def do_test(zd, **kwargs):
    utils.halt(kwargs['debug'])
    aps = lib.retrieve_aps(zd)
    wlan_conf_list = init_wlans(**kwargs)
    expected_wlan_name_list = create_wlans(zd, wlan_conf_list)
    res = verify_wlans_webui(zd, expected_wlan_name_list)
    if res.has_key('FAIL'):
        return res
    
    num_of_wgs = 32
    if kwargs.has_key('num_of_wgs'):
        num_of_wgs = kwargs['num_of_wgs']
    create_wlangroups(zd, wlan_conf_list, ssid_index=0, num_of_wgs=num_of_wgs)
    res = verify_wlangroups_webui(zd, num_of_wgs=num_of_wgs)
    if res.has_key('FAIL'):
        return res
    
    restart_and_wait(zd)
    zdcli = utils.create_zd_cli(**zdcfg)
    res = lib.check_all_aps_status_from_cmd(zdcli, aps, time_out=time_cfg['cli_timeout'], chk_mac=True)
    if not res :
        return {"FAIL":"time out when try to wait for all APs connecting."}
    
    if kwargs['chk_gui']:
        res = lib.check_aps_status_from_gui(zd, aps, time_out=time_cfg['gui_timeout'])
        
        if not res :
            return {"FAIL":"APs haven't connected correctly"}
        
    res = verify_wlans_webui(zd, expected_wlan_name_list)
    if res.has_key('FAIL'):
        return res
    
    res = verify_wlangroups_webui(zd, num_of_wgs=num_of_wgs)
    if res.has_key('FAIL'):
        return res
    
    remove_all_wlans_groups(zd) 
    remove_all_wlans(zd)
    utils.halt(kwargs['debug'])
    
    return {'PASS':''}
    
def do_clean_up(zd):
    zd.remove_all_cfg()
    
def init_wlans(**kwargs):
    wlan_cfg = dict(num_of_wlans=32, wlan_conf_list=None)
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
        
    else:
        
        for idx in range(0, wlan_cfg['num_of_wlans']):
            wlan = open_none.copy()
            wlan['ssid'] = '%s-wlan%2d' % (wlan['ssid'], idx + 1)
            wlan_conf_list.append(wlan)    
             
    return wlan_conf_list

def create_wlans(zd, wlan_conf_list=None):
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

def verify_wlans_webui(zd, expected_wlan_name_list):
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
    
def create_wlangroups(zd, wlan_conf_list, ssid_index=0, num_of_wgs=32):
    wlan_group_prefix = 'wlan_group_prefix'
    try:
        WGS.create_multi_wlan_groups(zd, wlan_group_prefix, 
                                     wlan_conf_list[ssid_index]['ssid'],
                                     num_of_wgs=num_of_wgs - 1)
        passmsg = 'The %s WLAN Groups are created successfully' % (num_of_wgs)
        logging.debug(passmsg)
        
    except Exception, e:
        
        errmsg = '[WLAN groups creating failed] %s' % e.message
        logging.debug(errmsg)
        raise Exception(errmsg)
    
def verify_wlangroups_webui(zd, num_of_wgs=32):
    # Verify the WLANs list show on the ZD if they are match with the expected WLANs
    wlan_group_prefix = 'wlan_group_prefix'
    wlan_group_list_on_zd = WGS.get_wlan_groups_list(zd)
    err_wlan_groups = []
    
    for i in range (num_of_wgs - 1):
        expected_wlan_group_name = wlan_group_prefix + '-%s' % (i + 1)
        if expected_wlan_group_name not in wlan_group_list_on_zd:
            err_wlan_groups.append(expected_wlan_group_name)
            
    if err_wlan_groups:
        errmsg = 'The expected WLAN group(s) %s is/are not shown on the WebUI' % err_wlan_groups
        logging.debug(errmsg)
        return {'Fail':errmsg}
    
    passmsg = 'WLAN Groups %s are shown on Zone Director correctly' % wlan_group_list_on_zd
    logging.debug(passmsg)               
    return {'PASS':passmsg}


def remove_all_wlans_groups(zd):
    # Base on the WLAN configuration list to create WLANs on ZD WebUI
    try:
        logging.info("Remove all WLAN Groups on the Zone Director.")
        WGS.remove_wlan_groups(zd, None)
        passmsg = 'All WLAN Groups are deleted successfully'
        logging.debug(passmsg)
        
    except Exception, e:
        errmsg = '[WLAN Groups deleting failed] %s' % e.message
        logging.debug(errmsg)        

def restart_and_wait( zd ):
#    zd._login()
    
    zd.navigate_to(zd.ADMIN,zd.ADMIN_RESTART)
    zd.s.click(loc_admin_restart_btn)
    time.sleep(2)
    if zd.s.is_confirmation_present():
        logging.info("Got confirmation: %s" % zd.s.get_confirmation())
        
    time_out = 1200
    logging.info("The Zone Director is being restarted. This process takes from 3 to 5 minutes. Please wait...")
    start_time = time.time()
    while True:
        if time.time()-start_time > time_out:
            raise Exception("Error: Timeout")
        res = ping(zd.ip_addr)
        if res.find("Timeout") != -1:
            break
        time.sleep(2)    
        
    logging.info("The Zone Director is being restarted. Please wait...")
    while True:
        if time.time()-start_time > time_out:
            raise Exception("Error: Timeout")
        
        res = ping(zd.ip_addr)
        if res.find("Timeout") == -1:
            break
        
        time.sleep(2)
        
    logging.info("The Zone Director has been restarted successfully.")
    time.sleep(15)
    
    logging.info("Please wait while I am trying to navigate to the ZD's main URL[%s]." % zd.url)
    time_out = 600 
    start_time = time.time()
    while True:
        if time.time()-start_time > time_out:
            raise Exception("Error: Timeout. Cannot url to ZD[%s]." % zd.url)
        
        try:
            zd.s.open(zd.url)
            zd.current_tab = zd.LOGIN_PAGE
            break
        
        except:
            time.sleep(2)
            pass 
               
def remove_all_wlans(zd):
    # Base on the WLAN configuration list to create WLANs on ZD WebUI
    try:
        WLAN.delete_all_wlans(zd)
        passmsg = 'All WLANs are deleted successfully'
        logging.debug(passmsg)
        
    except Exception, e:
        errmsg = '[WLANs deleting failed] %s' % e.message
        logging.debug(errmsg)
        
def update_zd_cfg(zdcfg, **kwargs):
    if kwargs.has_key('zd_ip_addr'):
        zdcfg['ip_addr'] = kwargs['zd_ip_addr']
        
    if kwargs.has_key('zd_username'):
        zdcfg['username'] = kwargs['zd_username']
        
    if kwargs.has_key('zd_password'):
        zdcfg['password'] = kwargs['zd_password']
        
    if kwargs.has_key('zd_shell_key'):
        zdcfg['shell_key'] = kwargs['zd_shell_key']

def usage():
    """
        Description:
            Apply  WLANs + WLANGroups to APs(SimAPs and RuckusAPs) ZoneDirector in scaling ENV, involved SimAPs Server etc.
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
            tea.py scaling_zd_wlans_wgs_restart te_root=u.zd.scaling zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
            tea.py scaling_zd_wlans_wgs_restart te_root=u.zd.scaling chk_gui=True debug=True
            tea.py scaling_zd_wlans_wgs_restart te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
    """
            
def main(**kwargs):
    mycfg = dict(chk_gui=False, debug=False)
    mycfg.update(kwargs)
    zd = do_config(**mycfg) 
    try:     
        msg = do_test(zd, **mycfg)
        if msg.has_key('FAIL'):
            logging.error(msg['FAIL'])
            do_clean_up(zd)
            return {"FAIL": msg }
        do_clean_up(zd)
        return {"PASS":""}
    finally:
        zd.s.shut_down_selenium_server()  
                
