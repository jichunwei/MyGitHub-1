'''
This is the unit tests for table header feature

Requirements
+ zd

Test
+ Make sure the displayed on ZD match with what those function results
+ For functions under /lib/zd/access_points_zd.py, active_clients_zd.py and
  /ZoneDirector.py, make sure the output consistent with previous implementation
    + /lib/zd/aps.py
      get_all_ap_briefs
      get_ap_brief_by_mac_addr

    + /lib/zd/access_points_zd.py
      get_ap_info_by_mac
      get_all_ap_info

    + /lib/zd/active_clients_zd.py
      get_all_clients_briefs

    + /ZoneDirector.py
      get_all_ap_info
      get_ap_info_ex

+ For those functions below, make sure the ap is rebooted
    + /lib/zd/aps.py
       reboot_all_aps
       reboot_ap_by_mac_addr

    + /lib/zd/access_points_zd.py
       reboot_ap

    + /ZoneDirector.py
       restart_aps

+ For those functions below, make sure the ap is allowed to be joined
  Requirements
  + disabled 'Automatically approve all joining requests' feature
  + make sure there is a new AP waiting for join ZD
    + /lib/zd/aps.py
       allow_ap_joining_by_mac_addr

    + /ZoneDirector.py
       allow_ap_joining

Examples
tea.py u.zd.table_to_dict
    test=get zd_ip_addr=192.168.0.2 ap_mac_addr=00:1d:2e:15:ff:c0
    test=join zd_ip_addr=192.168.0.2 ap_mac_addrs="['00:1d:2e:15:ff:c0', '00:22:7f:24:a9:80']"
    test=reboot zd_ip_addr=192.168.0.2 ap_mac_addr=00:1d:2e:15:ff:c0
'''

import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.common.utils import wait_for
from RuckusAutoTest.components import create_zd_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components import Helpers as lib


'''
. put your default config here
. standard config:
  . zd_ip_addr
  . fm_ip_addr
  . zd
  . fm
'''
default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    test = 'get',
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def _test_get(cfg):
    '''
    input
    . ap_mac_addr
    '''
    logging.info('[TEST 01] Get the whole/an item on ZD > Access Points table'
                 ' and return as dict (or list)')

    logging.info('[TEST 01.01] Get the whole ZD > Access Points table'
                 ' and return as dict (or list)')
    logging.info('[TEST 01.01.01] by the newly developed module'
                 ' (lib.zd.aps.get_all_ap_briefs)')
    pp(lib.zd.aps.get_all_ap_briefs(cfg['zd']))

    logging.info('[TEST 01.01.02] by the lib.zd.ap.get_all_ap_info'
                 ' (for backward compatible)')
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)
    pp(lib.zd.ap.get_all_ap_info(cfg['zd']))

    logging.info('[TEST 01.01.03] by the lib.zd.ap.get_all_ap_info'
                 ' (for backward compatible)')
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)
    pp(cfg['zd'].get_all_ap_info())

    logging.info('[TEST 01.02] Get one entry [with MAC Address = %s] on'
                 ' ZD > Access Points table and return as dict'
                 % cfg['ap_mac_addr'])
    logging.info('[TEST 01.02.01] by the newly developed module'
                 ' (lib.zd.get_ap_brief_by_mac_addr)')
    pp(lib.zd.aps.get_ap_brief_by_mac_addr(cfg['zd'], cfg['ap_mac_addr']))

    logging.info('[TEST 01.02.02] by the lib.zd.ap.get_ap_info_by_mac'
                 ' (for backward compatible)')
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)
    pp(lib.zd.ap.get_ap_info_by_mac(cfg['zd'], cfg['ap_mac_addr']))

    logging.info('[TEST 01.02.03] by the zd.get_all_ap_info'
                 ' (for backward compatible)')
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)
    pp(cfg['zd'].get_all_ap_info(cfg['ap_mac_addr']))

    logging.info('[TEST 01.02.04] by the zd.get_ap_info_ex'
                 ' (for backward compatible)\n'
                 'Notice: this could take a long while...')
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)
    pp(cfg['zd'].get_ap_info_ex(cfg['ap_mac_addr']))

    logging.info('[TEST 01.03] Get the whole/an item on ZD > Currently Active Clients table'
                 ' and return as dict (or list)')
    logging.info('[TEST 01.03.01] by the newly developed module'
                 ' (lib.cac.get_all_clients_briefs)')
    pp(lib.zd.cac.get_all_clients_briefs(cfg['zd']))

    logging.info('[TEST 01.03.02] by the zd.get_active_client_list'
                 ' (for backward compatible)')
    cfg['zd'].navigate_to(cfg['zd'].MONITOR, cfg['zd'].MONITOR_CURRENTLY_ACTIVE_CLIENTS)
    pp(cfg['zd'].get_active_client_list())

    cfg['result'] = 'PASS'
    cfg['message'] = 'The Access Points table can be get and populate in a ' \
                    'dict (or list). One item on the table can be get.'
    return cfg


def _test_join(cfg):
    '''
    input
    . ap_mac_addrs: a list of 2 addresses for 2 tests
    '''
    logging.info('[TEST 02] Allow an AP to join ZD by MAC')
    logging.info('[TEST 02.01] by the newly developed module'
                 ' (lib.zd.aps.allow_ap_joining_by_mac_addr)')
    lib.zd.aps.allow_ap_joining_by_mac_addr(cfg['zd'], cfg['ap_mac_addrs'][0])

    logging.info('[TEST 02.02] by the zd.allow_ap_joining'
                 ' (for backward compatible)')
    cfg['zd'].allow_ap_joining(cfg['ap_mac_addrs'][1])

    cfg['result'] = 'PASS'
    cfg['message'] = 'Able to let the APs to join ZD'
    return cfg


def _test_reboot(cfg):
    '''
    input
    . ap_mac_addr
    '''
    logging.info('[TEST 03] Reboot an AP [%s]/all APs'
                 % cfg['ap_mac_addr'])
    logging.info('[TEST 03.01] Reboot an AP [%s]' % cfg['ap_mac_addr'])
    logging.info('[TEST 03.01.01] by the newly developed module'
                 ' (lib.zd.aps.reboot_ap_by_mac_addr)')
    lib.zd.aps.reboot_ap_by_mac_addr(cfg['zd'], cfg['ap_mac_addr'])

    wait_for('the AP [%s] to boot up to perform next test'
             % cfg['ap_mac_addr'], 2 * 60)
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)

    logging.info('[TEST 03.01.02] by the lib.zd.ap.reboot_ap'
                 ' (for backward compatible)')
    lib.zd.ap.reboot_ap(cfg['zd'], cfg['ap_mac_addr'])

    wait_for('the AP [%s] to boot up to perform next test'
             % cfg['ap_mac_addr'], 2 * 60)
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)

    logging.info('[TEST 03.01.03] by the zd.restart_aps'
                 ' (for backward compatible)')
    cfg['zd'].restart_aps(cfg['ap_mac_addr'])

    wait_for('the AP [%s] to boot up to perform next test'
             % cfg['ap_mac_addr'], 2 * 60)
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)

    logging.info('[TEST 03.02] Reboot all APs')
    logging.info('[TEST 03.02.01] by the newly developed module'
                 ' (lib.zd.aps.reboot_all_aps)')
    lib.zd.aps.reboot_all_aps(cfg['zd'])

    wait_for('all APs to boot up to perform next test', 2 * 60)
    cfg['zd'].navigate_to(cfg['zd'].DASHBOARD, cfg['zd'].NOMENU)

    logging.info('[TEST 03.02.01] by the zd.restart_aps'
                 ' (for backward compatible)')
    cfg['zd'].restart_aps()

    wait_for('all APs to boot up', 2 * 60)

    cfg['result'] = 'PASS'
    return cfg


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    if cfg['test'] == 'get':
        return _test_get(cfg)
    elif cfg['test'] == 'join':
        return _test_join(cfg)
    elif cfg['test'] == 'reboot':
        return _test_reboot(cfg)


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
