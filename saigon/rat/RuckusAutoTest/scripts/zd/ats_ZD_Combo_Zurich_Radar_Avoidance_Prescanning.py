"""
This test suite is configure to allow testing follow test cases - which are belong to Radar Avoidance Prescanning:
    expect result: All steps should result properly.
    
    How to:
    [RAPS configuration test]
        1) Enable/disable RAPS function in ZD GUI and ZD CLI
        2) Enable/disable scand function in AP CLI and scand process in AP shell by command 'ps -ef | grep scand'

    [RAPS non-DFS channel and DFS blocked channel verification]
        1) Change country code from GB(UK).
        2) Use the command 'get channelavailability wifiX' to check both 2.4G and 5G channels' status on AP(2.4G:wifi0, 5G:wifi1, wifi2)
        4) Check the 'available'/ 'blocked' / 'dfs-blocked'  channels on ZD's WebUI.
        5) Compare 'available'/ 'blocked' / 'dfs-blocked' channels on AP with avariable channels displayed on ZD.They must be the same.
        6) Configure AP channel to a fixed DFS channel by ZD shell 'cat /etc/airespider-default/country-list.xml | grep United Kingdom'
        7) Create a standard WLAN, because non-Mesh AP detects radrar signal and does DFS channel hop only when WLAN exists in AP.
           (For Root/Mesh AP, we needn't create WLAN since meshu/meshd WLAN exists in Root/Mesh AP)
        8) Use the command 'radartool -i wifi1 bangradar' to generate radar signal and make AP change channel.
        9) Verify event that DFS channel changes to another value.
        10)Use the command 'get channelavailability wifi1' to check the 5G channels' status on AP
        11)Check the avariable channel status on ZD's WebUI
        12)Compare 'available'/ 'blocked' / 'dfs-blocked'  channels on AP with avariable channels displayed on ZD.They must be the same
        13)Change country code back to US

Created on June 2013
@author: kevin.tan@ruckuswireless.com
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _define_wlan_cfg():
    wlan_cfg = dict(ssid='raps-auto-test', auth='PSK', wpa_ver='WPA_Mixed', encryption='Auto', key_index='', key_string='raps-auto-test',
                    sta_auth='PSK', sta_wpa_ver='WPA2', sta_encryption='AES')

    return wlan_cfg

def defineTestConfiguration(cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    
    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD in the beginning'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap_list'][0],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    ######################################## case 1 #######################################################################
    test_case_name = '[RAPS configuration]'
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%sSet ZD to factory default' % (test_case_name)
    test_cfgs.append(({},test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_RAPS_Configuration'
    common_name = '%sRAPS configuration test in country code US' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sSet country code to UK' % (test_case_name)
    test_cfgs.append(({'country_code':'United Kingdom', 'unfix_ap': False}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_RAPS_Configuration'
    common_name = '%sRAPS configuration test in country code UK' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag}, test_name, common_name, 2, False))

    ######################################## case 2 #######################################################################
    test_case_name = '[RAPS channel status check]'

    test_name = 'CB_ZD_Set_Country_Code'
    common_name = '%sSet country code to UK' % (test_case_name)
    test_cfgs.append(({'country_code':'United Kingdom', 'unfix_ap': False}, test_name, common_name, 1, False))

    wlan_cfg = _define_wlan_cfg()

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a test WLAN on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg]}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_RAPS_Channel_Status_Check'
    common_name = '%sRAPS channel verification test'  % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag}, test_name, common_name, 2, False))
    
    #Recover to original status
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'Set country code back to US'
    test_cfgs.append(({'country_code':'United States', 'unfix_ap': False}, test_name, common_name, 0, True))

    return test_cfgs
 
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list     = tbcfg['sta_ip_list']
    ap_sym_dict     = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        if target_sta_radio != 'na':
            print "DFS only supports 802.11na(5GHz), select 11na automatically"
            target_sta_radio = 'na'

        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        model = ap_sym_dict[active_ap_list[0]]['model'].lower()
        if not (('sc8800' in model) or ('zf7782' in model) or ('zf7781' in model)):
            print 'Create test suits failed, active AP should be SC8800-S, SC8800S-AC, 7782, 7782-x, 7781-xy, etc. (ap-11n-ppc)'
            return
    else:        
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    tcfg = {
            'target_station':'%s' % target_sta,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            'radio_mode': target_sta_radio,
            }
        
    ts_name = 'Radio Avoidance Prescanning'
    ts = testsuite.get_testsuite(ts_name, 'Verify the mesh RAPS functionality', combotest=True)
    test_cfgs = defineTestConfiguration(tcfg)

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
    createTestSuite(**_dict)