'''
This is a tea program which test enable/disable ZD smart redundancy function

by Louis Lou

require:
    ZoneDirector1 ---- zd1
    ZoneDirector2 ---- zd2

Test:
    1. clear all the configuration on 2 ZDs
    2. enable zd1 and zd2 smart redundancy via Web UI using the same share secret
        + check local device IP address status
        + check peer device IP address status
        if zd1 ---> active , zd2 ---> standby
        else zd1 ---> standby , zd2 ---> active
    3. change ZD from active to active state (also test standby to standby)
        + 1. Setup the S.R. test bed and make sure the ZD_1 will be the Active state, and ZD_2 will be the Standby state.
        + 2. Cut down the ZD_2 network capability, and make sure ZD_1 keep in Active state.
        + 3. Recover the ZD_2 network capability, and make sure ZD_1 keep in Active state.
        + ZD_1 will change from Active to Active.

    4. change ZD from  active to standby (also test standby to active)
        + 1. make sure the ZD1 will be the active state, and ZD2 will be the standby state
        + 2. cut down the ZD1 network capability, and make sure the ZD2 will be in Active state
        + 3. recover the ZD1 network capability, and make sure the ZD2 will be in Active state
        + ZD1 will change from Active to standby
        
    5. clean up the smart redundancy configuration

Usage example:
    1. tea.py u.zd.failover_eth_24hours
    2. tea.py u.zd.failover_eth_24hours zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3
    3. tea.py u.zd.failover_eth_24hours zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing 
    4. tea.py u.zd.failover_eth_24hours zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing run_time=1

'''

import time
import logging

from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.NetgearL3Switch import NetgearL3Switch
from RuckusAutoTest.components.lib.zd import redundancy_zd
#from RuckusAutoTest.common import lib_Debug as bugme

def do_config(tcfg):
    zd1 = ZoneDirector(dict(ip_addr=tcfg['zd1_ip_addr']))
    zd2 = ZoneDirector(dict(ip_addr=tcfg['zd2_ip_addr']))
    sw = NetgearL3Switch(dict())
    time.sleep(3)
    logging.info('Make sure the smart redundancy was disabled')
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
    
    zd1.clear_all_events()
    zd2.clear_all_events()
    
    return dict(zd1 = zd1, zd2 = zd2,sw = sw)


def do_test(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    sw = tcfg['sw']
    share_secret = tcfg['share_secret']
    hour = tcfg['run_time']
    logging.info("Make sure the Smart Redundancy be enabled")
    redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret)
    
    timeout = hour * 60 * 60
    start_time = time.time()
    while True:
        logging.info('Get the ZD1 %s state', zd1.ip_addr)
        zd1_state = redundancy_zd.get_local_device_state(zd1).lower()
        logging.debug('the ZD %s state is %s', zd1.ip_addr,zd1_state)
        if zd1_state == 'active':
            swap_active_to_standby(zd1,zd2,sw)
        else:
            swap_active_to_standby(zd2,zd1,sw)
            
        if time.time() - start_time > timeout:
            break
        
def do_clean_up(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
    
    tcfg['zd1'].destroy()
    tcfg['zd2'].destroy()

def swap_active_to_standby(active_zd, standby_zd,sw):
    logging.info('Verify smart redundancy state change from active to standby')
    logging.info('Get the Active ZD interface')
    active_zd_mac = active_zd.get_mac_address()
    active_zd_interface = sw.mac_to_interface(active_zd_mac)
    logging.debug('The Active ZD interface is %s',active_zd_interface)
    
    logging.info('Disable the active ZD interface')
    sw.disable_interface(active_zd_interface)
    
    time.sleep(20)
    
    logging.info('Make sure former Standby ZD %s become active', standby_zd.ip_addr)
    if redundancy_zd.get_local_device_state(standby_zd).lower() != 'active':
        return('FAIL','The former Standby ZD %s has NOT become active after 30s' % standby_zd.ip_addr)
    else:
        logging.info('The former Standby ZD %s has become active' % standby_zd.ip_addr)
    
    logging.info('Enable the former Active ZD %s interface' % active_zd.ip_addr)
    sw.enable_interface(active_zd_interface)
#    bugme.do_trace('debug')
    time.sleep(10)
    active_zd.s.refresh()
    standby_zd.s.refresh()
    logging.info('Make sure the swap successfully')
    if redundancy_zd.get_local_device_state(standby_zd).lower() == 'active':
        if redundancy_zd.get_local_device_state(active_zd).lower() == 'standby':
            logging.info("Swap active to Standby successfully,the former Active ZD is now Standby ZD and Standby ZD is now Active ZD")
            return('PASS,swap active to standby successfully')
    else:
        return("FAIL","Swap active to standby failed")
    
    
def main(**cfg):
    default_cfg = dict(
                       debug=False,
                       zd1_ip_addr='192.168.0.2',
                       zd2_ip_addr = '192.168.0.3',
                       share_secret = 'testing',
                       run_time = 24
                       )
    default_cfg.update(cfg)
    
    tcfg = do_config(default_cfg)
    tcfg.update(default_cfg)
    
    msg = do_test(tcfg)
    do_clean_up(tcfg)
    
    return msg
    
    