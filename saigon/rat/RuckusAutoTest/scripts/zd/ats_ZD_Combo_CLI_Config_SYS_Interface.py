'''
Description:
    Configure System Interface information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(sys_if_conf):
    common_id = '[system_interface]'
    test_cfgs = []
   
    test_name = 'CB_ZD_CLI_Config_SYS_IF'
    common_name = '%s1.Configure System Interface via ZD CLI' %common_id
    param_cfg = dict(sys_if_conf=sys_if_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_SYS_IF_Set_Get'
    common_name = '%s2.Verify SYS Interface CLI Set and CLI Get are the same info' %common_id
    param_cfg = dict(sys_if_conf=sys_if_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_SYS_IF_Set_GUIGet'
    common_name = '%s3.Verify SYS Interface CLI Set and GUI Get are the same info' %common_id
    param_cfg = dict(sys_if_conf=sys_if_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_Verify_SYS_IF_Vlan'
    common_name = '%s4.Set and Verify System Interface Management VLAN 301' %common_id
    param_cfg = dict(sys_if_conf = dict(vlan_id = 301))
    test_cfgs.append((param_cfg,test_name,common_name,1,False))
    
    test_name = 'CB_ZD_CLI_SYS_IF_Remove_Verify_VLAN'
    common_name = '%s5.Remove and Verify management VLAN via CLI' %common_id
    param_cfg = dict(sys_if_conf = dict(vlan_id = 301))
    test_cfgs.append((param_cfg,test_name,common_name,1,False))
    
    test_name = 'CB_ZD_CLI_Config_SYS_IF'
    common_name = '%s6.Configure System Interface mode to DHCP' %common_id
    param_cfg = dict(sys_if_conf=dict(mode = 'dhcp'))
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    return test_cfgs


def def_conf():
    conf = {}
    conf['ip_addr'] = '192.168.0.2'
    conf['net_mask'] = '255.255.255.0'
#    conf['vlan_id'] = '2'
    conf['mode'] = 'static'
    conf['gateway'] = '192.168.0.253'
    conf['pri_dns'] = '192.168.0.252'
    conf['sec_dns'] = '192.168.0.254'
    return conf  
    

def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ts_name = 'Configure SYS Interface via CLI and Verify via GUI'
    ts = testsuite.get_testsuite(ts_name, 'SYS Interface CLI Configuration', combotest=True)
    sys_conf = def_conf()
    test_cfgs = define_test_configuration(sys_conf)

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
    