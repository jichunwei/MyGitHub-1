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
  . ap_mac_addr
'''
default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    ap_mac_addr = '68:92:34:1d:5a:e0',
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    logging.info('[TEST 01] Get all Member APs info of %s WLAN Group:' % 'Default')
    pp(lib.zd.wgs.get_all_mem_ap_briefs(cfg['zd'], 'Default'))

    logging.info('[TEST 02] Get info of Member AP with MAC Address %s of %s WLAN Group:' %
                 (cfg['ap_mac_addr'], 'Default'))
    pp(lib.zd.wgs.get_mem_ap_brief_by_mac(cfg['zd'], 'Default', cfg['ap_mac_addr']))

    logging.info('[TEST 03] Checking get_status_ex_by_ap_mac_addr() for backward compatibility')
    pp(lib.zd.wgs.get_status_ex_by_ap_mac_addr(cfg['zd'], 'Default', cfg['ap_mac_addr']))

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
pydev debugger: starting
[UserExit] model fix_test_param DOES not exist, function ignored at [Sat Feb 12 10:45:48 2011].
2011-02-12 10:45:50,066 INFO     [TEA.Module u.zd.wlan_groups] tcfg:
{'u.zd.wlan_groups': None}
2011-02-12 10:45:54,473 DEBUG    Creating the Selenium Manager
2011-02-12 10:45:54,473 DEBUG    [selenium_jar]: D:\dev\saigon\rat\RuckusAutoTest\common\selenium-server.jar
2011-02-12 10:45:59,487 INFO     Creating Zone Director component [192.168.0.2]
2011-02-12 10:45:59,487 DEBUG    {'browser_type': 'firefox',
 'config': {'password': 'admin', 'username': 'admin'},
 'https': True,
 'ip_addr': '192.168.0.2',
 'selenium_mgr': <RuckusAutoTest.common.SeleniumControl.SeleniumManager instance at 0x0272BDC8>}
2011-02-12 10:46:22,723 DEBUG    Updating edit_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating wlan_member_chk_tmpl in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_member_wlan_vlan_tag in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating check_name_default in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_description in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating check_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating doEdit in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_member_wlan_vlan_no_change in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating doDelete in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating wlan_member_tbl in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating get_description in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_Cancel in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_OK in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating doEdit_default in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_member_wlan_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_member_wlan_tag_override in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating select_all in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating show_more_button in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_member_wlan_vlan_untag in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating edit_member_vlan_override in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating doClone in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating get_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating get_totals in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating create_new in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,723 DEBUG    Updating get_wgs_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating edit_member_wlan_original_vlan in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating doNext in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating edit_member_vlan_wlan in wlan_groups_zd module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating LOCATORS_CFG_WLANGROUPS in wlan_groups_zd module to the version 9.2.0.99
2011-02-12 10:46:22,737 DEBUG    Updating info in guest_access_zd module to the version 8.2.0.0
2011-02-12 10:46:22,737 DEBUG    Updating const in guest_access_zd module to the version 8.2.0.0
2011-02-12 10:46:22,737 DEBUG    Updating _log_to_the_page in guest_access_zd module to the version 8.2.0.0
2011-02-12 10:46:22,737 DEBUG    Updating xlocs in control_zd module to the version 8.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating LOCATORS_CFG_ACCESSPOINTS in access_points_zd module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating LOCATORS_SPEEDFLEX in speedflex_zd module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating LOCATORS_CFG_WLANS in wlan_zd module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating install_simap in image_installer module to the version 8.2.0.0
2011-02-12 10:46:22,737 DEBUG    Updating install in image_installer module to the version 8.2.0.0
2011-02-12 10:46:22,737 DEBUG    Updating install_simap in image_installer module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating install in image_installer module to the version 9.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating info in ZoneDirector2 class instance to the version 8.0.0.0
2011-02-12 10:46:22,737 DEBUG    Updating info in ZoneDirector2 class instance to the version 8.2.0.0
2011-02-12 10:46:22,737 DEBUG    Updating shell_key in ZoneDirector2 class instance to the version 8.2.0.0
2011-02-12 10:46:22,737 DEBUG    Updating remove_all_cfg in ZoneDirector2 class instance to the version 9.0.0.0
2011-02-12 10:47:20,441 INFO     [TEST 01] Get all Member APs info of Default WLAN Group:
{u'68:92:34:1d:5a:e0': {'channel': u'48 (11a/n-40), 11 (11g/n-20)',
                        'clients': u'0',
                        'description': u'',
                        'ip_addr': u'192.168.0.131',
                        'ipv6': u'',
                        'mac': u'68:92:34:1d:5a:e0',
                        'model': u'zf7363',
                        'status': u'Connected'},
 u'68:92:34:2a:9f:00': {'channel': u'48 (11a/n-40), 6 (11g/n-20)',
                        'clients': u'0',
                        'description': u'',
                        'ip_addr': u'192.168.0.132',
                        'ipv6': u'',
                        'mac': u'68:92:34:2a:9f:00',
                        'model': u'zf7363',
                        'status': u'Connected'}}
2011-02-12 10:47:42,457 INFO     [TEST 02] Get info of Member AP with MAC Address 68:92:34:1d:5a:e0 of Default WLAN Group:
{'channel': u'48 (11a/n-40), 11 (11g/n-20)',
 'clients': u'0',
 'description': u'',
 'ip_addr': u'192.168.0.131',
 'ipv6': u'',
 'mac': u'68:92:34:1d:5a:e0',
 'model': u'zf7363',
 'status': u'Connected'}
2011-02-12 10:48:01,660 INFO     [TEST 03] Checking get_status_ex_by_ap_mac_addr() for backward compatibility
{'channel': u'48 (11a/n-40), 11 (11g/n-20)',
 'clients': u'0',
 'description': u'',
 'ip_addr': u'192.168.0.131',
 'ipv6': u'',
 'mac': u'68:92:34:1d:5a:e0',
 'model': u'zf7363',
 'status': u'Connected'}
2011-02-12 10:48:28,894 DEBUG    Clean up the Selenium Manager
2011-02-12 10:48:48,144 INFO     [TEA.Module u.zd.wlan_groups] Result:
{   'ap_mac_addr': '68:92:34:1d:5a:e0',
    'message': '',
    'result': 'PASS',
    'u.zd.wlan_groups': None,
    'zd': <RuckusAutoTest.components.ZoneDirector.ZoneDirector2 instance at 0x0272BD78>,
    'zd_ip_addr': '192.168.0.2'}
2011-02-12 10:48:52,551 INFO     Close logging file D:\dev\saigon\runlog\tea_u.zd.wlan_groups\log_tea_u.zd.wlan_groups_201102121045.txt
[ERROR] on destroying object []
DEBUG:root:Clean up the Selenium Manager

'''