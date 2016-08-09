'''
This is a tea program which test ZD Mac.Addr comparison of smart redundancy function

by Louis Lou

require:
    ZoneDirector1 ---- zd1
    ZoneDirector2 ---- zd2

Test:
    1. clear all the configuration on 2 ZDs
    2. check all AP's MAC and disable the ports which AP connected on NetGear switch
    3. make sure there are no APs on the 2 ZDs
    4. enable zd1 and zd2 smart redundancy via Web UI using the same share secret
        + check local device IP address status
        + check peer device IP address status
        if zd1 ---> active , zd2 ---> standby
        else zd1 ---> standby , zd2 ---> active
    5. ZD of low MAC address will become active ZD, another will be standby ZD
    5. clean up the smart redundancy configuration

Usage example:
    1. tea.py u.zd.mac_comparison_redundancy_zd.py
    2. tea.py u.zd.mac_comparison_redundancy_zd.py zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3
    3. tea.py u.zd.mac_comparison_redundancy_zd.py zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing

'''

import time
import logging

from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.NetgearL3Switch import NetgearL3Switch
from RuckusAutoTest.components.RuckusAP import RuckusAP
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
    aplist = []
#    aplist.append(zd1.get_all_ap_sym_dict())
#    aplist.append(zd2.get_all_ap_sym_dict())
#
    return dict(zd1 = zd1, zd2 = zd2,sw = sw,ap_list = aplist)


def do_test(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    sw = tcfg['sw']
    return(
           comparsion_mac_without_ap(zd1,zd2),
           comparsion_mac_with_same_ap(zd1,zd2,sw)
           )
#    comparsion_mac_without_ap(zd1,zd2)
#    time.sleep(30)
#    comparsion_mac_with_same_ap(zd1,zd2,sw)


def do_clean_up(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)

def comparsion_mac_without_ap(zd1,zd2):
    zd1.navigate_to(zd1.DASHBOARD, zd1.NOMENU)
    zd1_mac_addr = zd1.get_mac_address()

    zd2.navigate_to(zd2.DASHBOARD, zd1.NOMENU)
    zd2_mac_addr = zd2.get_mac_address()
    logging.debug('The ZD1 %s mac address is %s and ZD2 %s mac address is %s' % (
                  zd1.ip_addr,zd1_mac_addr,zd2.ip_addr,zd2_mac_addr))

    zd1._delete_all_aps()
    zd2._delete_all_aps()
    share_secret = 'testing'
    redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret)

    if cmp(zd1_mac_addr,zd2_mac_addr) == -1:
        logging.info('ZD1 mac address is lower')
        if redundancy_zd.get_local_device_state(zd1).lower() == 'active':
            return("PASS",'ZD1 mac [%s] is lower than ZD2 [%s] and become active ZD' % (zd1_mac_addr,zd2_mac_addr))
        else:
            return('FAIL','ZD1 mac [%s] is lower than ZD2 [%s] but become standby ZD' % (zd1_mac_addr,zd2_mac_addr))
    else:
        logging.info('ZD2 mac address is lower')
        if redundancy_zd.get_local_device_state(zd2).lower() == 'active':
            return("PASS",'ZD2 mac [%s] is lower than ZD1 [%s] and become active ZD' % (zd2_mac_addr,zd1_mac_addr))
        else:
            return('FAIL','ZD2 mac [%s] is lower than ZD1 [%s] but become standby ZD' % (zd2_mac_addr,zd1_mac_addr))


def comparsion_mac_with_same_ap(zd1,zd2,sw):
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
    share_secret = 'testing'
    zd1.navigate_to(zd1.DASHBOARD, zd1.NOMENU)
    zd1_mac_addr = zd1.get_mac_address()

    zd2.navigate_to(zd2.DASHBOARD, zd2.NOMENU)
    zd2_mac_addr = zd2.get_mac_address()
    logging.debug('The ZD1 %s mac address is %s and ZD2 %s mac address is %s',
                  zd1.ip_addr,zd1_mac_addr,zd2.ip_addr,zd2_mac_addr)
#    bugme.do_trace('debug')
    while True:
        zd1_active_ap_list = []
        zd2_active_ap_list = []

        logging.info("Get ZD %s all active APs", zd1.ip_addr)

        all_ap_in_zd1_dict = zd1.get_all_ap_info()
        for ap in all_ap_in_zd1_dict:
            if not ap['status'].lower().find('connected'):
#                zd1_active_ap_list.append(ap)
                zd1_active_ap = RuckusAP(dict(ip_addr = ap['ip_addr'],username='admin',password='admin'))
                zd1_active_ap_list.append(zd1_active_ap)
        logging.info("Get ZD %s all active APs", zd2.ip_addr)
        all_ap_in_zd2_dict = zd2.get_all_ap_info()
        for ap in all_ap_in_zd2_dict:
            if not ap['status'].lower().find('connected'):
                zd2_active_ap = RuckusAP(dict(ip_addr = ap['ip_addr'],username='admin',password='admin'))
                zd2_active_ap_list.append(zd2_active_ap)

        if len(zd1_active_ap_list) == len(zd2_active_ap_list) != 0:
            redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret)
            if cmp(zd1_mac_addr,zd2_mac_addr) == -1:
                logging.info('ZD1 mac address is lower')
                if redundancy_zd.get_local_device_state(zd1).lower() == 'active':
                    return("PASS",'ZD1 mac [%s] is lower than ZD2 [%s] and become active ZD when they both have  %d APs' %
                           (zd1_mac_addr,zd2_mac_addr,len(zd1_active_ap_list)))
                else:
                    return('FAIL','ZD1 mac [%s] is lower than ZD2 [%s] but become standby ZD when they have oth have  %d APs' %
                           (zd1_mac_addr,zd2_mac_addr,len(zd1_active_ap_list)))
            else:
                logging.info('ZD2 mac address is lower')
                if redundancy_zd.get_local_device_state(zd2).lower() == 'active':
                    return("PASS",'ZD2 mac [%s] is lower than ZD1 [%s] and become active ZD when they both have  %d APs' %
                           (zd2_mac_addr,zd1_mac_addr,len(zd2_active_ap_list)))
                else:
                    return('FAIL','ZD2 mac [%s] is lower than ZD1 [%s] but become standby ZD when they both have  %d APs' %
                           (zd2_mac_addr,zd1_mac_addr,len(zd2_active_ap_list)))

        elif len(zd1_active_ap_list) > len(zd2_active_ap_list):
            number_ap_to_move = (len(zd1_active_ap_list) - len(zd2_active_ap_list)) / 2
    #        for ap in zd1_active_ap_list:
            cmd = 'set director ip  '+ zd2.ip_addr
            for i in range(0,number_ap_to_move):
                zd1_active_ap_list[i].do_cmd(cmd)
                zd1_active_ap_list[i].do_cmd('reboot')
        elif len(zd1_active_ap_list) < len(zd2_active_ap_list):
            number_ap_to_move = (len(zd1_active_ap_list) - len(zd2_active_ap_list)) / 2
            cmd = 'set director ip  ' + zd1.ip_addr
            for i in range(0,number_ap_to_move):
                zd2_active_ap_list[i].do_cmd(cmd)
                zd2_active_ap_list[i].do_cmd('reboot')

        time.sleep(150)
        zd1.s.refresh()
        zd2.s.refresh()


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

