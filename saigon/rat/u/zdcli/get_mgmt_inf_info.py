"""

 
"""
import logging
import time
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,    
)
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt_inf
from RuckusAutoTest.components.lib.zdcli import mgmt_interface_info as cli
#from RuckusAutoTest.components.lib.zd import access_points_zd as ap


default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    zd = ZoneDirector(default_cfg)
    return dict(zdcli = zdcli, zd = zd)

def do_test(zd, zdcli, **kwargs):
    logging.info('Disable MGMT IF via GUI')
    mgmt_inf.disable_mgmt_inf(zd)
    
    logging.info('Show MGMT-IF information via CLI')
    mgmt_if_info_cli = cli.show_mgmt_if_info(zdcli)
    
    logging.info('Verify MGMT-IF status is Disabled')
    cli.verify_no_mgmt_if_info(mgmt_if_info_cli)
    
    
    logging.info('Set MGMT Interface Info')
    ip_addr = '192.168.1.2'
    net_mask = '255.255.255.0'
    vlan = 2
    
    mgmt_inf.enable_mgmt_inf(zd, ip_addr, net_mask, vlan)
    
    logging.info('Get MGMT Info via GUI')
    mgmt_if_info_zd = mgmt_inf.get_mgmt_inf(zd)
    
    logging.info('Show MGMT info vai CLI')
    mgmt_if_info_cli = cli.show_mgmt_if_info(zdcli)
    
    logging.info('Verify MGMT-IF information are correct')
    cli.verify_mgmt_if_info(mgmt_if_info_cli, mgmt_if_info_zd)
    
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