# test methods introduced in ZD 8.0 and later
import re
import time
import logging
import pdb

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components import Helpers as lib

def pause_test_for(_pause, _with_reason):
    logging.info("[PAUSE %s] %s" % (str(_pause), _with_reason))
    time.sleep(_pause)

def check_wlan_on_ap_is_up(active_ap, ssid, check_status_timeout = 180, pause = 2):
    wlan_if = active_ap.ssid_to_wlan_if(ssid)
    logging.info("Verify WLAN [%s %s] is UP on the AP [%s %s]"
                % (ssid, wlan_if, active_ap.get_base_mac(), active_ap.ip_addr))
    start_time = time.time()
    while True:
        for (wlan_id, wlan) in active_ap.get_wlan_info_dict().iteritems():
            if wlan['wlanID'] == wlan_if and wlan['status'] == 'up':
                return ''

        timed_out = time.time() - start_time > check_status_timeout
        if timed_out:
            errmsg = "WLAN [%s %s] on AP [%s %s] is not up" \
                        % (ssid, wlan_if, active_ap.get_base_mac(), active_ap.ip_addr)
            return errmsg

        msg = "WLAN [%s %s] on AP [%s %s] is not up" \
            % (ssid, wlan_if, active_ap.get_base_mac(), active_ap.ip_addr)

        pause_test_for(pause, msg)


# wgs_cfg must have 'name', 'ap_na', 'ap_ng'; description is optional.
def assign_1ap_to_1wlan_with_wlan_groups(ZD, ap_mac, wlan_cfg, wgs_cfg):
    if not wgs_cfg.has_key('description'): wgs_cfg['description'] = '1AP-to-1WLAN-by-wgs'
    lib.zd.wgs.create_wlan_group(ZD,
                               wgs_cfg['name'],
                               wlan_cfg['ssid'],
                               False,
                               wgs_cfg['description'])
    wgs_info = lib.zd.wgs.get_wlan_group_of_member(ZD,
                                              wgs_cfg['name'],
                                              wlan_cfg['ssid'])
    lib.zd.ap.cfg_wlan_groups_by_mac_addr(ZD,
                                       ap_mac,
                                       wgs_cfg['ap_rp'],
                                       wgs_cfg['description'])
    wgs_apinfo = lib.zd.ap.get_cfg_info_by_mac_addr(ZD, ap_mac)
    # no client in the wga_name/ap at this moment
    ap_xstatus = lib.zd.wgs.get_status_ex_by_ap_mac_addr(ZD,
                                                  wgs_cfg['name'],
                                                  ap_mac)
    return (wgs_info, wgs_apinfo, ap_xstatus)

def assign_1ap_to_exist_wlan_with_wlan_groups(ZD, ap_mac, wgs_cfg):
    if not wgs_cfg.has_key('description') or wgs_cfg['description'] == None:
        wgs_cfg['description'] = '1AP-to-existWLAN-by-wgs'

    wlan_name_list = lib.zd.wlan.get_wlan_list(ZD)
    lib.zd.wgs.create_wlan_group(ZD,
                             wgs_cfg['name'],
                             wlan_name_list,
                             False,
                             wgs_cfg['description'])
    lib.zd.ap.cfg_wlan_groups_by_mac_addr(ZD,
                                      ap_mac,
                                      wgs_cfg['ap_rp'],
                                      wgs_cfg['description'])
    wgs_apinfo = lib.zd.ap.get_cfg_info_by_mac_addr(ZD, ap_mac)
    # no client in the wga_name/ap at this moment
    ap_xstatus = lib.zd.wgs.get_status_ex_by_ap_mac_addr(ZD, wgs_cfg['name'], ap_mac)
    return (wgs_apinfo, ap_xstatus)

#
# default components' values
#
def get_default_wlan_cfg(vlan_id = None):
    """ Return a default WLAN configuration that can bu used with new syntax accepted by the function
    _set_wlan_cfg in module wlan_zd.py """
    # "Open System" profile
    return { 'ssid': 'rat-wgs',
             'auth': 'open',
             'encryption': 'none',
             'wpa_ver': '',
             'key_string': '',
             'key_index': '',
             'username': '',
             'password': '',
             'vlan_id': vlan_id}

def get_default_wlan_groups_cfg(radio_mode = 'g'):
    if re.search(r'[an]+', radio_mode):
        # AP will be made to assocate with 5.0G radio
        wgs_cfg = {'name': 'wlan-wg-na', 'description': 'utest-wgs50-na', 'ap_na': {}, 'ap_ng': {}}
        wgs_cfg['ap_na'] = {'wlangroups': wgs_cfg['name']}
        wgs_cfg['ap_ng'] = {'default': True}
    else:
        wgs_cfg = {'name': 'wlan-wg-ng', 'description': 'utest-wgs24-ng', 'ap_na': {}, 'ap_ng': {}}
        wgs_cfg['ap_na'] = {'default': True}
        wgs_cfg['ap_ng'] = {'wlangroups': wgs_cfg['name']}
    return wgs_cfg


def assoc_station_with_bssid(target_station, wlan_cfg, bssid, check_status_timeout):
    logging.info("Configure a WLAN with SSID %s on the target station %s" % \
                 (wlan_cfg['ssid'], target_station.get_ip_addr()))
    target_station.cfg_wlan(wlan_cfg)

    target_station.connect_to_wlan(wlan_cfg['ssid'], bssid)

    logging.info("Check association status of the target station %s" % target_station.get_ip_addr())
    start_time = time.time()
    while True:
        if target_station.get_current_status() == "connected":
            break
        time.sleep(1)
        if time.time() - start_time > check_status_timeout:
            msg = "The station %s didn't associate to the wireless network after %d seconds" % \
                  (target_station.get_ip_addr(), check_status_timeout)
            return msg
    return ""


