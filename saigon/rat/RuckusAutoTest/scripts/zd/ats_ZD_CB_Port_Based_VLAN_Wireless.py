'''
INSTRUCTIONS for the following addtestsuite scripts:
- ats_ZD_CB_Port_Based_VLAN_Wired.py
- ats_ZD_CB_Port_Based_VLAN_Wireless.py
- ats_ZD_CB_Port_Based_VLAN_Upgrade.py

Besides the common known arguments (such as testbed name, active ap), you need to provide the following in this ats script:
- Based test suite name: the prefix of the generated test suite name, and it is the first element in this format: "%s - %s". For example, if you provide port-based-vlan, the suites will be:
  + port-based-vlan - configuration
  + port-based-vlan - access
  + ...
- The test interfaces of the two LinuxPC stations: LinuxPC1 is connected to an AP port. LinuxPC2 is connected to the ZD via the Switch.
  Warning: providing wrong interfaces require you to re-config the LinuxPC stations manually.
- Current/base build file path: the image path of the current build in the ZD. This is the starting point build where the test begins. Also, in the upgrade/downgrade procedure, we need to restore to the previous build before the up/downgrade.
- File path list of builds to up/downgrade: the list of builds to upgrade/downgrade. Each file path is separated by a space. You can provide one or many builds. The test will perform one by one, and after up/downgrading one build, it will restore to the current build before doing the next build in your list. For example, the base build is 9.2.0.0.138, and the list of builds is [9.1.0.0.38, 9.3.0.0.47]. The test first will downgrade to 9.1.0.0.38, then upgrade to 9.2.0.0.138, then upgrade to 9.3.0.0.47, then finally downgrade to 9.2.0.0.138.
  Warning: be aware of the configuration lost when providing the incompatible images.
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_testcase_cfg_list():
    '''
    '''
    testcase_cfg_list = []
    testcase_cfg_list.append({
        'name': "wireless to trunk with untag id",
        'ap_mgmt_vlan': "1",
        'wlan_cfg': {
            'ssid': "rat-wlan-port-based-vlan",
            'auth': "open",
            'encryption': "none",
            'do_tunnel': False,
            'vlan_id': 20,
        },
        'port_settings': {
            'lan1_enabled': True,
            'lan1_type': "trunk",
            'lan1_untagged_vlan': "20",
            'lan1_vlan_members': "",
        },
        'linux_pc1': {
            'test_intf': {
                'vlan': "",
                'ip_addr': "192.168.20.101",
            },
        },
        'ping': "allowed",
    })

    testcase_cfg_list.append({
        'name': "wireless to trunk without untag id",
        'ap_mgmt_vlan': "1",
        'wlan_cfg': {
            'ssid': "rat-wlan-port-based-vlan",
            'auth': "open",
            'encryption': "none",
            'do_tunnel': False,
            'vlan_id': 20,
        },
        'port_settings': {
            'lan1_enabled': True,
            'lan1_type': "trunk",
            'lan1_untagged_vlan': "none",
            'lan1_vlan_members': "",
        },
        'linux_pc1': {
            'test_intf': {
                'vlan': "20",
                'ip_addr': "192.168.20.101",
            },
        },
        'ping': "allowed",
    })

    testcase_cfg_list.append({
        'name': "wlan with tunnel over trunk port",
        'ap_mgmt_vlan': "10",
        'wlan_cfg': {
            'ssid': "rat-wlan-port-based-vlan",
            'auth': "open",
            'encryption': "none",
            'do_tunnel': True,
            'vlan_id': 20,
        },
        'port_settings': {
            'lan1_enabled': True,
            'lan1_type': "trunk",
            'lan1_untagged_vlan': "1",
            'lan1_vlan_members': "",
            'lan2_enabled': True,
            'lan2_type': "trunk",
            'lan2_untagged_vlan': "none",
            'lan2_vlan_members': "",
        },
        'linux_pc2': {
            'test_intf': {
                'vlan': "20",
                'ip_addr': "192.168.20.102",
            },
        },
        'ping': "allowed",
    })

    testcase_cfg_list.append({
        'name': "wlan with tunnel over general port",
        'ap_mgmt_vlan': "10",
        'wlan_cfg': {
            'ssid': "rat-wlan-port-based-vlan",
            'auth': "open",
            'encryption': "none",
            'do_tunnel': True,
            'vlan_id': 20,
        },
        'port_settings': {
            'lan1_enabled': True,
            'lan1_type': "trunk",
            'lan1_untagged_vlan': "1",
            'lan1_vlan_members': "",
            'lan2_enabled': True,
            'lan2_type': "general",
            'lan2_untagged_vlan': "1",
            'lan2_vlan_members': "1-20",
        },
        'linux_pc2': {
            'test_intf': {
                'vlan': "20",
                'ip_addr': "192.168.20.102",
            },
        },
        'ping': "allowed",
    })

    return testcase_cfg_list


def define_test_cfg(cfg):
    fcfg = {
        'ap_tag': "AP1",
        'sta_tag': "STA1",
        'linux_pc1': {
            'sta_tag': "LinuxPC1",
            'ip_addr': "192.168.1.101", # Control IP Address
            'test_intf': {
                'eth': "eth0", # Interface under test
                'vlan': "", # VLAN to add to the interface
                'ip_addr': "192.168.0.101", # Default IP Address for PVID
            },
        },
        'linux_pc2': {
            'sta_tag': "LinuxPC2",
            'ip_addr': "192.168.1.102", # Control IP Address
            'test_intf': {
                'eth': "eth1", # Interface under test
                'vlan': "", # VLAN to add to the interface
                'ip_addr': "192.168.0.102", # Default IP Address for PVID
            },
        },
    }
    fcfg.update(cfg)

    test_cfgs = []
    ap_tag = fcfg['ap_tag']
    testcase_cfg_list = define_testcase_cfg_list()

    test_name = "CB_ZD_Remove_All_Config"
    common_name = "Remove all configuration from ZD"
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = "CB_ZD_Create_Active_AP"
    common_name = "Create active AP"
    test_cfgs.append(({'active_ap': fcfg['active_ap'],
                       'ap_tag': ap_tag,
                       }, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr': cfg['target_station'],
                       'sta_tag': fcfg['sta_tag'],
                       }, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': fcfg['sta_tag'],
                       }, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Backup AP Mgmt VLAN current settings"
    test_cfgs.append(({'cfg_type': "init"}, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Port_Override"
    common_name = "Config AP LAN ports to Trunk, Untag VLAN 1"
    test_cfgs.append(({'ap_tag': ap_tag,
                       'cfg_type': "init",
                       }, test_name, common_name, 0, False))

    for testcase_cfg in testcase_cfg_list:
        name = testcase_cfg['name']
        port_settings = testcase_cfg['port_settings']
        ap_mgmt_vlan = testcase_cfg['ap_mgmt_vlan']
        wlan_config = testcase_cfg['wlan_cfg']
        linux_pc1 = testcase_cfg.get('linux_pc1')
        linux_pc2 = testcase_cfg.get('linux_pc2')

        mgmt_vlan_mode = "enable"
        if ap_mgmt_vlan == "1":
            mgmt_vlan_mode = "disable"

        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "[%s] Config AP Mgmt VLAN to %s" % (name, ap_mgmt_vlan)
        test_cfgs.append(({'mgmt_vlan': {'mode': mgmt_vlan_mode, 'vlan_id': ap_mgmt_vlan, },
                           'cfg_type': "config",
                           }, test_name, common_name, 0, False))

        test_name = "CB_ZD_Verify_AP_Brief_Info"
        common_name = "[%s] Verify AP is managed at Mgmt VLAN %s" % (name, ap_mgmt_vlan)
        test_cfgs.append(({'ap_tag': ap_tag,
                           'expected_info': {'mgmt_vlan': ap_mgmt_vlan, 'state': "Connected", },
                           'check_status_timeout': 300,
                           'break_time': 30,
                           }, test_name, common_name, 0, False))

        test_name = "CB_ZD_Config_AP_Port_Override"
        common_name = "[%s] Config AP LAN ports" % name
        test_cfgs.append(({'ap_tag': ap_tag, 'port_settings': port_settings,
                           }, test_name, common_name, 1, False))

        tagging = "with tag %s " % ap_mgmt_vlan
        if port_settings.get('lan2_untagged_vlan') == str(ap_mgmt_vlan) or \
        str(ap_mgmt_vlan) == "1":
            tagging = "without tag"

        test_name = "CB_ZD_Verify_AP_Brief_Info"
        common_name = "[%s] Verify AP is managed at Mgmt VLAN %s %s" % (name, ap_mgmt_vlan, tagging)
        test_cfgs.append(({'ap_tag': ap_tag,
                           'expected_info': {'mgmt_vlan': ap_mgmt_vlan, 'state': "Connected", },
                           'check_status_timeout': 300,
                           'break_time': 30,
                           }, test_name, common_name, 1, False))

        test_name = 'CB_ZD_Create_Wlan'
        common_name = '[%s] Create a wlan on ZD' % (name,)
        test_cfgs.append(({'wlan_cfg_list': [wlan_config],
                           }, test_name, common_name, 1, False))

        test_name = "CB_StationLinuxPC_Config_Interface"
        common_name = "[%s] Cleanup %s interface" % (
            name, fcfg['linux_pc1']['sta_tag']
        )
        test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                           'is_cleanup': True,
                           'interface': fcfg['linux_pc1']['test_intf']['eth'],
                           'ip_addr': '192.17.111.1'
                           }, test_name, common_name, 1, False))

        test_name = "CB_StationLinuxPC_Config_Interface"
        common_name = "[%s] Cleanup %s interface" % (
            name, fcfg['linux_pc2']['sta_tag']
        )

        test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
                           'is_cleanup': True,
                           'interface': fcfg['linux_pc2']['test_intf']['eth'],
                           'ip_addr': '192.17.111.2'
                           }, test_name, common_name, 1, False))

        if linux_pc1:
            if_name = fcfg['linux_pc1']['test_intf']['eth']
            if linux_pc1['test_intf']['vlan']:
                if_name += ".%s" % linux_pc1['test_intf']['vlan']

            test_name = "CB_StationLinuxPC_Config_Interface"
            common_name = "[%s] Config %s interface %s, IP %s" % (
                name, fcfg['linux_pc1']['sta_tag'],
                if_name, linux_pc1['test_intf']['ip_addr']
            )
            test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                               'interface': fcfg['linux_pc1']['test_intf']['eth'],
                               'ip_addr': linux_pc1['test_intf']['ip_addr'],
                               'vlan_id': linux_pc1['test_intf']['vlan'],
                               }, test_name, common_name, 1, False))

        if linux_pc2:
            if_name = fcfg['linux_pc2']['test_intf']['eth']
            if linux_pc2['test_intf']['vlan']:
                if_name += ".%s" % linux_pc2['test_intf']['vlan']

            test_name = "CB_StationLinuxPC_Config_Interface"
            common_name = "[%s] Config %s interface %s, IP %s" % (
                name, fcfg['linux_pc2']['sta_tag'],
                if_name, linux_pc2['test_intf']['ip_addr']
            )
            test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
                               'interface': fcfg['linux_pc2']['test_intf']['eth'],
                               'ip_addr': linux_pc2['test_intf']['ip_addr'],
                               'vlan_id': linux_pc2['test_intf']['vlan'],
                               }, test_name, common_name, 1, False))


        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '[%s] Associate the station to the wlan' % (name,)
        test_cfgs.append(({'wlan_cfg': wlan_config,
                           'sta_tag': fcfg['sta_tag'],
                           }, test_name, common_name, 1, False))

        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '[%s] Get wifi address of the station' % (name,)
        test_cfgs.append(({'sta_tag': fcfg['sta_tag'],
                           }, test_name, common_name, 2, False))

        dest_ip = ""
        if linux_pc1:
            dest_ip = linux_pc1['test_intf']['ip_addr']

        if linux_pc2:
            dest_ip = linux_pc2['test_intf']['ip_addr']

        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '[%s] Verify Ping from %s to Dest IP %s' % \
                      (name, fcfg['sta_tag'], dest_ip)
        test_cfgs.append(({'sta_tag': fcfg['sta_tag'],
                           'condition': testcase_cfg['ping'],
                           'target': dest_ip,
                           }, test_name, common_name, 1, False))


    #--------------------
    test_name = "CB_ZD_Config_AP_Port_Override"
    common_name = "Unoverride AP LAN ports"
    test_cfgs.append(({'ap_tag': ap_tag,
                       'cfg_type': "teardown",
                       }, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Restore AP Mgmt VLAN settings"
    test_cfgs.append(({'cfg_type': "teardown"}, test_name, common_name, 0, False))

    test_name = "CB_ZD_Verify_AP_Brief_Info"
    common_name = "Verify AP is managed after Mgmt VLAN is restored"
    test_cfgs.append(({'ap_tag': ap_tag,
                       'expected_info': {'state': "Connected", },
                       'check_status_timeout': 300,
                       'break_time': 30,
                       }, test_name, common_name, 0, False))

    test_name = "CB_StationLinuxPC_Config_Interface"
    common_name = "Cleanup %s interface" % (fcfg['linux_pc1']['sta_tag'])
    test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                       'is_cleanup': True,
                       'interface': fcfg['linux_pc1']['test_intf']['eth'],
                       'ip_addr': '192.17.111.1'
                       }, test_name, common_name, 0, False))

    test_name = "CB_StationLinuxPC_Config_Interface"
    common_name = "Cleanup %s interface" % (fcfg['linux_pc2']['sta_tag'])
    test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
                       'is_cleanup': True,
                       'interface': fcfg['linux_pc2']['test_intf']['eth'],
                       'ip_addr': '192.17.111.2'
                       }, test_name, common_name, 0, False))


    test_name = "CB_StationLinuxPC_Config_Interface"
    common_name = "Set default %s interface %s, IP %s" % (
        fcfg['linux_pc1']['sta_tag'],
        fcfg['linux_pc1']['test_intf']['eth'],
        fcfg['linux_pc1']['test_intf']['ip_addr']
    )
    test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                       'interface': fcfg['linux_pc1']['test_intf']['eth'],
                       'ip_addr': fcfg['linux_pc1']['test_intf']['ip_addr'],
                       'vlan_id': "",
                       }, test_name, common_name, 0, False))

    test_name = "CB_StationLinuxPC_Config_Interface"
    common_name = "Set default %s interface %s, IP %s" % (
        fcfg['linux_pc2']['sta_tag'],
        fcfg['linux_pc2']['test_intf']['eth'],
        fcfg['linux_pc2']['test_intf']['ip_addr']
    )
    test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
                       'interface': fcfg['linux_pc2']['test_intf']['eth'],
                       'ip_addr': fcfg['linux_pc2']['test_intf']['ip_addr'],
                       'vlan_id': "",
                       }, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove the wlan from station'
    test_cfgs.append(({'sta_tag': fcfg['sta_tag'],
                       }, test_name, common_name, 1, False))


    return test_cfgs


def create_test_suite(**kwargs):
    ts_cfg = dict(
        interactive_mode = True,
        testsuite_name = "",
    )

    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    active_ap = testsuite.getActiveAp(ap_sym_dict)[0]

    base_ts = "Port Based VLAN"
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        base_ts = raw_input("Based test suite name: ").split()[0]

    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]

    linux1_test_eth = raw_input("LinuxPC1 interface under test: ").split()[0]
    linux2_test_eth = raw_input("LinuxPC2 interface under test: ").split()[0]

    fcfg = {
        'target_station': target_sta,
        'active_ap': active_ap,
        'linux_pc1': {
            'sta_tag': "LinuxPC1",
            'ip_addr': "192.168.1.101", # Control IP Address
            'test_intf': {
                'eth': linux1_test_eth, # Interface under test
                'vlan': "", # VLAN to add to the interface
                'ip_addr': "192.168.0.101", # Default IP Address for PVID
            },
        },
        'linux_pc2': {
            'sta_tag': "LinuxPC2",
            'ip_addr': "192.168.1.102", # Control IP Address
            'test_intf': {
                'eth': linux2_test_eth, # Interface under test
                'vlan': "", # VLAN to add to the interface
                'ip_addr': "192.168.0.102", # Default IP Address for PVID
            },
        },
    }

    test_cfgs = define_test_cfg(fcfg)

    ts_name = "%s - wireless" % base_ts
    ts = testsuite.get_testsuite(ts_name, "Port Based VLAN configuration", combotest = True)

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

