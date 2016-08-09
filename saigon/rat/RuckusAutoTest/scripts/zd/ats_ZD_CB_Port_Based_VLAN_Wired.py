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


def define_neg_port_config():
    '''
    '''
    neg_port_settings = [
        {'lan1_enabled': True,
         'lan1_type': "general",
         'lan1_vlan_members': "0",
        },
        {'lan1_enabled': True,
         'lan1_type': "general",
         'lan1_vlan_members': "0-1",
         },
        {'lan1_enabled': True,
         'lan1_type': "general",
         'lan1_vlan_members': "4095",
         },
        {'lan1_enabled': True,
         'lan1_type': "general",
         'lan1_vlan_members': "4094-4095",
         },
        {'lan1_enabled': True,
         'lan1_type': "general",
         'lan1_untagged_vlan': "4095",
         'lan1_vlan_members': "1-4094",
         },
    ]

    return neg_port_settings


def define_testcase_cfg_list():
    '''
    '''
    testcase_cfg_list = []
    testcase_cfg_list.append({
        'suite': 'configuration',
        'common': {
            'name': "Trunk1_Access4069",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "trunk",
                'lan2_enabled': True,
                'lan2_type': "access",
                'lan2_untagged_vlan': "4069",
                'lan2_vlan_members': "",
            },
        },
    })
    testcase_cfg_list.append({
        'suite': 'configuration',
        'common': {
            'name': "Trunk1_Trunk4069",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "trunk",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "4069",
                'lan2_vlan_members': "",
            },
        },
    })
    testcase_cfg_list.append({
        'suite': 'configuration',
        'common': {
            'name': "Trunk1_General4069,3072-4094",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "trunk",
                'lan2_enabled': True,
                'lan2_type': "general",
                'lan2_untagged_vlan': "4069",
                'lan2_vlan_members': "3072-4094",
            },
        },
    })

    testcase_cfg_list.append({
        'suite': 'access',
        'common': {
            'name': "Access20_Trunk20",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "access",
                'lan1_untagged_vlan': "20",
                'lan1_vlan_members': "",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "20",
                'lan2_vlan_members': "",
            },
        },
        'case1': {
            'name': "wo.tag_wo.tag",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.102",
                },
            },
            'ping': "allowed",
        },
        'case2': {
            'name': "wo.tag_tag20",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "20",
                    'ip_addr': "192.168.20.202",
                },
            },
            'ping': "disallowed",
        },
        'case3': {
            'name': "wo.tag_tag50",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.102",
                },
            },
            'ping': "disallowed",
        },
    })

    testcase_cfg_list.append({
        'suite': 'access',
        'common': {
            'name': "Access20_Trunk10",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "access",
                'lan1_untagged_vlan': "20",
                'lan1_vlan_members': "",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "10",
                'lan2_vlan_members': "",
            },
        },
        'case1': {
            'name': "wo.tag_wo.tag",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.10.102",
                },
            },
            'ping': "disallowed",
        },
        'case2': {
            'name': "wo.tag_tag20",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "20",
                    'ip_addr': "192.168.20.202",
                },
            },
            'ping': "allowed",
        },
        'case3': {
            'name': "wo.tag_tag50",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.102",
                },
            },
            'ping': "disallowed",
        },
    })

    testcase_cfg_list.append({
        'suite': 'access',
        'common': {
            'name': "Access20_TrunkNONE",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "access",
                'lan1_untagged_vlan': "20",
                'lan1_vlan_members': "",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "none",
                'lan2_vlan_members': "",
            },
        },
        'case1': {
            'name': "wo.tag_wo.tag",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.102",
                },
            },
            'ping': "disallowed",
        },
        'case2': {
            'name': "wo.tag_tag20",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "20",
                    'ip_addr': "192.168.20.202",
                },
            },
            'ping': "disallowed",
        },
        'case3': {
            'name': "wo.tag_tag50",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "192.168.20.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.102",
                },
            },
            'ping': "disallowed",
        },
    })

    testcase_cfg_list.append({
        'suite': 'general1',
        'common': {
            'name': "General50,10-20_Trunk50",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "general",
                'lan1_untagged_vlan': "50",
                'lan1_vlan_members': "10-20",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "50",
                'lan2_vlan_members': "",
            },
        },
        'case1': {
            'name': "wo.tag_wo.tag",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "172.16.10.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "172.16.10.102",
                },
            },
            'ping': "allowed",
        },
        'case2': {
            'name': "tag50_tag50",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.201",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.202",
                },
            },
            'ping': "disallowed",
        },
        'case3': {
            'name': "tag10_tag10",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.102",
                },
            },
            'ping': "allowed",
        },
        'case4': {
            'name': "tag512_tag512",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "512",
                    'ip_addr': "192.168.12.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "512",
                    'ip_addr': "192.168.12.102",
                },
            },
            'ping': "disallowed",
        },
    })

    testcase_cfg_list.append({
        'suite': 'general1',
        'common': {
            'name': "General50,10-20_Trunk512",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "general",
                'lan1_untagged_vlan': "50",
                'lan1_vlan_members': "10-20",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "512",
                'lan2_vlan_members': "",
            },
        },
        'case1': {
            'name': "wo.tag_wo.tag",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "172.16.10.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "172.16.10.102",
                },
            },
            'ping': "disallowed",
        },
        'case2': {
            'name': "tag50_tag50",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.201",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.202",
                },
            },
            'ping': "disallowed",
        },
        'case3': {
            'name': "tag10_tag10",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.102",
                },
            },
            'ping': "allowed",
        },
        'case4': {
            'name': "tag2048_tag2048",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "2048",
                    'ip_addr': "192.168.48.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "2048",
                    'ip_addr': "192.168.48.102",
                },
            },
            'ping': "disallowed",
        },
    })

    testcase_cfg_list.append({
        'suite': 'general2',
        'common': {
            'name': "GeneralNONE,10-20_Trunk50",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "general",
                'lan1_untagged_vlan': "none",
                'lan1_vlan_members': "10-20",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "50",
                'lan2_vlan_members': "",
            },
        },
        'case2': {
            'name': "tag50_tag50",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.201",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.202",
                },
            },
            'ping': "disallowed",
        },
        'case3': {
            'name': "tag10_tag10",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.102",
                },
            },
            'ping': "allowed",
        },
        'case4': {
            'name': "tag512_tag512",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "512",
                    'ip_addr': "192.168.12.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "512",
                    'ip_addr': "192.168.12.102",
                },
            },
            'ping': "disallowed",
        },
    })

    testcase_cfg_list.append({
        'suite': 'general2',
        'common': {
            'name': "General50,10-20_TrunkNONE",
            'port_settings': {
                'lan1_enabled': True,
                'lan1_type': "general",
                'lan1_untagged_vlan': "50",
                'lan1_vlan_members': "10-20",
                'lan2_enabled': True,
                'lan2_type': "trunk",
                'lan2_untagged_vlan': "none",
                'lan2_vlan_members': "",
            },
        },
        'case1': {
            'name': "wo.tag_wo.tag",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "172.16.10.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "",
                    'ip_addr': "172.16.10.102",
                },
            },
            'ping': "disallowed",
        },
        'case2': {
            'name': "tag50_tag50",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.201",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "50",
                    'ip_addr': "172.16.10.202",
                },
            },
            'ping': "disallowed",
        },
        'case3': {
            'name': "tag10_tag10",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "10",
                    'ip_addr': "192.168.10.102",
                },
            },
            'ping': "allowed",
        },
        'case4': {
            'name': "tag512_tag512",
            'linux_pc1': {
                'test_intf': {
                    'vlan': "512",
                    'ip_addr': "192.168.12.101",
                },
            },
            'linux_pc2': {
                'test_intf': {
                    'vlan': "512",
                    'ip_addr': "192.168.12.102",
                },
            },
            'ping': "disallowed",
        },
    })


    return testcase_cfg_list


def define_test_cfg(cfg, suite = ""):
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
    }
    fcfg.update(cfg)


    test_cfgs = []

    ap_tag = fcfg['ap_tag']
    ap_mgmt_vlan = fcfg['ap_mgmt_vlan']


    testcase_cfg_list = define_testcase_cfg_list()

    # Negative port settings
    neg_port_settings = define_neg_port_config()

    test_name = "CB_ZD_Remove_All_Config"
    common_name = "Remove all configuration from ZD"
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = "CB_ZD_Create_Active_AP"
    common_name = "Create active AP"
    test_cfgs.append(({'active_ap': fcfg['active_ap'],
                       'ap_tag': ap_tag,
                       }, test_name, common_name, 0, False))

# Comment out the following 2 steps because LinuxPC object has been created when testbed is up,
# no need to create it again, or error will happen.
#    test_name = "CB_StationLinuxPC_Create_Station"
#    common_name = "Create station %s" % fcfg['linux_pc1']['sta_tag']
#    test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
#                       'sta_ip_addr': fcfg['linux_pc1']['ip_addr'],
#                       }, test_name, common_name, 0, False))
#
#    test_name = "CB_StationLinuxPC_Create_Station"
#    common_name = "Create station %s" % fcfg['linux_pc2']['sta_tag']
#    test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
#                       'sta_ip_addr': fcfg['linux_pc2']['ip_addr'],
#                       }, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Backup AP Mgmt VLAN current settings"
    test_cfgs.append(({'cfg_type': "init"}, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Config AP Mgmt VLAN to %s" % ap_mgmt_vlan
    test_cfgs.append(({'mgmt_vlan': {'mode': "enable", 'vlan_id': ap_mgmt_vlan, },
                       'cfg_type': "config",
                       }, test_name, common_name, 0, False))

    test_name = "CB_ZD_Verify_AP_Brief_Info"
    common_name = "Verify AP is managed at Mgmt VLAN %s" % ap_mgmt_vlan
    test_cfgs.append(({'ap_tag': ap_tag,
                       'expected_info': {'mgmt_vlan': ap_mgmt_vlan, 'state': "Connected", },
                       'check_status_timeout': 300,
                       'break_time': 30,
                       }, test_name, common_name, 0, False))

    test_name = "CB_ZD_Config_AP_Port_Override"
    common_name = "Config AP LAN ports to Trunk, Untag VLAN 1"
    test_cfgs.append(({'ap_tag': ap_tag,
                       'cfg_type': "init",
                       }, test_name, common_name, 0, False))

    if suite == "configuration":
        idx = 0
        for port_settings in neg_port_settings:
            idx += 1
            test_name = "CB_ZD_Config_AP_Port_Override"
            common_name = "[VLAN range] Config AP LAN ports - negative #%s" % idx
            test_cfgs.append(({'ap_tag': ap_tag,
                               'port_settings': port_settings,
                               'is_negative': True,
                               }, test_name, common_name, 1, False))

    for testcase_cfg in testcase_cfg_list:
        if suite != testcase_cfg.get('suite'):
            continue

        name = testcase_cfg['common']['name']
        port_settings = testcase_cfg['common']['port_settings']

        test_name = "CB_ZD_Config_AP_Port_Override"
        common_name = "Config AP LAN ports to %s" % name
        test_cfgs.append(({'ap_tag': ap_tag, 'port_settings': port_settings,
                           }, test_name, common_name, 0, False))

        if suite == "configuration":
            if port_settings['lan2_untagged_vlan'] == str(ap_mgmt_vlan):
                tagging = "without tag"

            else:
                tagging = "with tag %s " % ap_mgmt_vlan

            test_name = "CB_ZD_Verify_AP_Brief_Info"
            common_name = "[%s] Verify AP is managed at Mgmt VLAN %s %s" % \
                          (name, ap_mgmt_vlan, tagging)
            test_cfgs.append(({'ap_tag': ap_tag,
                               'expected_info': {'mgmt_vlan': ap_mgmt_vlan, 'state': "Connected", },
                               'check_status_timeout': 300,
                               'break_time': 30,
                               }, test_name, common_name, 1, False))

        for case, case_cfg in testcase_cfg.iteritems():
            if case in ['common', 'suite']:
                continue

            l2name = "%s %s" % (name, case_cfg['name'])

            test_name = "CB_StationLinuxPC_Config_Interface"
            common_name = "[%s] Cleanup %s interface" % (
                l2name, fcfg['linux_pc1']['sta_tag']
            )
            test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                               'is_cleanup': True,
                               'interface': fcfg['linux_pc1']['test_intf']['eth'],
                               'ip_addr': '192.17.111.1'
                               }, test_name, common_name, 1, False))

            test_name = "CB_StationLinuxPC_Config_Interface"
            common_name = "[%s] Cleanup %s interface" % (
                l2name, fcfg['linux_pc2']['sta_tag']
            )

            test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
                               'is_cleanup': True,
                               'interface': fcfg['linux_pc2']['test_intf']['eth'],
                               'ip_addr': '192.17.111.2'
                               }, test_name, common_name, 1, False))

            if_name = fcfg['linux_pc1']['test_intf']['eth']
            if case_cfg['linux_pc1']['test_intf']['vlan']:
                if_name += ".%s" % case_cfg['linux_pc1']['test_intf']['vlan']

            test_name = "CB_StationLinuxPC_Config_Interface"
            common_name = "[%s] Config %s interface %s, IP %s" % (
                l2name, fcfg['linux_pc1']['sta_tag'],
                if_name, case_cfg['linux_pc1']['test_intf']['ip_addr']
            )
            test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                               'interface': fcfg['linux_pc1']['test_intf']['eth'],
                               'ip_addr': case_cfg['linux_pc1']['test_intf']['ip_addr'],
                               'vlan_id': case_cfg['linux_pc1']['test_intf']['vlan'],
                               }, test_name, common_name, 1, False))


            if_name = fcfg['linux_pc2']['test_intf']['eth']
            if case_cfg['linux_pc2']['test_intf']['vlan']:
                if_name += ".%s" % case_cfg['linux_pc2']['test_intf']['vlan']

            test_name = "CB_StationLinuxPC_Config_Interface"
            common_name = "[%s] Config %s interface %s, IP %s" % (
                l2name, fcfg['linux_pc2']['sta_tag'],
                if_name, case_cfg['linux_pc2']['test_intf']['ip_addr']
            )
            test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
                               'interface': fcfg['linux_pc2']['test_intf']['eth'],
                               'ip_addr': case_cfg['linux_pc2']['test_intf']['ip_addr'],
                               'vlan_id': case_cfg['linux_pc2']['test_intf']['vlan'],
                               }, test_name, common_name, 1, False))


            if_name = fcfg['linux_pc1']['test_intf']['eth']
            if case_cfg['linux_pc1']['test_intf']['vlan']:
                if_name += ".%s" % case_cfg['linux_pc1']['test_intf']['vlan']

            test_name = "CB_StationLinuxPC_Ping_Dest"
            common_name = "[%s] Verify Ping from %s interface %s to dest IP %s" % (
                l2name, fcfg['linux_pc1']['sta_tag'],
                if_name, case_cfg['linux_pc2']['test_intf']['ip_addr']
            )
            test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                               'sta_eth': if_name,
                               'condition': case_cfg['ping'],
                               'ping_timeout_ms': 6 * 1000,
                               'target': case_cfg['linux_pc2']['test_intf']['ip_addr'],
                               }, test_name, common_name, 2, False))


    test_name = "CB_ZD_Config_AP_Port_Override"
    common_name = "Unoverride AP LAN ports"
    test_cfgs.append(({'ap_tag': ap_tag,
                       'cfg_type': "teardown",
                       }, test_name, common_name, 0, True))

    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Restore AP Mgmt VLAN settings"
    test_cfgs.append(({'cfg_type': "teardown"}, test_name, common_name, 0, True))

    test_name = "CB_ZD_Verify_AP_Brief_Info"
    common_name = "Verify AP is managed after Mgmt VLAN is restored"
    test_cfgs.append(({'ap_tag': ap_tag,
                       'expected_info': {'state': "Connected", },
                       'check_status_timeout': 300,
                       'break_time': 30,
                       }, test_name, common_name, 0, True))

    test_name = "CB_StationLinuxPC_Config_Interface"
    common_name = "Cleanup %s interface" % (fcfg['linux_pc1']['sta_tag'])
    test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
                       'is_cleanup': True,
                       'interface': fcfg['linux_pc1']['test_intf']['eth'],
                       'ip_addr': '192.17.111.1'
                       }, test_name, common_name, 0, True))

    test_name = "CB_StationLinuxPC_Config_Interface"
    common_name = "Cleanup %s interface" % (fcfg['linux_pc2']['sta_tag'])
    test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
                       'is_cleanup': True,
                       'interface': fcfg['linux_pc2']['test_intf']['eth'],
                       'ip_addr': '192.17.111.2'
                       }, test_name, common_name, 0, True))


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
                       }, test_name, common_name, 0, True))

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
                       }, test_name, common_name, 0, True))

# Comment out the following 2 steps because the next suite cannot run and error will happen after
# closeing the connection with LinuxPC.
#    test_name = "CB_StationLinuxPC_Close_Station"
#    common_name = "Close station %s" % fcfg['linux_pc1']['sta_tag']
#    test_cfgs.append(({'sta_tag': fcfg['linux_pc1']['sta_tag'],
#                       }, test_name, common_name, 0, False))
#
#    test_name = "CB_StationLinuxPC_Close_Station"
#    common_name = "Close station %s" % fcfg['linux_pc2']['sta_tag']
#    test_cfgs.append(({'sta_tag': fcfg['linux_pc2']['sta_tag'],
#                       }, test_name, common_name, 0, False))

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

    cfg_list = define_testcase_cfg_list()
    suite_list = []
    for item in cfg_list:
        suite = item.get("suite")
        if suite and not suite in suite_list:
            suite_list.append(suite)

    for suite in suite_list:
        ts_name = "%s - %s" % (base_ts, suite)
        ts = testsuite.get_testsuite(ts_name, "Port Base VLAN - configuration", combotest = True)

        test_cfgs = define_test_cfg(fcfg, suite)

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

