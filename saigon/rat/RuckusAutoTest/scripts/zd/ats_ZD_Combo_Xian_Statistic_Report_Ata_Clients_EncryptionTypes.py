'''
Created on 2013-8-5
@author: cwang@ruckuswireless.com
'''
import time
import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


def build_encryption_types():
    tcs = []
        
    tcs.append(({},
                'CB_ATA_Setup_ENV',
                'Setup ATA ENV, bind with veriwave.',
                0,
                False
                ))    
    
    tcid = "[Statistic report with different encryption types]"
    tcs.append(({},
                'CB_ATA_Test_Sta_Encryption_Types',
                '%sTest for encryption types' % tcid,
                1,
                False
                ))
    
    
    tcs.append(({},
                'CB_ATA_Purge_ENV',
                '%sPurge Ports from veriwave' % tcid,
                0,
                True
                ))
       
    return tcs


def build_wispr():
    tcs = []
    tcs.append(({},
            'CB_ATA_Setup_ENV',
            'Setup ATA ENV, bind with veriwave.',
            0,
            False
            ))   
    
    tcid = "[Statistic report station session with WISPr]"
    tcs.append(({},
                'CB_ATA_Test_Sta_WISPr',
                '%sstation session information',
                1,
                False
                ))
    
    tcs.append(({},
                'CB_ATA_Purge_ENV',
                '%sPurge Ports from veriwave' % tcid,
                0,
                True
                ))    
    return tcs

def build_dpsk():
    tcs = []
    tcs.append(({},
            'CB_ATA_Setup_ENV',
            'Setup ATA ENV, bind with veriwave.',
            0,
            False
            ))   
    
    tcid = "[Statistic report with DPSK]"
    tcs.append(({},
                'CB_ATA_Test_Sta_DPSK',
                '%sDPSK testing.',
                1,
                False
                ))
    
    tcs.append(({},
                'CB_ATA_Purge_ENV',
                '%sPurge Ports from veriwave' % tcid,
                0,
                True
                ))    
    return tcs

    
    
def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Statistic Reporting-Clients-Encryptions-Types",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    
    if attrs["interactive_mode"]:        
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, 
                                                 "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()        
    else:
        ts_name = attrs["testsuite_name"]
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name            
            break
    
    
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
    
    
    ts_name_list = [
                    ('ATA clients Encryption types.', build_tcs),                                                                       
                    ]
    cfg = {}
    cfg['target_station'] = sta_ip_addr
    cfg['all_aps_mac_list'] = tbcfg['ap_mac_list']
    cfg['ap_radio'] = target_sta_radio
    cfg['active_ap'] = active_ap
    cfg['ap_sym_dict'] = ap_sym_dict
        
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(cfg)
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
            
def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)