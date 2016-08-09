'''
This is a tea program which test ZD Mac.Addr comparison of smart redundancy function

by Louis Lou

require:
    ZoneDirector1 ---- zd1
    ZoneDirector2 ---- zd2

Test:
    1. Disable Smart Redundancy on 2 ZDs.
    2. Make sure the higher ZD Mac_addr has more AP.
    3. Enable Smart Redundancy on 2 ZDs.
    4. Verify the ZD which has more AP become the Active ZD.
    5. Verify the ZD which has less AP become the Standby ZD
    6. clean up the smart redundancy configuration

Usage example:
    1. tea.py u.zd.ap_comparison_redundancy_zd.py
    2. tea.py u.zd.ap_comparison_redundancy_zd.py zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3
    3. tea.py u.zd.ap_comparison_redundancy_zd.py zd1_ip_addr=192.168.0.2 zd2_ip_addr=192.168.0.3 share_secret=testing

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
#
    return dict(zd1 = zd1, zd2 = zd2,sw = sw,ap_list = aplist)


def do_test(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    sw = tcfg['sw']
    return(
           comparsion_ap(zd1,zd2,sw),
           )


def do_clean_up(tcfg):
    zd1 = tcfg['zd1']
    zd2 = tcfg['zd2']
    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)


def comparsion_ap(zd1,zd2,sw):
#    redundancy_zd.disable_pair_smart_redundancy(zd1, zd2)
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

        if len(zd1_active_ap_list) < len(zd2_active_ap_list):
            redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret)
            if redundancy_zd.get_local_device_state(zd1).lower() == 'standby':
                return("PASS",'ZD2 [%s] has %d APs more than ZD1 [%s] has %d APs, so ZD2 become Active' %
                       (zd2.ip_addr,len(zd2_active_ap_list),zd1.ip_addr,len(zd1_active_ap_list)))
            else:
                return('FAIL','ZD2 [%s] has %d APs more than ZD1 [%s] has %d APs, but ZD2 become Standby' %
                       (zd2.ip_addr,len(zd2_active_ap_list),zd1.ip_addr,len(zd1_active_ap_list)))


        elif len(zd1_active_ap_list) == len(zd2_active_ap_list) != 0:
            number_ap_to_move = (len(zd1_active_ap_list) - len(zd2_active_ap_list))
            ap_cmd = 'set director ip  '+ zd2.ip_addr
            for i in range(0,number_ap_to_move):
                zd1_active_ap_list[i].do_cmd(ap_cmd)
                zd1_active_ap_list[i].do_cmd('reboot')

        else:
            redundancy_zd.enable_pair_smart_redundancy(zd1, zd2, share_secret)
            if redundancy_zd.get_local_device_state(zd1).lower() == 'active':
                return("PASS",'ZD2 [%s] has %d APs less than ZD1 [%s] has %d APs, so ZD2 become Standby' %
                       (zd2.ip_addr,len(zd2_active_ap_list),zd1.ip_addr,len(zd1_active_ap_list)))
            else:
                return('FAIL','ZD2 [%s] has %d APs less than ZD1 [%s]  has %d APs, but ZD2 become Active' %
                       (zd2.ip_addr,len(zd2_active_ap_list),zd1.ip_addr,len(zd1_active_ap_list)))

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

