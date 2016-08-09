'''

@author: serena.tan@ruckuswireless.com
'''


import sys
import time
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


def choose_active_ap(ap_sym_dict, input_prompt = ''):
    message = "Choose an active AP: "
    if input_prompt:
        message = input_prompt
        
    while True:
        active_ap = raw_input(message)
        if active_ap not in ap_sym_dict:
            print "AP[%s] doesn't exist." % active_ap
            
        else:
            return active_ap
        

def define_test_cfgs(tcfg):
    test_cfgs = []
    ap_tag = tcfg['active_ap']
    ap_mac = tcfg['active_ap_mac']
    sta_tag = tcfg['target_sta']
    radio_mode = tcfg['active_radio']
    wlan_cfg = tcfg['wlan_cfg']
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP: %s' % ap_tag
    test_params = {'ap_tag': ap_tag, 'active_ap': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create client: %s' % sta_tag
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = "Create WLAN: %s" % (wlan_cfg['ssid'])
    test_params = {'wlan_cfg_list': [wlan_cfg], 
                   'enable_wlan_on_default_wlan_group': False}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create WLAN group: %s" % (tcfg['wg_cfg']['name']) 
    test_cfgs.append(({'wgs_cfg': tcfg['wg_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the WLAN group to radio '%s' of AP: %s" % (radio_mode, ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = "Client '%s' associate WLAN: %s" % (sta_tag, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag, 
                   'wlan_cfg': wlan_cfg,
                   'remove_all_wlans': False,
                   'verify_ip_subnet': False,
                   'start_browser': False}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Start_Back_Ground_Traffic'
    common_name = "Start back ground traffic between client '%s' and linux server" % sta_tag
    test_params = {'sta_tag': sta_tag,
                   'zapd_sta': tcfg['target_ip']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    
    tcid = "[Capture packets in AP CLI - local]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': '',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - local-nob]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'nob',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - local-noc]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'noc',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - local-nop]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'nop',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - local-nobcp]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'nobcp',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - stream]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': '',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - stream-nob]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'nob',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - stream-noc]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'noc',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - stream-nop]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'nop',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in AP CLI - stream-nobcp]"
    test_name = 'CB_AP_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'nobcp',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - local]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': '',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - local-nob]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'nob',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - local-noc]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'noc',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - local-nop]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'nop',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - local-nobcp]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'nobcp',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - stream]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': '',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - stream-nob]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'nob',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - stream-noc]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'noc',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - stream-nop]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'nop',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD CLI - stream-nobcp]"
    test_name = 'CB_ZD_CLI_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_tag': ap_tag,
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'capture_filter': 'nobcp',
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD GUI - local]"
    test_name = 'CB_ZD_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_mac_list': [ap_mac],
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': '',
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD GUI - local-ip]"
    test_name = 'CB_ZD_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_mac_list': [ap_mac],
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'sta_wifi_ip',
                   'sta_tag': sta_tag,
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    

    tcid = "[Capture packets in ZD GUI - local-mac]"
    test_name = 'CB_ZD_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_mac_list': [ap_mac],
                   'radio_mode': radio_mode,
                   'capture_mode': 'local',
                   'capture_filter': 'sta_wifi_mac',
                   'sta_tag': sta_tag,
                   'capture_time': 30,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = "[Capture packets in ZD GUI - stream]"
    test_name = 'CB_ZD_Capture_Packets'
    common_name = "%sCapture and analyze packets in AP: %s" % (tcid, ap_tag)
    test_params = {'ap_mac_list': [ap_mac],
                   'radio_mode': radio_mode,
                   'capture_mode': 'stream',
                   'ap_tag': ap_tag,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Stop_Back_Ground_Traffic'
    common_name = "Stop back ground traffic between client '%s' and linux server" % sta_tag
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Capture_APs'
    common_name = 'Remove all capture APs to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_sta = '',
                 active_radio = '',
                 ts_name = "",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        active_ap = choose_active_ap(ap_sym_dict, "Choose an active AP: ")
            
        target_sta = testsuite.getTargetStation(sta_ip_list)
        active_radio = testsuite.get_target_sta_radio()
        
    else:
        active_ap = attrs["active_ap"]
        target_sta = attrs['target_sta']
        active_radio = attrs["active_radio"]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if active_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, active_radio)
        return

    active_ap_role = ''
    res = re.search('Connected \((.+)\)', ap_sym_dict[active_ap]['status'], re.I)
    if res:
        active_ap_role = ' - %s AP' % res.group(1).split(' ')[0]
    
    wlan_cfg = {
        'ssid': 'rat-cap-%s' % time.strftime("%H%M%S"), 
        'auth': "open",
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        }
    
    wg_cfg = {
        'name': 'rat_wg-cap-%s' % time.strftime("%H%M%S"),
        'description': 'WLAN group for packet capture',
        'vlan_override': False,
        'wlan_member': {wlan_cfg['ssid']: {}},
        }
    
    tcfg = dict(active_ap = active_ap,
                active_ap_mac = ap_sym_dict[active_ap]['mac'],
                active_radio = active_radio,
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                wg_cfg = wg_cfg,
                target_ip = '192.168.0.252',
                )
    test_cfgs = define_test_cfgs(tcfg)

    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    elif active_ap_role:
        ts_name = "Mesh - Capture Packets - %s%s - %s" \
                  % (active_ap_model, active_ap_role, active_radio)
    
    else:
        ts_name = "Capture Packets - %s - %s" % (active_ap_model, active_radio)
                  
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the capture packets functionality.",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest = True)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test cases with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
    
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    