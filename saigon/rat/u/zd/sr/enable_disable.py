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
        +check the events log
    3. disable zd1 and zd2 smart redundancy via Web UI.
        +check the "Enable Smart Redundancy" check box is off
        +check the events log
    4. negative test
        +enable zd1 and zd2 smart redundancy via Web UI using different share secret
        +enable zd1 and zd2 smart redundancy via Web UI using invalid peer device IP address
        check the events log 
    5. clean up the smart redundancy configuration

Usage example:
    1. tea.py u.zd.enable_redundancy_zd
    2. tea.py u.zd.enable_redundancy_zd zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3
    3. tea.py u.zd.enable_redundancy_zd zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing

'''

import time
import logging

from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import redundancy_zd
from RuckusAutoTest.common import lib_Debug as bugme

def do_config(tcfg):
    zd1 = ZoneDirector(dict(ip_addr=tcfg['zd1_ip_addr']))
    zd2 = ZoneDirector(dict(ip_addr=tcfg['zd2_ip_addr']))
    time.sleep(5)
    
    logging.info('Make sure the smart redundancy was disabled')
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
      
    logging.info('Clear all the events in the 2 ZDs')
    zd1.clear_all_events()
    zd2.clear_all_events()
    
    return dict(zd1 = zd1, zd2 = zd2)


def do_test(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    share_secret = 'testing'
    
    logging.info('Verify the Smart Redundancy can be ENABLED via Web UI')
    logging.info('Make sure the ZD %s and ZD %s smart redundancy with the share secret %s' % (zd1.ip_addr,zd2.ip_addr,share_secret))
    if redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret):
        logging.info("The smart redundancy was enabled via WEB UI")
        logging.info('Make sure the Events log has enable Smart Redundancy log')
        events_log1_enable = zd1.getEvents()
        events_log2_enable = zd2.getEvents()
        find_string_enable = 'Smart Redundancy is [enabled]'

        redundancy_zd.check_events(events_log1_enable,find_string_enable)
        redundancy_zd.check_events(events_log2_enable,find_string_enable) 
    else:
        return("FAIL","The smart redundancy was NOT enabled via Web UI")
 
    logging.info("Verify the Smart Redundancy can be DISABLED via Web UI")
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
    logging.info('Make sure the Events has disable Smart Redundancy log')
    events_log1_disable = zd1.getEvents()
    events_log2_disable = zd2.getEvents()
    find_string_disable = 'Smart Redundancy is [disabled]'
    
    redundancy_zd.check_events(events_log1_disable,find_string_disable)
    redundancy_zd.check_events(events_log2_disable,find_string_disable)
    
    test_different_share_secret(tcfg)
    test_different_peer_ip(tcfg)
    return("PASS, all the steps are corrected")
        
def do_clean_up(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
  
        
def test_different_share_secret(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    share_secret = 'testing'
    timeout = 30
    
    different_share_secret = share_secret + 'test'
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
    
    zd1.clear_all_events()
    zd2.clear_all_events()
    
    logging.info('Make sure 2 ZD can NOT become a pair smart redundancy ZD with different share secret')
    redundancy_zd.enable_single_smart_redundancy(zd1, zd2.ip_addr, share_secret) 
    redundancy_zd.enable_single_smart_redundancy(zd2, zd1.ip_addr, different_share_secret)
    start_time = time.time()
    while True:
        if redundancy_zd._get_peer_device_ip_address_status(zd1)[1].lower() == 'shared secret mismatched':
            logging.info("correct behavior, the shared secret mismatched, so it is not a pair smart redundancy ZD")
            events_log = zd1.getEvents()
            for events in events_log:
                if events.__contains__("[Smart Redundancy] Failed! Shared Secrets are mismatched"):
                    logging.info("OK, there is mismatched info in events log")
                break
        
        if redundancy_zd.get_local_device_state(zd1) == 'active':
            if redundancy_zd.get_local_device_state(zd2) =='standby': 
                logging.info('Incorrect behavior -- Enable smart redundancy successfully, and the ZD1 %s is the active ZD' % zd1.ip_addr)
                return ('FAIL','')
                
        elif redundancy_zd.get_local_device_state(zd1) =='standby': 
            if redundancy_zd.get_local_device_state(zd2) =='active':
                logging.info('Incorrect behavior -- Enable smart redundancy successfully, and the ZD2 %s is the active ZD' % zd2.ip_addr)
                return ("FAIL",'')
            
        if time.time() - start_time > timeout:
            logging.info("The 2 ZD don't be enable smart redundancy after %d seconds--Correct behavior" % timeout)
            break
        

def test_different_peer_ip(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    share_secret = 'testing'
    timeout = 30
    pause = 5
    ip_addr='1.1.1.1'
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
    
    zd1.clear_all_events()
    zd2.clear_all_events()
    
    redundancy_zd.enable_single_smart_redundancy(zd1, ip_addr, share_secret) 
    redundancy_zd.enable_single_smart_redundancy(zd2, ip_addr, share_secret)
    start_time = time.time()
    while True:
        if redundancy_zd._get_peer_device_ip_address_status(zd1)[1].lower() == 'disconnected':
            if redundancy_zd._get_peer_device_ip_address_status(zd2)[1].lower() == 'disconnected':
                logging.info("Correct behavior, the peer IP disconnected, so it is not a pair smart redundancy ZD")
                break
        elif redundancy_zd._get_peer_device_ip_address_status(zd1)[1].lower().find('mismatched'):
            logging.info("Correct behavior, the peer IP mismatched, so it is not a pair smart redundancy ZD")
            break
        elif redundancy_zd.get_local_device_state(zd1) == 'active':
            if redundancy_zd.get_local_device_state(zd2) =='standby': 
                logging.info('Incorrect behavior -- Enable smart redundancy successfully, and the ZD1 %s is the active ZD' % zd1.ip_addr)
                return ('FAIL','')
                
        elif redundancy_zd.get_local_device_state(zd1) =='standby': 
            if redundancy_zd.get_local_device_state(zd2) =='active':
                logging.info('Incorrect behavior -- Enable smart redundancy successfully, and the ZD2 %s is the active ZD' % zd2.ip_addr)
                return ("FAIL",'')
        else:
            time.sleep(pause)
                
        if time.time() - start_time > timeout:
            logging.info("The 2 ZD don't be enable smart redundancy after %d seconds" % pause)
            break
        

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
    
    