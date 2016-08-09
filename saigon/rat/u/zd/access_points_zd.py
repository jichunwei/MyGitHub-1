'''
'''

import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib


'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    mac = '68:92:34:2a:9f:00',
)

def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    # NEW PUBLIC ACCESS METHODS
    ap_cfg = lib.zd.ap.get_ap_config_by_mac(cfg['zd'], cfg['mac'])
    pp(ap_cfg)
    lib.zd.ap.set_ap_config_by_mac(cfg['zd'], cfg['mac'], **ap_cfg)

    logging.info('[TEST 101] Set/Get AP General Info')
    lib.zd.ap.set_ap_general_by_mac_addr(cfg['zd'], cfg['mac'])
    pp(lib.zd.ap.get_ap_general_info_by_mac(cfg['zd'], cfg['mac']))

    logging.info('[TEST 102] Set/Get AP IP Config')
    lib.zd.ap.set_ap_ip_config_by_mac_addr(cfg['zd'], cfg['mac'])
    pp(lib.zd.ap.get_ap_ip_config_by_mac(cfg['zd'], cfg['mac']))

    logging.info('[TEST 103] Set/Get AP Radio Config')
    lib.zd.ap.set_ap_radio_by_mac_addr(cfg['zd'], cfg['mac'], 'ng')
    pp(lib.zd.ap.get_ap_radio_config_by_mac(cfg['zd'], cfg['mac']))

    logging.info('[TEST 104] Set/Get AP Mesh Config')
    lib.zd.ap.set_ap_mesh_by_mac_addr(cfg['zd'], cfg['mac'])
    pp(lib.zd.ap.get_ap_mesh_config_by_mac(cfg['zd'], cfg['mac']))


    # ADAPTER METHODS FOR ZONEDIRECTOR
    logging.info('[TEST 105] zd.get_ap_cfg')
    ap_cfg = cfg['zd'].get_ap_cfg(cfg['mac'])
    pp(ap_cfg)

    logging.info('[TEST 106] zd.set_ap_cfg')
    ip_management = ap_cfg['ip_management']
    ip_management.update({'by-dhcp': 'manual'})
    new_ap_cfg = {
        'mac_addr': ap_cfg['mac_addr'],
        'channelization': 'Auto',
        'channel': 'Auto',
        'txpower': 'Auto',
        'mesh_uplink_aps': ap_cfg['mesh_uplink_aps'],
        'ip_management': ip_management,
    }
    cfg['zd'].set_ap_cfg(new_ap_cfg)

    # OLD/UN-MODIFIED METHODS + MODIFIED METHODS + ADAPTER METHODS SECTION
    logging.info('[TEST 201] get_limited_zd_discovery_cfg')
    pp(lib.zd.ap.get_limited_zd_discovery_cfg(cfg['zd']))

    logging.info('[TEST 202] get_cfg_info_by_mac_addr')
    pp(lib.zd.ap.get_cfg_info_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 203] _get_ap_supported_radios')
    pp(lib.zd.ap._get_ap_supported_radios(cfg['zd'], cfg['mac']))

    logging.info('[TEST 204] default_wlan_groups_by_mac_addr')
    lib.zd.ap.default_wlan_groups_by_mac_addr(cfg['zd'], cfg['mac'])


    logging.info('[TEST 205] cfg_wlan_groups_by_mac_addr')
    ap_rp = {'ng': {'default': True},
             'na': {'default': True}}
    lib.zd.ap.cfg_wlan_groups_by_mac_addr(cfg['zd'], cfg['mac'], ap_rp)

    logging.info('[TEST 206] cfg_wlan_groups_by_mac_addr')
    ap_rp = {'ng': {'wlangroups': 'Default', 'channel': '6'},
             'na': {'wlangroups': 'Default', 'channel': '149'}}
    lib.zd.ap.cfg_wlan_groups_by_mac_addr(cfg['zd'], cfg['mac'], ap_rp)

    logging.info('[TEST 207] assign_to_wlan_groups_by_radio')
    lib.zd.ap.assign_to_wlan_groups_by_radio(cfg['zd'], cfg['mac'], 'Default')

    logging.info('[TEST 208] assign_to_default_wlan_group')
    lib.zd.ap.assign_to_default_wlan_group(cfg['zd'], cfg['mac'])

    logging.info('[TEST 209] assign_all_ap_to_default_wlan_group')
    lib.zd.ap.assign_all_ap_to_default_wlan_group(cfg['zd'])

    logging.info('[TEST 210] get_ap_cfg')
    pp(lib.zd.ap.get_ap_cfg(cfg['zd'], cfg['mac'], ['ng', 'na']))

    logging.info('[TEST 211] cfg_ap')
    cfg_set = {'radio': 'ng', 'channel': '6', 'wlan_service': True}
    lib.zd.ap.cfg_ap(cfg['zd'], cfg['mac'], cfg_set)

    logging.info('[TEST 212] get_ap_cfg_2')
    pp(lib.zd.ap.get_ap_cfg_2(cfg['zd'], cfg['mac']))

    logging.info('[TEST 213] get_ap_cfg_list')
    pp(lib.zd.ap.get_ap_cfg_list(cfg['zd'], [cfg['mac']]))

    logging.info('[TEST 214] get_all_ap_cfg')
    pp(lib.zd.ap.get_all_ap_cfg(cfg['zd']))

    logging.info('[TEST 215] get_radio_cfg_options')
    pp(lib.zd.ap.get_radio_cfg_options(cfg['zd'], cfg['mac']))


    cfg['result'] = 'PASS'
    cfg['message'] = ''
    return cfg


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)

    res = None
    try:
        res = do_test(tcfg)

    except Exception, ex:
        print ex.message

    do_clean_up(tcfg)

    return res

'''
'''