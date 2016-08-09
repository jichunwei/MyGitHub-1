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
    3. failover from Active ZD.
    4. make sure the Active ZD become Standby, and the Standby become Active, and take over all the Active ZD.
    5. repeat step 4.
    6. clean up the smart redundancy configuration
    

Usage example:
    1. tea.py u.zd.failover_redundancy_zd
    2. tea.py u.zd.failover_redundancy_zd zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3
    3. tea.py u.zd.failover_redundancy_zd zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing

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
#    sw = tcfg['sw']
    share_secret = 'testing'
    
    redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret)
    logging.info('Clear all Events in 2 ZDs')
    zd1.clear_all_events()
    zd2.clear_all_events()
    
    zd1_state = redundancy_zd.get_local_device_state(zd1)
#    zd1_state = zd_state['zd1']
    if zd1_state == 'active':
        failover_active_zd(zd1)
        check_event(zd1)
    else:
        failover_active_zd(zd2)
        check_event(zd2)
        
def do_clean_up(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)

def failover_active_zd(zd):
    logging.info('Test for fail over button in active ZD')
    zd_state = redundancy_zd.get_local_device_state(zd)
    logging.debug('The ZD %s current state is %s', zd.ip_addr, zd_state)
    
    logging.info('Click failover button on ZD %s',zd.ip_addr)
    redundancy_zd.failover(zd)
    

def check_event(zd):
    logging.info('Check the event log has contain failover message')
    events_log = zd.getEvents()
    find_string_enable = '[Smart Redundancy] Received failover command for changing state to ~state~'
    redundancy_zd.check_events(events_log, find_string_enable)

def main(**cfg):
    default_cfg = dict(
                       debug=False,
                       zd1_ip_addr='192.168.0.2',
                       zd2_ip_addr = '192.168.0.3',
                       share_secret = 'testing'
                       )
    default_cfg.update(cfg)
    
    tcfg = do_config(default_cfg)
    msg = do_test(tcfg)
    do_clean_up(tcfg)
    
    tcfg['zd1'].destroy()
    tcfg['zd2'].destroy()
    
    return msg
    
    