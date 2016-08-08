'''
add 8 wlan in default wlan grp
while 500 ap try to connect to zd,edit wlan and wlan grp cfg
check the status of apmng,stamng and webmng
'''

import sys
import logging
import copy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def defineTestConfiguration(wlan_cfg):
    test_cfgs = [] 

    test_case_name='[add 8 wlan in defalut Wlan group]'
    test_name = 'CB_Scaling_RemoveZDAllConfig'
    common_name = '%sRemove all the Configurations before add wlan' % test_case_name
    test_cfgs.append(({},test_name, common_name,1,False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate WLANs in ZD GUI'% test_case_name
    test_cfgs.append(( {'wlan_cfg_list':wlan_cfg}, test_name, common_name, 0, False))
    
    test_case_name='[reboot zd in zd cli]'
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%sreboot zd from zdcli'% test_case_name
    test_cfgs.append(( {'timeout':10*60}, test_name, common_name, 1, False))
    
    for restart in range(100):
        test_case_name='[remember pid,%d]' % restart
        test_name = 'CB_Scaling_ZD_CLI_Process_Check'
        common_name = '%s:apmgr and stamgr and webmgr daemon pid mark.' %test_case_name
        param_cfg = {}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_case_name='[edit wlan group while ap connecting,%d]' % restart
        test_name = 'CB_ZD_Config_Wlan_Group_And_Check_Ap'
        common_name = '%s:check ap number and config wlan group' %test_case_name
        param_cfg = {'wlan_cfg_list':wlan_cfg,'timeout':10*60,'expect_ap_num':500}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_case_name='[check pid,%d]' % restart
        test_name = 'CB_Scaling_ZD_CLI_Process_Check'
        common_name = '%s:apmgr and stamgr and webmgr daemon pid verify.' %test_case_name
        param_cfg = {}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
            
        test_case_name='[reboot zd in zd cli,%d]' % restart
        test_name = 'CB_ZD_CLI_Reboot_ZD'
        common_name = '%sreboot zd from zdcli'% test_case_name
        test_cfgs.append(( {'timeout':10*60}, test_name, common_name, 1, False))
    
    return test_cfgs

def define_wlan_cfg_list():
    logging.info('Generate a list of the WLAN configuration')
    
    conf = {'ssid': '',
            'auth': 'open',
            'encryption': 'none',
            }
    
    wlan_cfg_list = []
    for i in range(8):
        cfg = copy.deepcopy(conf)
        ssid = "wlan-%d" % (i)
        cfg['ssid'] = ssid
        wlan_cfg_list.append(cfg)
    return wlan_cfg_list
                


def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="edit wlan grp while ap connecting"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
    #ap_sym_dict = tb_cfg["ap_sym_dict"]
    #active_aps = testsuite.getActiveAp(ap_sym_dict)
    
    #get active ap mac list
    active_ap_mac_list=tb_cfg['ap_mac_list']
    
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="edit wlan grp while ap connecting"
    wlan_cfg=define_wlan_cfg_list()
    test_cfgs = defineTestConfiguration(wlan_cfg)
    ts = testsuite.get_testsuite(ts_name, 'edit wlan grp while ap connecting', interactive_mode = attrs["interactive_mode"], combotest=True)

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
    _dict['tbtype'] = 'ZD_Scaling'
    make_test_suite(**_dict)
    