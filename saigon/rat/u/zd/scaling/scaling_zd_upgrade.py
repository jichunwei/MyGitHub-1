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
        notes:
    Examples:
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  sim_version='8.7.0.0.4' image="zd3k_8.7.0.0.17.ap_8.7.0.0.15.img" zd_shell_key="!v54! M6l@06BPTWL4zJXg3J18bvoPVLJaEtTk"
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_shell_key="!v54!" chk_gui=True debug=True
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_shell_key="!v54! M6l@06BPTWL4zJXg3J18bvoPVLJaEtTk"
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  image="zd3k_8.7.0.0.17.ap_8.7.0.0.15.img"
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_ip_addr='192.168.0.2'
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
"""
import time
import os
import logging

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
    zd = utils.create_zd(**zdcfg)
    zdcli = utils.create_zd_cli(**zdcfg)
    cmps['zd'] = zd
    cmps['zdcli'] = zdcli
    return {"PASS":""}

def do_test(**kwargs):
    utils.halt(kwargs['debug'])
    zd = cmps['zd']
    aps = lib.resolve_verify_all_aps(zd)
    
    logging.info('try to upgrade zd...')
    errmsg = upgrade_zd_firmware(zd)
    if errmsg : return errmsg
    logging.info('try to upgrade Sim AP firmware.')
    
    zdcli = utils.create_zd_cli(**zdcfg)
    cmps['zdcli'] = zdcli
    installer.main(**package_simap_cfg)
    try:
        zd.do_login()
    except:
        pass
    
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
    return {"PASS":""}

def do_clean_up():
    pass

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
        notes:
    Examples:
        tea.py scaling_zd_upgrade te_root=u.zd.scaling tftpserver='192.168.0.180'  sim_version='8.7.0.0.4' image="zd3k_8.7.0.0.17.ap_8.7.0.0.15.img" zd_shell_key="!v54! M6l@06BPTWL4zJXg3J18bvoPVLJaEtTk"
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

