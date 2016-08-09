'''
This is the unit tests table to dict when iterating table with/or without data row

Examples
tea.py u.zd.table_to_dict_datarow
'''

import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_station_by_ip_addr,
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
    sta_ip_addr = '192.168.1.11',
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def get_wlan_cfg(cfg = {}):
    p = dict(
        ssid = 'test-table-to-dict',
        description = '',
        auth = 'PSK',
        encryption = 'TKIP',
        wpa_ver = 'WPA',
        key_index = '',
        key_string = '1234567890',
        sta_auth = 'PSK',
        sta_encryption = 'TKIP',
        sta_wpa_ver = 'WPA',
    )
    p.update(cfg)
    return p


def _test_table_nodata(cfg):
    '''
    '''
    logging.info('[TEST] Iterating a table with no data row present')

    logging.info('Remove all active clients')
    cfg['zd'].remove_all_active_clients()

    logging.info('Get all active clients')
    pp(lib.zd.cac.get_all_clients_briefs(cfg['zd']))


    logging.info('[TEST] Iterating a table with data row')

    logging.info('Remove station wlan')
    cfg['sta'].remove_all_wlan()

    wlan_cfg = get_wlan_cfg()

    logging.info('Configure a wlan on the ZD')
    cfg['zd'].cfg_wlan(wlan_cfg)

    logging.info('Configure a wlan on the target station')
    cfg['sta'].cfg_wlan(wlan_cfg)

    logging.info('Get all active clients')
    pp(lib.zd.cac.get_all_clients_briefs(cfg['zd']))

    cfg['result'] = 'PASS'
    cfg['message'] = ''
    return cfg


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    _cfg['sta'] = create_station_by_ip_addr(default_cfg.pop('sta_ip_addr'))
    return _cfg


def do_test(cfg):
    return _test_table_nodata(cfg)


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
