'''
Description:
    Configure Smart Redundancy information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com

Update @2011-9-21, by cwang@ruckuswireless.com
Update content:
    Add data plane for smart redundancy enable | disable.
'''

import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

def _get_wlan():
    return dict( name = "RAT-Open-None-CLI-SR-Interface",
                 ssid = "RAT-Open-None-CLI-SR-Interface", 
                 auth = "open", 
                 encryption = "none",                 
                 )
    
def build_setup_env():
    test_cfgs = []    
    test_cfgs.append(({'wlan_conf' : _get_wlan()},
                      'CB_ZD_CLI_Create_Wlan',
                      'Create a WLAN from CLI',
                      1, 
                      False
                      ))
    
    return test_cfgs

def build_cls_env():
    test_cfgs = []
    test_cfgs.append(({'name':'RAT-Open-None-CLI-SR-Interface'},
                       'CB_ZD_CLI_Remove_Wlan_Configuration',
                       'Remove WLAN from CLI',
                       0, 
                       False
                     ))    
    return test_cfgs

def build_asso_sta(tcid, sta = '192.168.1.11'):
    test_cfgs = []
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': sta}, 
                       'CB_ZD_Create_Station', 
                       '%sGet the station' % tcid, 
                       1, 
                       False))
               
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': _get_wlan()}, 
                      'CB_ZD_Associate_Station_1', 
                      '%sAssociate the station' % tcid, 
                      1, 
                      False))    

    
    test_cfgs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      '%sGet wifi address' % tcid, 
                      1, 
                      False))
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'allowed',
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       '%sThe station ping a target IP' % tcid, 
                       2, 
                       False))  
                    
    return test_cfgs


def build_tcs(sta, sr_conf):
    
    test_cfgs = []
    
    test_cfgs.extend(build_setup_env())
    
    common_id = '[Disable Smart Redundancy]'
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%sDisable Smart Redundancy via ZD CLI' %common_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))     
    
    test_cfgs.extend(build_asso_sta(common_id, sta)) 
   
    common_id = '[Enable Smart Redundancy]'
    test_name = 'CB_ZD_CLI_Config_SR'
    common_name = '%sConfig Smart Redundancy via ZD CLI' %common_id
    param_cfg = dict(sr_conf=sr_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_SR_Set_Get'
    common_name = '%sVerify SR CLI Set and CLI Get are the same info' %common_id
    param_cfg = dict(sr_conf=sr_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_SR_Set_GUIGet'
    common_name = '%sVerify SR CLI Set and GUI Get are the same info' %common_id
    param_cfg = dict(sr_conf=sr_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    #checking ssid valid or not.
    test_cfgs.extend(build_asso_sta(common_id, sta))
            
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Clean up the smart redundancy setting'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    common_id = '[Disable Smart Redundancy after enable]'    
    test_cfgs.extend(build_asso_sta(common_id, sta))  
    
    return test_cfgs


def def_sr_conf():
    conf = {}
    conf['peer_ip_addr'] = '192.168.0.3'
    conf['secret'] = utils.make_random_string(random.randint(1,15),
                                              type = 'alnum')
    
    return conf  
    

def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']    
    sta = testsuite.getTargetStation(sta_ip_list)
    ts_name = 'Configure Smart Redundancy via CLI and Verify via GUI'
    ts = testsuite.get_testsuite(ts_name, 'Smart Redundancy CLI Configuration', combotest=True)
    sr_conf = def_sr_conf()
    test_cfgs = build_tcs(sta, sr_conf)

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
    