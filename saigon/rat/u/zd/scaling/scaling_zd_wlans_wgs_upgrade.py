"""
    Description:
        Upgrade ZoneDirector with wlans and wlan groups in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
    Prerequisites:
      1) TFTP server is runing at your ENV, "install_apimg.sh" script and "rcks_fw.bl7" 
      image exist at TFTP server root folder
      2) All of SimAPs are running at your ENV and all of them are connected. 
    Usage:
        tea.py <scaling_zd_wlans_wgs_upgrade key/value pair> ...
        
        where <scaling_zd_wlans_wgs_upgrade key/value pair> are:
          tftpserver        :     'ipaddr of tftp server'
          zd_ip_addr        :     'ipaddr of ZoneDirector'
          zd_username       :     'uername of ZoneDirector'
          zd_password       :     'password of ZoneDirector'
          zd_shell_key      :     'enter key of super mode against ZD.'
          sim_version       :     'image version of SIMAP'
          image             :     'image file of ZoneDirector which provide for upgrading'
          chk_gui           :     'True then will verify from ZoneDirector GUI'
          num_of_wlans      :     'number of wlans want to create'
          num_of_wgs        :     'number of wlan groups want to create'          
        notes:
    Examples:
        tea.py scaling_zd_wlans_wgs_upgrade te_root=u.zd.scaling tftpserver='192.168.0.20'  sim_version='8.7.0.0.10' image="zd3k_8.7.0.0.17.ap_8.7.0.0.15.img" zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG" num_of_wlans=3 num_of_wgs=3
        tea.py scaling_zd_wlans_wgs_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_shell_key="!v54!" chk_gui=True debug=True
        tea.py scaling_zd_wlans_wgs_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_shell_key="!v54! M6l@06BPTWL4zJXg3J18bvoPVLJaEtTk"
        tea.py scaling_zd_wlans_wgs_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  image="zd3k_8.7.0.0.17.ap_8.7.0.0.15.img"
        tea.py scaling_zd_wlans_wgs_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_ip_addr='192.168.0.2'
        tea.py scaling_zd_wlans_wgs_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
"""

import time
import os
import logging

from RuckusAutoTest.components.lib.zd import wlan_zd as WLAN
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as WGS

from lib import scaling_zd_lib as lib
from lib import scaling_utils as utils
from u.zd.simap import simap_image_installer as installer


zdcfg = {'ip_addr': '192.168.0.2',
         'username': 'admin',
         'password': 'admin',
         'shell_key':'!v54!'
         }  

time_cfg = {'gui_timeout':120 * 10,
          'cli_timeout':120 * 10,
          }

package_simap_cfg = {'upgrade_simap':True,
                     'tftpserver':'192.168.0.180',
                     'model':'ss2942 ss7942',
                     'version':'8.7.0.0.4',
                     'shell_key':zdcfg['shell_key'],
                     'do_install_ap' : True,
                     'do_upload_image':True,
                     'do_upload_script':True,
                     }

imgcfg = {'img_file_path': 'E:/p4/qa_auto/tools/rat-branches/tikona86/rat/zd3k_8.7.0.0.17.ap_8.7.0.0.15.img',
          'forceUpgrade': True,
          'rmDatafiles': False} 

cmps = {'zd':None, 'zdcli':None, 'agents':None}

#=======================================================

def do_config(**kwargs):
    utils.halt(kwargs['debug']) 
    update_zd_cfg(zdcfg, **kwargs)
    update_package_cfg(package_simap_cfg, **kwargs)
    update_image_cfg(imgcfg, **kwargs)
    if not verify_image(imgcfg['img_file_path']):
        return {"FAIL":"can't find your image[%s]" % imgcfg['img_file_path']}
    
    zd = utils.create_zd(**zdcfg)
    zdcli = utils.create_zd_cli(**zdcfg)
    cmps['zd'] = zd
    cmps['zdcli'] = zdcli 
    zd.removeAllConfig()
    
    return {"PASS":""}

def do_test(**kwargs):
    
    utils.halt(kwargs['debug'])
    zd = cmps['zd']
    aps = lib.resolve_verify_all_aps(zd)
    
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
    
    logging.info('try to upgrade zd...')
    errmsg = upgrade_zd_firmware(zd)
    if errmsg:
        return errmsg
    
    logging.info('try to upgrade Sim AP firmware.')
    
    zdcli = utils.create_zd_cli(**zdcfg)
    cmps['zdcli'] = zdcli
    installer.main(**package_simap_cfg)
    time.sleep(5)
    logging.info("Navigate to the ZD's URL.")
    zd.s.open(zd.url)
    zd.current_tab = zd.LOGIN_PAGE
    
    res = lib.check_all_aps_status_from_cmd(zdcli, aps, time_out=time_cfg['cli_timeout'], chk_mac=True)
    if not res :
        return {"FAIL":"time out when try to wait for all APs connecting."} 

    if kwargs['chk_gui'] :
        res = lib.check_aps_status_from_gui(zd, aps, time_out=time_cfg['gui_timeout'])
        if not res : 
            return {"FAIL":"some APs haven't connected successfully."}
        
    res = verify_wlans_webui(zd, expected_wlan_name_list)
    if res.has_key('FAIL'):
        return res
    
    res = verify_wlangroups_webui(zd, num_of_wgs=num_of_wgs)
    if res.has_key('FAIL'):
        return res
    
    remove_all_wlangroups(zd) 
    remove_all_wlans(zd)
    utils.halt(kwargs['debug'])  
      
    return {"PASS":""}

def do_clean_up():
    if cmps['zd']:
        cmps['zd'].removeAllConfig()

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
        
    else :
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

def remove_all_wlans(zd):
    # Base on the WLAN configuration list to create WLANs on ZD WebUI
    try:
        WLAN.delete_all_wlans(zd)
        passmsg = 'All WLANs are deleted successfully'
        logging.debug(passmsg)
        
    except Exception, e:
        errmsg = '[WLANs deleting failed] %s' % e.message
        logging.debug(errmsg)
        
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


def remove_all_wlangroups(zd):
    # Base on the WLAN configuration list to create WLANs on ZD WebUI
    try:
        logging.info("Remove all WLAN Groups on the Zone Director.")
#            zhlp.WGS.removeWlanMembersOutOfWlanGroup(self.zd, self.wlan_group_list_on_zd[self.ssid_index], self.wlan_conf_list)
        WGS.remove_wlan_groups(zd, None)
        passmsg = 'All WLAN Groups are deleted successfully'
        logging.debug(passmsg)
        
    except Exception, e:
        errmsg = '[WLAN Groups deleting failed] %s' % e.message
        logging.debug(errmsg)        

def upgrade_zd_firmware(zd):
    
    """
        1. upgrade firmware to what you need.
        2. verify firmware version which has upgraded successfully.
    """
    t0 = time.time()       
    try:
        logging.info('try to upgrade ZD by image[%s]' % imgcfg['img_file_path'])
        lib.upgrade_sw(zd, imgcfg['img_file_path'])
        
    except Exception, e:
        return {'FAIL' : '[RESTORE ERROR]: %s' % e.message}
    
    if imgcfg['rmDatafiles']:
        os.remove(imgcfg['img_file_path'])
        elapsed = time.time() - t0
        logging.info('elapsed time : %d' % elapsed)
    return ''

def update_zd_cfg(zdcfg, **kwargs):
    if kwargs.has_key('zd_ip_addr'):
        zdcfg['ip_addr'] = kwargs['zd_ip_addr']
        
    if kwargs.has_key('zd_username'):
        zdcfg['username'] = kwargs['zd_username']
        
    if kwargs.has_key('zd_password'):
        zdcfg['password'] = kwargs['zd_password']
        
    if kwargs.has_key('zd_shell_key'):
        zdcfg['shell_key'] = kwargs['zd_shell_key']

def update_package_cfg(pcfg, **kwargs): 
    if kwargs.has_key('tftpserver'):
        pcfg['tftpserver'] = kwargs['tftpserver']
        
    if kwargs.has_key('models'):
        pcfg['model'] = kwargs['models']
        
    if kwargs.has_key('sim_version'):
        pcfg['version'] = kwargs['sim_version']
        
    if kwargs.has_key('zd_shell_key'):
        pcfg['shell_key'] = kwargs['zd_shell_key']

def update_image_cfg(imgcfg, **kwargs):
    if kwargs.has_key('image'):
        imgcfg['img_file_path'] = kwargs['image']
        
    imgcfg['img_file_path'] = os.path.realpath(imgcfg['img_file_path'])
    if kwargs.has_key('forceUpgrade'):
        imgcfg['forceUpgrade'] = kwargs['forceUpgrade']
        
    if kwargs.has_key('rmDatafiles'):
        imgcfg['rmDatafiles'] = kwargs['rmDatafiles']

def verify_image(filename):
    if os.path.exists(filename):
        return True
    
    else :
        return False
        
def usage():
    """
    Description:
        Upgrade ZoneDirector in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
    Prerequisites:
      1) TFTP server is runing at your ENV, "install_apimg.sh" script and "rcks_fw.bl7" 
      image exist at TFTP server root folder
      2) All of SimAPs are running at your ENV and all of them are connected. 
    Usage:
        tea.py <scaling_zd_upgrade key/value pair> ...
        
        where <scaling_zd_upgrade key/value pair> are:
          tftpserver        :     'ipaddr of tftp server'
          zd_ip_addr        :     'ipaddr of ZoneDirector'
          zd_username       :     'uername of ZoneDirector'
          zd_password       :     'password of ZoneDirector'
          zd_shell_key      :     'enter key of super mode against ZD.'
          sim_version       :     'image version of SIMAP'
          image             :     'image file of ZoneDirector which provide for upgrading'
          chk_gui           :     'True then will verify from ZoneDirector GUI'
          num_of_wlans      :     'number of wlans want to create'
          num_of_wgs        :     'number of wlan groups want to create'          
        notes:
    Examples:
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  sim_version='8.7.0.0.4' image="zd3k_8.7.0.0.17.ap_8.7.0.0.15.img" zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_shell_key="!v54!" chk_gui=True debug=True
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_shell_key="!v54! M6l@06BPTWL4zJXg3J18bvoPVLJaEtTk"
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  image="zd3k_8.7.0.0.17.ap_8.7.0.0.15.img"
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_ip_addr='192.168.0.2'
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
    """
    pass

def main(**kwargs):
    mycfg = dict(chk_gui=False, debug=False)
    mycfg.update(kwargs)
    try:
        msg = do_config(**mycfg)
        if msg.has_key('FAIL'):
            logging.error('failure reason:%s' % msg['FAIL'])
            msg = do_clean_up()
            
        else:        
            msg = do_test(**mycfg)
            if msg.has_key('FAIL'):
                logging.error(msg['FAIL'])
                do_clean_up()
                return {"FAIL": msg }
            
            do_clean_up()
            
        return {"PASS":""}
    
    finally:
        if cmps['zd'] :
            cmps['zd'].s.shut_down_selenium_server()
            