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
    3. click failover button in active ZD.
    4. make sure the active become standby and the standby become active and take over all the active AP. 
    5. repeat step 4 for 24 hours.   
    6. clean up the smart redundancy configuration

Usage example:
    1. tea.py u.zd.failover_button_24hours
    2. tea.py u.zd.failover_button_24hours zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3
    3. tea.py u.zd.failover_button_24hours zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing
    4. tea.py u.zd.failover_button_24hours zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing run_time=0.5
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
    share_secret = tcfg['share_secret']
    hour = tcfg['run_time']
    
    redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret)
    timeout = hour * 60 * 60
    start_time = time.time()
    while True:
        logging.info('Clear all Events in 2 ZDs')
        zd1.clear_all_events()
        zd2.clear_all_events()
        
        zd1_state = redundancy_zd.get_local_device_state(zd1)
        if zd1_state == 'active':
            failover_active_zd(zd1)
            check_event(zd1)
        else:
            failover_active_zd(zd2)
            check_event(zd2)
        if time.time() - start_time > timeout:
            break
        
        
def do_clean_up(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
    tcfg['zd1'].destroy()
    tcfg['zd2'].destroy()
    
    
def failover_active_zd(zd):
    logging.info('Test for fail over button in active ZD')
    zd_state = redundancy_zd.get_local_device_state(zd)
    logging.debug('The ZD %s current state is %s', zd.ip_addr, zd_state)
    
    logging.info('Click failover button on ZD %s',zd.ip_addr)
    redundancy_zd.failover(zd)
    

def check_event(zd):
    logging.info('Check the event log has contain failover message')
    events_log = zd.getEvents()
    find_string = '[Smart Redundancy] * failover *'
    redundancy_zd.check_events(events_log, find_string)

def main(**cfg):
    default_cfg = dict(
                       debug = False,
                       zd1_ip_addr = '192.168.0.2',
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
    
    