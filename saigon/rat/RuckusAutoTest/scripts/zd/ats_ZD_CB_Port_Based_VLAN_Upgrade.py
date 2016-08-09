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
        'ap_mgmt_vlan': "4069",
        'image_file_path_list': [],
        'base_build_file_path': "",
        'force_upgrade': True,
    }
    fcfg.update(cfg)

    ap_tag = fcfg['ap_tag']
    ap_mgmt_vlan = fcfg['ap_mgmt_vlan']

    image_file_path_list = fcfg.get('image_file_path_list')
    if not image_file_path_list:
        image_file_path_list = [
            r"\\172.18.35.42\training\image\ZD3K\ZD3000_9.3.0.0.47.tar.gz",
            r"\\172.18.35.42\training\image\ZD3K\ZD3000_9.3.0.0.47.tar.gz",
        ]

    base_build_file_path = fcfg.get('base_build_file_path')
    if not base_build_file_path:
        base_build_file_path = r"\\172.18.35.42\training\image\ZD3K\ZD3000_9.2.0.0.138.tar.gz"

    port_settings = {
        'lan1_enabled': True,
        'lan1_type': "general",
        'lan1_untagged_vlan': "50",
        'lan1_vlan_members': "10-20",
        'lan2_enabled': True,
        'lan2_type': "trunk",
        'lan2_untagged_vlan': "1",
        'lan2_vlan_members': "",
    }

    expected_info = {
        'override_parent': True,
        'lan1': {'type': u'general', 'dot1x': u'disabled', 'enabled': True, 'untagged_vlan': u'50', 'vlan_members': u'10-20'},
        'lan2': {'type': u'trunk', 'dot1x': u'disabled', 'enabled': True, 'untagged_vlan': u'1', 'vlan_members': u'1-4094'},
    }

    name = "upgrade and downgrade"
    test_cfgs = []
    test_name = "CB_ZD_Remove_All_Config"
    common_name = "Remove all configuration from ZD"
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = "CB_ZD_Create_Active_AP"
    common_name = "Create active AP"
    test_cfgs.append(({'active_ap': fcfg['active_ap'],
                       'ap_tag': ap_tag,
                       }, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Backup AP Mgmt VLAN current settings"
    test_cfgs.append(({'cfg_type': "init"}, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Port_Override"
    common_name = "Config AP LAN ports to Trunk, Untag VLAN 1"
    test_cfgs.append(({'ap_tag': ap_tag,
                       'cfg_type': "init",
                       }, test_name, common_name, 0, False))


    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "[%s] Config AP Mgmt VLAN to %s" % (name, ap_mgmt_vlan)
    test_cfgs.append(({'mgmt_vlan': {'mode': "enable", 'vlan_id': ap_mgmt_vlan, },
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

    idx = 0
    for image_file_path in image_file_path_list:
        idx += 1
        test_name = 'CB_ZD_Upgrade'
        common_name = "[%s] Perform ZD Upgrade %s" % (name, idx)
        test_cfgs.append(({'image_file_path': image_file_path,
                           'force_upgrade': fcfg['force_upgrade']},
                          test_name, common_name, 1, False))

        test_name = "CB_ZD_Verify_AP_Port_Override"
        common_name = "[%s] Verify AP Port settings after upgrade %s" % (name, idx)
        test_cfgs.append(({'ap_tag': ap_tag,
                           'expected_info': expected_info,
                           }, test_name, common_name, 1, False))

        test_name = 'CB_ZD_Upgrade'
        common_name = "[%s] Restore to ZD base build %s" % (name, idx)
        test_cfgs.append(({'image_file_path': base_build_file_path,
                           'force_upgrade': fcfg['force_upgrade']},
                          test_name, common_name, 1, False))


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

    linux1_test_eth = raw_input("LinuxPC1 (connected to AP port) test interface: ").split()[0]
    linux2_test_eth = raw_input("LinuxPC2 (connected to the Switch) test interface: ").split()[0]

    base_build_file_path = raw_input("Current/base build file path: ").split()[0]
    image_file_path_list = raw_input("File path list of builds to up/downgrade: ").split()

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
        'image_file_path_list': image_file_path_list,
        'base_build_file_path': base_build_file_path,
    }

    test_cfgs = define_test_cfg(fcfg)

    ts_name = "%s - upgrade" % base_ts
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

