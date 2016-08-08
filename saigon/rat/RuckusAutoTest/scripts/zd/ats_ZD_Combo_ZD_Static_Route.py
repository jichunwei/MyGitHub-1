"""
Configure ZD static route table and check whether if works or not
    
    Operations:
    1.    Create Static Route in ZD GUI and check it in ZD shell
    2.    Edit Static Route in ZD GUI and check it in ZD shell
    3.    Clone Static Route in ZD GUI and check it in ZD shell
    4.    Delete designed Static Route in ZD GUI and check it in ZD shell
    
    Route type:
    1.    subnet, such as '172.17.9.0/24'
    2.    host, such as '172.17.9.252/32'
    3.    mixed, such as '172.17.9.252/27', equals to subnet '172.28.30.224/27'

Created on 2013-05-15
@author: kevin.tan
"""

import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils


def define_test_cfg():
    test_cfgs = []
    
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = 'Delete all static routes at beginning'
    test_cfgs.append(({'operation': 'delete all'}, test_name, common_name, 0, False))

    #################################################
    test_case_name = '[subnet route]'
    route = {'name':'route_1', 'subnet':'172.17.9.0/24'}
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure a static route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'add',
                        'parameter': route, 'check_zd_shell': True}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Config_Static_Route'
    route_edit = {'name':'route_edit', 'subnet':'172.19.11.0/24'}
    common_name = '%sEdit a static route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'edit', 'name': route['name'],
                        'parameter': route_edit, 'check_zd_shell': True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    route_clone = {'name':'route_clone', 'subnet':'172.20.12.0/24'}
    common_name = '%sClone a static route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'clone', 'name': route_edit['name'],
                        'parameter': route_clone, 'check_zd_shell': True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete edited static route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'delete',
                        'name': route_edit['name'], 'parameter': route_edit, 'check_zd_shell': True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete cloned static route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'delete',
                        'name': route_clone['name'], 'parameter': route_clone, 'check_zd_shell': True}, test_name, common_name, 2, False))

    #################################################
    test_case_name = '[host route]'
    route = {'name':'route_2', 'subnet':'172.26.20.252/24'}
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure a static  route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'add',
                        'parameter': route, 'check_zd_shell': True}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete a static route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'delete',
                        'name': route['name'], 'parameter': route, 'check_zd_shell': True}, test_name, common_name, 2, False))

    #################################################
    test_case_name = '[mixed route]'
    route = {'name':'route_3', 'subnet':'172.28.30.252/27'} #equal to subnet '172.28.30.224/27'
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure a static  route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'add',
                        'parameter': route, 'check_zd_shell': True}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete a static route and check in ZD shell' % (test_case_name)
    test_cfgs.append(({'operation': 'delete',
                        'name': route['name'], 'parameter': route, 'check_zd_shell': True}, test_name, common_name, 2, False))

    #################################################
    test_case_name = '[negative route]'
    test_name = 'CB_ZD_Static_Route_Negative_Config'
    common_name = '%sCheck configure illegal route failed' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = 'Delete all static routes at last'
    test_cfgs.append(({'operation': 'delete all'}, test_name, common_name, 0, True))

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
        
    test_cfgs = define_test_cfg()
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "ZD Static Route"

    ts = testsuite.get_testsuite(ts_name, ("ZD Static Route"), combotest=True)

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
