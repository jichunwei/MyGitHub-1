'''
'''
import copy
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    default_conf = {
        'language': 'English',
        'system_name': 'ruckus',
        'country_code': 'United States',
        'mesh_enabled': False,
        'ip_dualmode': True,
        'dhcp_enabled': True,
        'ipv6_autoconfig': True,
        'wireless1_enabled': True,
        'wireless1_name': 'Ruckus-Wireless-1',
        'authentication_open': True,
        'guest_wlan_enabled': False,
        'admin_name': 'admin',
        'admin_password': '',
        'create_user_account_is_checked': False,
    },
    new_conf = {
        'dhcp_enabled': False,
        'ip_addr': '192.168.0.2',
        'net_mask': '255.255.255.0',
        'gateway': '192.168.0.253',
        'dns1': '192.168.0.252',

        'wireless1_enabled': True,
        'wireless1_name': 'rat-setup-wizard',
        'authentication_open': True,

        'create_user_account_is_checked': True,
        'new_user_name': 'user',
        'new_user_password': 'password'
    }
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))

    return _cfg


def do_test(cfg):
    logging.info('[TEST 01] Setup Wizard with Default information')
    cfg['zd'].setup_wizard_cfg()

    logging.info('[TEST 02] Setup Wizard with provided default config')
    cfg['zd'].setup_wizard_cfg(cfg['default_conf'])

    logging.info('[TEST 03] Setup Wizard with new config')
    cfg['zd'].setup_wizard_cfg(new_conf = cfg['new_conf'])

    logging.info('[TEST 04] Setup Wizard with provided default config and new config')
    cfg['zd'].setup_wizard_cfg(cfg['default_conf'], cfg['new_conf'])

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
[UserExit] model fix_test_param DOES not exist, function ignored at [Thu Feb 17 11:53:29 2011].
2011-02-17 11:53:31,759 INFO     [TEA.Module u.zd.test123] tcfg:
{'u.zd.test123': None}
2011-02-17 11:53:31,759 DEBUG    Creating the Selenium Manager
2011-02-17 11:53:31,759 DEBUG    [selenium_jar]: D:\dev\saigon\rat\RuckusAutoTest\common\selenium-server.jar
2011-02-17 11:53:36,759 INFO     Creating Zone Director component [192.168.0.2]
2011-02-17 11:53:36,759 DEBUG    {'browser_type': 'firefox',
 'config': {'password': 'admin', 'username': 'admin'},
 'https': True,
 'ip_addr': '192.168.0.2',
 'selenium_mgr': <RuckusAutoTest.common.SeleniumControl.SeleniumManager instance at 0x01936198>}
2011-02-17 11:53:59,009 DEBUG    Updating edit_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,009 DEBUG    Updating wlan_member_chk_tmpl in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,009 DEBUG    Updating edit_member_wlan_vlan_tag in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,009 DEBUG    Updating check_name_default in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,009 DEBUG    Updating edit_description in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,009 DEBUG    Updating check_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,025 DEBUG    Updating doEdit in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,025 DEBUG    Updating edit_member_wlan_vlan_no_change in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating doDelete in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating wlan_member_tbl in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating get_description in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_Cancel in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_OK in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating doEdit_default in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_member_wlan_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_member_wlan_tag_override in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating select_all in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating show_more_button in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_member_wlan_vlan_untag in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_member_vlan_override in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating doClone in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating get_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating get_totals in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating create_new in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating get_wgs_name in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_member_wlan_original_vlan in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating doNext in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating edit_member_vlan_wlan in wlan_groups_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating LOCATORS_CFG_WLANGROUPS in wlan_groups_zd module to the version 9.2.0.99
2011-02-17 11:53:59,040 DEBUG    Updating info in guest_access_zd module to the version 8.2.0.0
2011-02-17 11:53:59,040 DEBUG    Updating const in guest_access_zd module to the version 8.2.0.0
2011-02-17 11:53:59,040 DEBUG    Updating _log_to_the_page in guest_access_zd module to the version 8.2.0.0
2011-02-17 11:53:59,040 DEBUG    Updating xlocs in control_zd module to the version 8.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating LOCATORS_CFG_ACCESSPOINTS in access_points_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating LOCATORS_SPEEDFLEX in speedflex_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating LOCATORS_CFG_WLANS in wlan_zd module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating install_simap in image_installer module to the version 8.2.0.0
2011-02-17 11:53:59,040 DEBUG    Updating install in image_installer module to the version 8.2.0.0
2011-02-17 11:53:59,040 DEBUG    Updating install_simap in image_installer module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating install in image_installer module to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating info in ZoneDirector2 class instance to the version 8.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating info in ZoneDirector2 class instance to the version 8.2.0.0
2011-02-17 11:53:59,040 DEBUG    Updating shell_key in ZoneDirector2 class instance to the version 8.2.0.0
2011-02-17 11:53:59,040 DEBUG    Updating remove_all_cfg in ZoneDirector2 class instance to the version 9.0.0.0
2011-02-17 11:53:59,040 DEBUG    Updating info in ZoneDirector2 class instance to the version 9.2.0.99
2011-02-17 11:53:59,055 INFO     [TEST 01] Setup Wizard with Default information
2011-02-17 11:54:03,352 INFO     The Zone Director is being reset. Please wait...
2011-02-17 11:54:13,461 INFO     The Zone Director is being restarted. Please wait...
2011-02-17 11:55:09,977 INFO     The Zone Director has been reset successfully to factory configuration.
2011-02-17 11:55:09,977 INFO     Navigate to the ZD's WebUI URL: https://192.168.0.2
2011-02-17 11:55:10,336 INFO     Stand on the Language page
2011-02-17 11:55:11,868 INFO     Stand on the General page
2011-02-17 11:55:13,447 INFO     Stand on the Management IP page
2011-02-17 11:55:15,275 INFO     Stand on the Wireless LANs page
2011-02-17 11:55:16,977 INFO     Stand on the Admin Name page
2011-02-17 11:55:19,384 INFO     Stand on the Finish page
2011-02-17 11:55:24,493 INFO     Navigate to the Zone Director's homepage: https://192.168.0.2
2011-02-17 11:55:29,040 INFO     [TEST 02] Setup Wizard with provided default config
2011-02-17 11:55:39,743 INFO     The Zone Director is being reset. Please wait...
2011-02-17 11:55:49,977 INFO     The Zone Director is being restarted. Please wait...
2011-02-17 11:56:46,993 INFO     The Zone Director has been reset successfully to factory configuration.
2011-02-17 11:56:46,993 INFO     Navigate to the ZD's WebUI URL: https://192.168.0.2
2011-02-17 11:56:47,352 INFO     Stand on the Language page
2011-02-17 11:56:48,900 INFO     Stand on the General page
2011-02-17 11:56:50,555 INFO     Stand on the Management IP page
2011-02-17 11:56:52,572 INFO     Stand on the Wireless LANs page
2011-02-17 11:56:54,525 INFO     Stand on the Admin Name page
2011-02-17 11:56:57,040 INFO     Stand on the Finish page
2011-02-17 11:57:02,118 INFO     Navigate to the Zone Director's homepage: https://192.168.0.2
2011-02-17 11:57:06,650 INFO     [TEST 03] Setup Wizard with new config
2011-02-17 11:57:16,211 INFO     The Zone Director is being reset. Please wait...
2011-02-17 11:57:26,493 INFO     The Zone Director is being restarted. Please wait...
2011-02-17 11:58:23,009 INFO     The Zone Director has been reset successfully to factory configuration.
2011-02-17 11:58:23,009 INFO     Navigate to the ZD's WebUI URL: https://192.168.0.2
2011-02-17 11:58:23,540 INFO     Stand on the Language page
2011-02-17 11:58:25,086 INFO     Stand on the General page
2011-02-17 11:58:26,634 INFO     Stand on the Management IP page
2011-02-17 11:58:31,540 INFO     Stand on the Wireless LANs page
2011-02-17 11:58:33,743 INFO     Stand on the Admin Name page
2011-02-17 11:58:37,400 INFO     Stand on the Finish page
2011-02-17 11:58:42,477 INFO     Navigate to the Zone Director's homepage: https://192.168.0.2
2011-02-17 11:58:42,618 INFO     [TEST 04] Setup Wizard with provided default config and new config
2011-02-17 11:58:52,180 INFO     The Zone Director is being reset. Please wait...
2011-02-17 11:59:02,493 INFO     The Zone Director is being restarted. Please wait...
2011-02-17 11:59:59,009 INFO     The Zone Director has been reset successfully to factory configuration.
2011-02-17 11:59:59,009 INFO     Navigate to the ZD's WebUI URL: https://192.168.0.2
2011-02-17 11:59:59,336 INFO     Stand on the Language page
2011-02-17 12:00:00,884 INFO     Stand on the General page
2011-02-17 12:00:02,540 INFO     Stand on the Management IP page
2011-02-17 12:00:07,634 INFO     Stand on the Wireless LANs page
2011-02-17 12:00:10,086 INFO     Stand on the Admin Name page
2011-02-17 12:00:13,852 INFO     Stand on the Finish page
2011-02-17 12:00:18,930 INFO     Navigate to the Zone Director's homepage: https://192.168.0.2
2011-02-17 12:00:19,102 DEBUG    Clean up the Selenium Manager
2011-02-17 12:00:19,211 INFO     [TEA.Module u.zd.test123] Result:
None
2011-02-17 12:00:19,211 INFO     Close logging file D:\dev\saigon\runlog\tea_u.zd.test123\log_tea_u.zd.test123_201102171153.txt
DEBUG:root:Clean up the Selenium Manager
'''
