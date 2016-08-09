'''
Description:
    Configure L2 ACL information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com
'''

import sys
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist


def define_wlan_cfg():

    _wlan_cfgs = dict()

    _wlan_cfgs['open-none'] = (
        dict(
            name = 'open-none-' + utils.make_random_string(random.randint(2,22),type = 'alpha'),
            description = utils.make_random_string(random.randint(1,64),type = 'alpha'),
            type = 'standard-usage'
        )
    )

    return _wlan_cfgs


def define_test_cfg(cfg):
    fcfg = {
        'acl_policy_list': [],
    }
    fcfg.update(cfg)

    #wlan_cfg_dict = define_wlan_cfg()
    acl_policy_list = fcfg['acl_policy_list']
    #target_ip_addr = fcfg['ras_ip_addr']

    
    #@author: Liang Aihua, @change: keep consistent with rat.db
    #test_name = 'CB_ZD_Create_Station'
    #common_name = 'Create target station'
    #test_cfgs.append(({'sta_ip_addr': cfg['target_station'],
    #                   'sta_tag': "sta1"}, test_name, common_name, 0, False))

    #test_name = 'CB_Station_Remove_All_Wlans'
    #common_name = 'Remove all wlans from station'
    #test_cfgs.append(({'sta_tag': "sta1"}, test_name, common_name, 0, False))

    l2acl_conf_list =[]
    for acl_policy in acl_policy_list:
        l2acl_conf_list.extend(gen_acl_policy(acl_policy))
        
        #@author: Liang Aihua, @change: 2014-11-13
        #test_name = 'CB_ZD_Remove_All_Wlans'
        #common_name = '[L2 ACL "%s"] Remove all WLAN from ZD' % acl_policy['policy']
        #test_cfgs.append(({}, test_name, common_name, 1, False))
    test_cfgs =[]
    test_name = 'CB_ZD_Remove_All_L2_ACLs'
    common_name = 'Clean all L2 ACLs from ZD WebUI'
        #common_name = '[L2 ACL "%s"] Clean all L2 ACLs from ZD WebUI' % acl_policy['policy']
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Create_L2_ACLs'
    common_name = '[L2 ACL] Create 2 L2 ACLs via CLI'
        #common_name = '[L2 ACL "%s"] Create 2 L2 ACLs via CLI' % acl_policy['policy']
    param_cfg = dict(l2acl_conf_list = l2acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

        #test_name = 'CB_ZD_CLI_Create_Wlan'
        #common_name = '[L2 ACL "%s"] Create a WLAN on ZDCLI' % acl_policy['policy']
        #wlan_conf = deepcopy(wlan_cfg_dict['open-none'])
        #wlan_conf.update({'l2acl': l2acl_conf_list[0]['acl_name'],
        #                  'ssid': wlan_conf['name'],
        #                  'auth': "open",
        #                  'encryption': "none"})
        #test_cfgs.append(( {'wlan_conf': wlan_conf}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Verify_L2_ACLs_CLISet_CLIGet'
    common_name = '[L2 ACL] Verify L2ACL CLI Set and CLI Get are the same info'
        #common_name = '[L2 ACL "%s"] Verify L2ACL CLI Set and CLI Get are the same info' % acl_policy['policy']
    param_cfg = dict(l2acl_conf_list = l2acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_L2_ACLs_CLISet_GUIGet'
    common_name = '[L2 ACL] Verify L2 ACL CLI Set and GUI Get are the same info'
        #common_name = '[L2 ACL "%s"] Verify L2 ACL CLI Set and GUI Get are the same info' % acl_policy['policy']
    param_cfg = dict(l2acl_conf_list = l2acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        #@author: Liang Aihua, @change: 2014-11-13
        #is_negative = True
        #if acl_policy['policy'] == 'allow':
        #    is_negative = False

        #test_name = 'CB_ZD_Associate_Station_1'
        #common_name = '[L2 ACL "%s"] Associate the station to the wlan' % acl_policy['policy']
        #test_cfgs.append(({'wlan_cfg': wlan_conf,
        #                   'sta_tag': "sta1",
        #                   'is_negative': is_negative},
        #                  test_name, common_name, 1, False))

        #if not is_negative:
        #    test_name = 'CB_ZD_Client_Ping_Dest'
        #    common_name = '[L2 ACL "%s"] Verify client can ping a target IP' % acl_policy['policy']
        #    test_cfgs.append(({'sta_tag': "sta1",
        #                       'condition': 'allowed',
        #                       'target': target_ip_addr}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Verify_L2_ACLs_Rename_Remove_MAC'
    common_name = '[L2 ACL] Verify L2 ACL Rename and Remove MAC address'
        #common_name = '[L2 ACL "%s"] Verify L2 ACL Rename and Remove MAC address' % acl_policy['policy']
    param_cfg = dict(l2acl_conf_list = l2acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    #@author: Liang Aihua, @change: 201-11-13
    #test_name = 'CB_ZD_Remove_All_Wlans'
    #common_name = 'Remove all WLAN from ZD'
    #test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_L2_ACLs'
    common_name = 'Clean all L2 ACLs from ZD WebUI'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))


    return test_cfgs


def gen_acl_policy(acl_policy):
    '''
    '''
    return [{
        'acl_name': utils.make_random_string(random.randint(2, 32), type = 'alnum'),
        'description': utils.make_random_string(random.randint(2, 32), type = 'alnum'),
        'mac_entries': acl_policy['mac_list'],
        'policy': acl_policy['policy'],
    }]


def _generate_mac_addr(num = 128):
    '''
    '''
    mac_list = []
    for i in range(num):
        mac = [0, 0, 0, 0, 0, i + 1]
        mac = ':'.join(map(lambda x: "%02x" % x, mac))
        mac_list.append(mac)

    return mac_list


def create_test_suite(**kwargs):
    ts_cfg = dict(
        interactive_mode = True,
        station = (0, "g"),
        testsuite_name = "",
    )

    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']

    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)

    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        
    allow_mac_list = raw_input("Allow listed stations: ").split()
    #@author: Liang Aihua,@change: change test logic(2014-11-18)
    #allow_mac_list.extend(_generate_mac_addr(1))
    if not allow_mac_list:
        allow_mac_list.extend(_generate_mac_addr(1))

    deny_mac_list = raw_input("Deny listed stations: ").split()
    #@author: Liang Aihua,@change: change test logic(2014-11-18)
    #deny_mac_list.extend(_generate_mac_addr(1))
    if not deny_mac_list:
        deny_mac_list.extend(_generate_mac_addr(1))

    acl_policy_list = [
        {'mac_list': allow_mac_list,
         'policy': 'allow',
        },
        {'mac_list': deny_mac_list,
         'policy': 'deny',
        },
    ]

    ts_name = 'Config L2 ACL via CLI and Verify via GUI'
    ts = testsuite.get_testsuite(ts_name, 'L2 ACL CLI Configuration', combotest = True)

    fcfg = {
        'target_station': target_sta,
        'ras_ip_addr': ras_ip_addr,
        'acl_policy_list': acl_policy_list,
    }
    test_cfgs = define_test_cfg(fcfg)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)

