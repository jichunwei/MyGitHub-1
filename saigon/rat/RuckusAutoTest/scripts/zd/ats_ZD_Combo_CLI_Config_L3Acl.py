'''
Description:
    Configure L3 ACL information on ZD CLI, verify the information on ZD GUI.
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
            name = 'open-none-' + utils.make_random_string(random.randint(2, 22), type = 'alpha'),
            description = utils.make_random_string(random.randint(1, 64), type = 'alpha'),
            type = 'standard-usage'
        )
    )

    return _wlan_cfgs


def define_test_cfg(cfg):
    fcfg = {
        'acl_policy_list': [],
    }
    fcfg.update(cfg)

    wlan_cfg_dict = define_wlan_cfg()
    acl_policy_list = fcfg['acl_policy_list']
    target_ip_addr = fcfg['ras_ip_addr']

    test_cfgs = []
    
    #@author: Liang Aihua,@change: Delete cases not exist in database.(2014-11-18)
    #test_name = 'CB_ZD_Create_Station'
    #common_name = 'Create target station'
    #test_cfgs.append(({'sta_ip_addr': cfg['target_station'],
    #                   'sta_tag': "sta1"}, test_name, common_name, 0, False))

    #test_name = 'CB_Station_Remove_All_Wlans'
    #common_name = 'Remove all wlans from station'
    #test_cfgs.append(({'sta_tag': "sta1"}, test_name, common_name, 0, False))

    #test_name = 'CB_Station_CaptivePortal_Start_Browser'
    #common_name = 'Start browser in station'
    #test_cfgs.append(({'sta_tag': "sta1",
    #                   'browser_tag': "browser1"}, test_name, common_name, 0, False))

    
    for acl_policy in acl_policy_list:
        l3acl_conf_list = gen_acl_policy(acl_policy)
    #@author: Liang Aihua,@change: Release these cases from every acl policy.(2014-11-18)
        #test_name = 'CB_ZD_Remove_All_Wlans'
        #common_name = '[L3 ACL %s]Remove all WLAN from ZD' % acl_policy['policy']
        #test_cfgs.append(({}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Remove_All_L3_ACLs'
    common_name = 'Clean all L3 ACLs from ZD WebUI'
        #common_name = '[L3 ACL "%s"] Clean all L3 ACLs from ZD WebUI' % acl_policy['policy']
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Create_L3_ACLs'
    common_name = '[L3 ACL] Create 2 L3 ACLs via CLI'
        #common_name = '[L3 ACL "%s"] Create 2 L3 ACLs via CLI' % acl_policy['policy']
    param_cfg = dict(l3acl_conf_list = l3acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

        #test_name = 'CB_ZD_CLI_Create_Wlan'
        #common_name = '[L3 ACL "%s"] Create a WLAN on ZDCLI' % acl_policy['policy']
        #wlan_conf = deepcopy(wlan_cfg_dict['open-none'])
        #wlan_conf.update({'l3acl': l3acl_conf_list[0]['acl_name'],
        #                  'ssid': wlan_conf['name'],
        #                  'auth': "open",
        #                  'encryption': "none"})
        #test_cfgs.append(( {'wlan_conf': wlan_conf}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Verify_L3_ACLs_CLISet_CLIGet'
    common_name = '[L3 ACL] Verify L3ACL CLI Set and CLI Get are the same info'
        #common_name = '[L3 ACL "%s"] Verify L3ACL CLI Set and CLI Get are the same info' % acl_policy['policy']
    param_cfg = dict(l3acl_conf_list = l3acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_L3_ACLs_CLISet_GUIGet'
    common_name = '[L3 ACL] Verify L3 ACL CLI Set and GUI Get are the same info'
        #common_name = '[L3 ACL "%s"] Verify L3 ACL CLI Set and GUI Get are the same info' % acl_policy['policy']
    param_cfg = dict(l3acl_conf_list = l3acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))

        #test_name = 'CB_ZD_Associate_Station_1'
        #common_name = '[L3 ACL "%s"] Associate the station to the wlan' % acl_policy['policy']
        #test_cfgs.append(({'wlan_cfg': wlan_conf,
        #                   'sta_tag': "sta1"},
        #                  test_name, common_name, 1, False))

        #pingable = "allowed"
        #if acl_policy['policy'] == 'allow':
        #    pingable = "disallowed"

        #test_name = 'CB_ZD_Client_Ping_Dest'
        #common_name = '[L3 ACL "%s"] Verify client can ping a target IP' % acl_policy['policy']
        #test_cfgs.append(({'sta_tag': "sta1",
        #                   'condition': pingable,
        #                   'target': target_ip_addr}, test_name, common_name, 1, False))

        #test_name = 'CB_Station_CaptivePortal_Download_File'
        #common_name = '[L3 ACL "%s"] Verify download file from server' % acl_policy['policy']
        #test_cfgs.append(({'sta_tag': "sta1",
        #                   'browser_tag': "browser1",
        #                   #'validation_url': "http://%s/authenticated/" % target_ip_addr,
        #                   }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Verify_L3_ACLs_Rename'
    common_name = '[L3 ACL] Verify L3 ACL Rename and Remove MAC address'
        #common_name = '[L3 ACL "%s"] Verify L3 ACL Rename and Remove MAC address' % acl_policy['policy']
    param_cfg = dict(l3acl_conf_list = l3acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_L3_ACLs_Delete_Rule'
    common_name = '[L3 ACL] Delete L3 ACL Rule and verify the Rule is deleted'
        #common_name = '[L3 ACL "%s"] Delete L3 ACL Rule and verify the Rule is deleted' % acl_policy['policy']
    param_cfg = dict(l3acl_conf_list = l3acl_conf_list)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))


    #test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    #common_name = 'Quit browser in Station'
    #test_cfgs.append(({'sta_tag': "sta1",
    #                   'browser_tag': "browser1"}, test_name, common_name, 0, False))

    #test_name = 'CB_ZD_Remove_All_Wlans'
    #common_name = 'Remove all WLAN from ZD'
    #test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_L3_ACLs'
    common_name = 'Clean all ACLs from ZD WebUI'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))

    return test_cfgs


def gen_acl_policy(acl_policy):
    '''
    '''
    return [{
        'acl_name': utils.make_random_string(random.randint(2, 32), type = 'alnum'),
        'description': utils.make_random_string(random.randint(2, 32), type = 'alnum'),
        'rule_conf_list': acl_policy['rule_conf_list'],
        'policy': acl_policy['policy'],
    }]


def gen_rule_conf_list():
    rule_policy_list = [
        dict(
            policy = 'allow',
            rule_conf_list = [
                dict(
                    rule_order = 3,
                    rule_description = "icmp_deny",
                    rule_type = 'deny',
                    rule_destination_addr = "192.168.0.0/24",
                    rule_destination_port = 'Any',
                    rule_protocol = 1,
                ),
                dict(
                    rule_order = 4,
                    rule_description = "http_allow",
                    rule_type = 'allow',
                    rule_destination_addr = "172.16.10.0/24",
                    rule_destination_port = 80,
                    rule_protocol = 6,
                )
            ],
        ),
        dict(
            policy = 'deny',
            rule_conf_list = [
                dict(
                    rule_order = 3,
                    rule_description = "icmp_allow",
                    rule_type = 'allow',
                    rule_destination_addr = "192.168.0.0/24",
                    rule_destination_port = 'Any',
                    rule_protocol = 1,
                ),
                dict(
                    rule_order = 4,
                    rule_description = "http_allow",
                    rule_type = 'allow',
                    rule_destination_addr = "172.16.10.0/24",
                    rule_destination_port = 80,
                    rule_protocol = 6,
                ),
            ],
        ),
    ]

    return rule_policy_list


def create_test_suite(**kwargs):
    '''
    '''
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

    ts_name = 'Config L3 ACL via CLI and Verify via GUI'
    ts = testsuite.get_testsuite(ts_name, 'L3 ACL CLI Configuration', combotest = True)

    fcfg = {
        'target_station': target_sta,
        'ras_ip_addr': ras_ip_addr,
        'acl_policy_list': gen_rule_conf_list(),
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

