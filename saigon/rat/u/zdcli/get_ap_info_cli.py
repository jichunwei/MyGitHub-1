"""

by louis.lou@ruckuswireless.com
2010-8-31
test procedure:
1.

"""
import logging
import time
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,    
)
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as cli
from RuckusAutoTest.components.lib.zd import access_points_zd as ap

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    zd = ZoneDirector(default_cfg)
    return dict(zdcli = zdcli, zd = zd)

def do_test(zd, zdcli, **kwargs):
    ap_info_on_zd = ap.get_all_ap_info(zd)
    mac_list = ap_info_on_zd.keys()
    for mac in mac_list:
        description = 'AP-description-%s' % time.strftime("%H%M%S")
        device_name = 'AP-device-name-%s' % time.strftime("%H%M%S")
        logging.info('Configure the AP')
        ap_cfg = dict(mac=mac,description=description,device_name=device_name)
        ap.set_ap_cfg_info(zd, ap_cfg)
        
    logging.info('Show ap all')
    all_ap_info_on_cli = cli.show_ap_all(zdcli)
    logging.info('All the AP information on CLI is \n%s' % all_ap_info_on_cli)
    
    logging.info('Show AP information in GUI')
    all_ap_info_on_zd = zd.get_all_ap_info()
    logging.info('All the AP information on GUI is \n%s:' % all_ap_info_on_zd)
    
    logging.info("Verify show ap all")
    if not cli.verify_ap_all(all_ap_info_on_cli, all_ap_info_on_zd):
        return ("FAIL")
    device_name_list = []
#    mac_list = []
    for ap_info in all_ap_info_on_zd:
        device_name_list.append(ap_info['device_name'])
#        mac_list.append(ap_info['mac'])
    for dev_name in device_name_list:
        ap_info_on_cli = cli.show_ap_info_by_name(zdcli, dev_name)
        k = ap_info_on_cli['AP']['ID'].keys()[0]
        mac = ap_info_on_cli['AP']['ID'][k]['MAC Address']
        ap_info_on_zd = zd.get_ap_info_ex(mac)
        cli.verify_ap_name(ap_info_on_cli, ap_info_on_zd,k)
        
    for mac in mac_list:
        ap_info_on_cli = cli.show_ap_info_by_mac(zdcli, mac) 
        k = ap_info_on_cli['AP']['ID'].keys()[0]
        cli.verify_ap_mac(ap_info_on_cli, ap_info_on_zd,k)   
        
    return("PASS")
def do_clean_up(zd,zdcli):
    try:
        del(zdcli)
        zd.s.shut_down_selenium_server()
        del(zd)
                
    except:
        pass
    
    
def main(**kwargs):
    try:
        cfg = do_config(**kwargs)
        zdcli = cfg['zdcli']
        zd = cfg['zd']
        
        res = do_test(zd,zdcli, **kwargs)         
        return res
    finally:
        do_clean_up(zd,zdcli)
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)