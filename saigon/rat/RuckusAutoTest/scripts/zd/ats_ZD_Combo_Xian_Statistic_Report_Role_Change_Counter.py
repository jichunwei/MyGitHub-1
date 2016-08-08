'''
Created on 2013-9-23
@author: cwang@ruckuswireless.com
'''
import time
import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


def build_tcs(ap_tags):
    tcs = []
    tcs.append(({'ap_tags':ap_tags,
                 'test_fun_name':'up_link_change' 
                 },
                'StatisticReportAPTopologyChangeTester',
                '[MAP uplink change by manual/auto]ap-mesh-num-uplink-acquired',
                1,
                False
                ))
    
    tcs.append(({'ap_tags':ap_tags,
                 'test_fun_name':'map_reboot' 
                 },
                'StatisticReportAPTopologyChangeTester',
                '[Reboot MAP/MAP heartbeat lost]ap-mesh-num-uplink-acquired',
                1,
                False
                ))
    
    tcs.append(({'ap_tags':ap_tags,
                 'test_fun_name':'root_map_change'
                 },
                'StatisticReportAPTopologyChangeTester',
                '[RAP changes to MAP/MAP changes to RAP]ap-mesh-num-uplink-acquired',
                1,
                False
                ))
    
    tcs.append(({'ap_tags':ap_tags,
                 'test_fun_name':'disable_mesh_role'
                 },
                'StatisticReportAPTopologyChangeTester',
                '[Disable AP mesh role]ap-mesh-num-uplink-acquired',
                1,
                False
                ))
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Statistic Reporting-AP topology change counter",
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
    
    
    taglist = []
    for aptag, apinfo in ap_sym_dict.items():
        taglist = [aptag]
        radios = lib_Constant._ap_model_info[apinfo['model'].lower()]['radios']
        for aptag2, apinfo2 in ap_sym_dict.items():
            if aptag2 == aptag:
                continue
                        
            radios2 = lib_Constant._ap_model_info[apinfo['model'].lower()]['radios']
            if radios == radios2:
                taglist.append(aptag2)
        
        if len(taglist) > 3:
            break
    
    if len(taglist) < 3:
        raise Exception("Need more than 2 the same radios AP in your testbeds")
                
    
    ts_name_list = [("Statistic Reporting-AP topology change counter", build_tcs),                                                                          
                    ]
        
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(taglist[:3])
    
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