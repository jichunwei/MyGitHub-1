'''
Description: 
    Show SNMPV2 Agent setting on ZD CLI, verify the information on ZD GUI.
    By Chris
    cwang@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def gen_id(id):
    return '(%d) ' % id

def define_test_configuration(cfg):
    test_cfgs = []
    ex_id = "[SNMP Agent configure from GUI, Check from CLI]"
    i = 1     
    test_name = 'CB_ZD_Get_SNMP_Agent_Info'
    common_name = '%s%sGet SNMPV2 Agent setting information from GUI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV2_Info'
    common_name = '%s%sGet SNMPV2 Agent information from CLI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    i += 1    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info'
    common_name = '%s%sVerify SNMPV2 Agent setting between GUI and CLI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    
    i += 1    
    test_name = 'CB_ZD_Set_SNMP_Agent_Info'
    common_name = '%s%sEnable snmp agent setting information from CLI' % (ex_id, gen_id(i))
    param_cfg =     {'contact': u'support@ruckuswireless.com',
                     'enabled': True,
                     'location': u'880 West Maude Avenue, Suite 101, Sunnyvale, CA 94085 USA',
                     'ro_community': u'public',
                     'rw_community': u'private'
                     }
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    i += 1
    test_name = 'CB_ZD_Get_SNMP_Agent_Info'
    common_name = '%s%sGet SNMPV2 Agent setting information from GUI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV2_Info'
    common_name = '%s%sGet SNMPV2 Agent configuration information from CLI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    i += 1    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info'
    common_name = '%s%sVerify SNMPV2 Agent setting between GUI and CLI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    
    i += 1    
    test_name = 'CB_ZD_Set_SNMP_Agent_Info'
    common_name = '%s%sDisable snmp agent setting information from CLI' % (ex_id, gen_id(i))
    param_cfg =     {'contact': u'support@ruckuswireless.com',
                     'enabled': False,
                     'location': u'880 West Maude Avenue, Suite 101, Sunnyvale, CA 94085 USA',
                     'ro_community': u'public',
                     'rw_community': u'private'
                     }
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    i += 1
    test_name = 'CB_ZD_Get_SNMP_Agent_Info'
    common_name = '%s%sGet SNMPV2 Agent setting information from GUI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV2_Info'
    common_name = '%s%sGet SNMPV2 Agent configuration information from CLI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    i += 1    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info'
    common_name = '%s%sVerify SNMPV2 Agent setting between GUI and CLI' % (ex_id, gen_id(i))
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
         
    
    return test_cfgs


def define_test_paramter():
    cfg = {}             
    return cfg


def create_test_suite(**kwargs):
    ts_name = 'TCID: x-Show SNMPV2 Agent setting information in CLI'
    ts = testsuite.get_testsuite(ts_name, 'Show SNMPV2 Agent setting information in CLI', combotest=True)
    cfg = define_test_paramter()
    test_cfgs = define_test_configuration(cfg)

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
    