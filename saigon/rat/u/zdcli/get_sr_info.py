"""

 
"""
import logging
import time
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,    
)
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr
#from RuckusAutoTest.components.lib.zd import access_points_zd as ap


default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    zd = ZoneDirector(default_cfg)
    return dict(zdcli = zdcli, zd = zd)

def do_test(zd, zdcli, **kwargs):
    
    logging.info('Show SR Info')
    sr_info = sr.show_sr_info(zdcli)
    logging.info(sr_info)
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