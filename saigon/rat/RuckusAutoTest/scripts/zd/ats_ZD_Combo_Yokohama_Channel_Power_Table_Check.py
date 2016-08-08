"""
	Channel table and power table consistency check between ZD and AP usage
    
    expect result: All steps should result properly.
    
    How to:
        1)  Download latest files('country-list.xml','regdomain') by HTTP URL
        2)  Check channel table consistency between ZD and AP
        3)  Download latest files('country-codes.csv') by HTTP URL
        4)  Check country table consistency between ZD and AP
        5)  Download latest files('country-matrix.xls','regdmn_chan.h') by HTTP URL
        6)  Check power table consistency between ZD and AP

Created on 2013-2-18
@author: kevin.tan
"""

import os
import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils


#1st file---country-list.xml
#2nd file---regdomain
#3rd file---country-codes.csv
#4th file---Country matrix.xls
#5th file---regdmn_chan.h

http_url_path   = r'https://ruckuswirelesscom-2.sharepoint.microsoftonline.com/engineering/softwareengineering/Shared%20Documents/Yokohama%20-%209.6/Channel%20Power%20table/'
local_file_path = 'C:\\tmp\\'

def define_test_cfg(cfg):
    test_cfgs = []
    
    flist1 = ['country-list.xml','regdomain']
    flist2 = ['country-codes.csv']
    flist3 = ['country_matrix.xls','regdmn_chan.h']

    ####################### TEST CASE I ###############################
    test_case_name = "[Channel table check]"

    test_name = 'CB_ZD_Dowload_Http_Url'
    common_name = '%sDownload latest files by HTTP URL' % test_case_name
    test_cfgs.append(({'http_file_url_list': [(http_url_path+flist1[0]), (http_url_path+flist1[1])],
                       'local_file_path': local_file_path}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Check_Channel_Table'
    common_name = '%sCheck channel table consistency between ZD and AP' % test_case_name
    test_cfgs.append(({'local_file_path': local_file_path,
					   'file_name_list': flist1},test_name, common_name, 1, False))  


    ####################### TEST CASE II ###############################
    test_case_name = "[Country table check]"

    test_name = 'CB_ZD_Dowload_Http_Url'
    common_name = '%sDownload latest files by HTTP URL' % test_case_name
    test_cfgs.append(({'http_file_url_list': [(http_url_path+flist2[0])],
                       'local_file_path': local_file_path}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Check_Country_Table'
    common_name = '%sCheck power table consistency between ZD and AP' % test_case_name
    test_cfgs.append(({'file_name':'country-codes.csv'},
					   test_name, common_name, 1, False))  

    
    ####################### TEST CASE III ###############################
    test_case_name = "[Power table check]"

    test_name = 'CB_ZD_Dowload_Http_Url'
    common_name = '%sDownload latest files country-matrix.xls by HTTP URL' % test_case_name
    test_cfgs.append(({'http_file_url_list': [(http_url_path+flist3[0]), (http_url_path+flist3[1])],
                       'local_file_path': local_file_path}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Check_Power_Table'
    common_name = '%sCheck power table consistency between ZD and AP' % test_case_name
    test_cfgs.append(({'local_file_path': local_file_path,
					   'file_name_list': flist3},test_name, common_name, 1, False))  


    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
  
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    tcfg = {
            }
    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Channel and power table check"

    ts = testsuite.get_testsuite(ts_name, "Channel and power table check" , combotest=True)

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
