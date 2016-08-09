'''
For WLAN sanity checking before/after Upgrade, 
must make sure all of WLANs works very well. 
'''
import sys
import random
import time
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

BUILD_STREAM = 'ZD3000_9.5.0.0_production'
BUILD_NUMBER  = '143'


def define_Wlan_cfg(ras_server_name):
    wlan_cfgs = []
    wlan_cfgs.append(dict(ssid = "open-none-%s" % (time.strftime("%H%M%S")), 
                          auth = "open", wpa_ver = "", encryption = "none",
                          key_index = "" , key_string = "",
                          username = "", password = "", auth_svr = "",
                          tcid = "[Open_None]"))

    wlan_cfgs.append(dict(ssid = "wep-64-%s" % (time.strftime("%H%M%S")),
                          auth = "open", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[Open_WEP_64_key_1]"))

    wlan_cfgs.append(dict(ssid = "wep-128-%s" % (time.strftime("%H%M%S")),
                          auth = "open", wpa_ver = "", encryption = "WEP-128",
                          key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[Open_WEP_128_key_1]"))

    wlan_cfgs.append(dict(ssid = "shared-wep-64-%s" % (time.strftime("%H%M%S")), 
                          auth = "shared", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[Shared_WEP_64_key_1]"))

    wlan_cfgs.append(dict(ssid = "shared-wep-128-%s" % (time.strftime("%H%M%S")),
                          auth = "shared", wpa_ver = "", encryption = "WEP-128",
                          key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[Shared_WEP_128_key_1]"))

    wlan_cfgs.append(dict(ssid = "wpa-psk-tkip-%s" % (time.strftime("%H%M%S")),
                          auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , 
                          key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[WPA_PSK_TKIP]"))

    wlan_cfgs.append(dict(ssid = "wpa-psk-aes-%s" % (time.strftime("%H%M%S")),
                          auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , 
                          key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[WPA_PSK_AES]"))

    wlan_cfgs.append(dict(ssid = "wpa2-psk-tkip-%s" % (time.strftime("%H%M%S")),
                          auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , 
                          key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[WPA2_PSK_TKIP]"))

    wlan_cfgs.append(dict(ssid = "wpa2-psk-aes-%s" % (time.strftime("%H%M%S")),
                          auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , 
                          key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "",
                          tcid = "[WPA2_PSK_AES]"))

    wlan_cfgs.append(dict(ssid = "wpa-eap-tkip-%s" % (time.strftime("%H%M%S")),
                          auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", 
                          auth_svr = ras_server_name, tcid = "[EAP_WPA_TKIP_RADIUS]"))

    wlan_cfgs.append(dict(ssid = "wpa-eap-aes-%s" % (time.strftime("%H%M%S")),
                          auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", 
                          auth_svr = ras_server_name, tcid = "[EAP_WPA_AES_RADIUS]"))

    wlan_cfgs.append(dict(ssid = "wpa2-eap-tkip-%s" % (time.strftime("%H%M%S")),
                           auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", 
                          auth_svr = ras_server_name, tcid = "[EAP_WPA2_TKIP_RADIUS]"))

    wlan_cfgs.append(dict(ssid = "wpa2-eap-aes-%s" % (time.strftime("%H%M%S")),
                          auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", 
                          auth_svr = ras_server_name, tcid = "[EAP_WPA2_AES_RADIUS]"))

    return wlan_cfgs


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
        

def set_build():
    global BUILD_STREAM, BUILD_NUMBER
    while True:
        res = raw_input("Please input upgrade build stream: ["+BUILD_STREAM+"]")
        if not res:
            break
        else:
            BUILD_STREAM = res
            break
    
    while True:
        res = raw_input("Please input upgrade build number: ["+BUILD_NUMBER+"]")
        if not res:
            break
        else:
            BUILD_NUMBER = res
    
    print "Target build_stream %s, build_number %s" % (BUILD_STREAM, 
                                                       BUILD_NUMBER)
        
        
def decorate_common_name(test_cfgs):
    new_test_cfgs = []
    pre_tcid = ''
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        res = re.search("^\[(.*)\]", common_name)
        if res:
            tcid = res.group(1)
            if tcid != pre_tcid:
                pre_tcid = tcid
                counter = 1
            
            else:
                counter += 1
            
            common_name = common_name.replace("]", "] %s." % counter)
                              
        new_test_cfgs.append((test_params, testname, common_name, exc_level, is_cleanup))
    
    return new_test_cfgs


def remove_wlan_from_wg(tcid, wlan_cfg, wg_cfg, exe_level):
    test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
    common_name = "%sRemove WLAN '%s' from the WLAN group" % (tcid, wlan_cfg['ssid'])
    test_params = {'wgs_cfg': wg_cfg,
                   'wlan_list': [wlan_cfg['ssid']]}
    
    return (test_params, test_name, common_name, exe_level, False)


def test_encryption(cfg):
    conf = {
        'tcid': '',
        'wlan_cfg': {},
        'wg_cfg': {},
        'ap_tag': '',
        'sta_tag': '',
        'radio_mode': '',
        'target_ip': '192.168.0.252',        
        }
    conf.update(cfg)
    
    tcid = conf['tcid']
    wlan_cfg = conf['wlan_cfg']
    wg_cfg = conf['wg_cfg']
    test_cfgs = []
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'wlan_cfg_list': [wlan_cfg], 
                   'enable_wlan_on_default_wlan_group': False}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
    common_name = "%sAssign the WLAN to WLAN group: %s" % (tcid, wg_cfg['name'])
    test_params = {'wlangroup_name': wg_cfg['name'], 
                   'wlan_name_list': [wlan_cfg['ssid']]}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_On_APs'
    common_name = '%sVerify the WLAN on the active AP' % tcid
    test_params = {'ap_tag': conf['ap_tag'], 
                   'ssid': wlan_cfg['ssid']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))    
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '%sAssociate the target station' % tcid
    test_params = {'sta_tag': conf['sta_tag'], 
                   'wlan_cfg': wlan_cfg,
                   'verify_ip_subnet': False,
                   'start_browser': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Connectivity'
    common_name = "%sVerify the connectivity of the station" % tcid
    test_params = {'sta_tag': conf['sta_tag'],
                   'ap_tag': conf['ap_tag'],
                   'wlan_cfg': wlan_cfg,
                   'status': 'Authorized',
                   'username': wlan_cfg['username'],
                   'radio_mode': conf['radio_mode'],
                   'target_ip': conf['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, wg_cfg, 1))
    
    return test_cfgs

    
def define_test_cfg(tcfg):
    ap_tag = tcfg['active_ap']
    sta_tag = tcfg['target_station']
    ras_cfg = tcfg['raduis_svr_cfg']
    wg_cfg = tcfg['wg_cfg']
    radio_mode = tcfg['active_radio']
    
    test_cfgs = []
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP: %s' % ap_tag
    test_params = {'ap_tag': ap_tag, 'active_ap': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create station: %s' % sta_tag
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create a new WLAN group: %s" % (wg_cfg['name']) 
    test_cfgs.append(({'wgs_cfg': wg_cfg}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the WLAN group to radio '%s' of AP: %s" % (radio_mode, ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': wg_cfg['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create radius server: %s' % ras_cfg['server_name']
    test_cfgs.append(({'auth_ser_cfg_list': [ras_cfg]}, test_name, common_name, 0, False))
    
    
    for wlan_cfg in tcfg['wlan_cfg_list']:
        test_params = {
            'tcid': wlan_cfg['tcid'],
            'wlan_cfg': wlan_cfg,
            'wg_cfg': wg_cfg,
            'ap_tag': ap_tag,
            'sta_tag': sta_tag,
            'radio_mode': radio_mode,
            'target_ip': tcfg['target_ip'],
            }
        test_cfgs.extend(test_encryption(test_params))

    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all authentication servers to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
    
    #Do testing after upgrade.
    test_name = 'CB_ZD_Simply_Upgrade'
    common_name = 'DO upgrade'
    test_cfgs.append(({'build_stream':BUILD_STREAM,
                       'build_number':BUILD_NUMBER,
                       }, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create a new WLAN group: %s  after upgrade" % (wg_cfg['name']) 
    test_cfgs.append(({'wgs_cfg': wg_cfg}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the WLAN group to radio '%s' of AP: %s  after upgrade" % (radio_mode, ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': wg_cfg['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create radius server: %s after upgrade' % ras_cfg['server_name']
    test_cfgs.append(({'auth_ser_cfg_list': [ras_cfg]}, test_name, common_name, 0, False))
    
    
    for wlan_cfg in tcfg['wlan_cfg_list']:
        test_params = {
            'tcid': wlan_cfg['tcid'] + "after upgrade ",
            'wlan_cfg': wlan_cfg,
            'wg_cfg': wg_cfg,
            'ap_tag': ap_tag,
            'sta_tag': sta_tag,
            'radio_mode': radio_mode,
            'target_ip': tcfg['target_ip'],
            }
        test_cfgs.extend(test_encryption(test_params))

    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups to clean up after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all authentication servers to clean up after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))
           

    return test_cfgs


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_station = '',
                 active_radio = '',
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        active_ap = choose_active_ap(ap_sym_dict, "Choose an active AP: ")
        
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        active_radio = testsuite.get_target_sta_radio()
        
    else:
        active_ap = attrs['active_ap']
        target_sta = attrs['target_station']
        active_radio = attrs["active_radio"]    

    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = const.get_radio_mode_by_ap_model(active_ap_model)
    if active_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, active_radio)
        return
    
    
    set_build()

    raduis_svr_cfg = {
        'server_name': 'RADIUS_server',
        'server_addr': ras_ip_addr,
        'radius_auth_secret': '1234567890',
        'server_port': '1812',
        }
    
    wlan_cfg_list = define_Wlan_cfg(raduis_svr_cfg['server_name'])
    
    wg_cfg = {
        'name': 'rat-wg-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for encryption type test with Upgrade',
        'vlan_override': False,
        'wlan_member': {},
        }
    
    tcfg = {'raduis_svr_cfg': raduis_svr_cfg,
            'target_station': target_sta,
            'active_ap': active_ap,
            'active_radio': active_radio,
            'wlan_cfg_list': wlan_cfg_list,
            'wg_cfg': wg_cfg,
            'target_ip': '192.168.0.252'
            }
    test_cfgs = define_test_cfg(tcfg)
    
    test_cfgs = decorate_common_name(test_cfgs)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else: 
        ts_name = "Encryption Types - 11%s - With Upgrade" % active_radio
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify ZD to deploy WLANs with different encryption types",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
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
    