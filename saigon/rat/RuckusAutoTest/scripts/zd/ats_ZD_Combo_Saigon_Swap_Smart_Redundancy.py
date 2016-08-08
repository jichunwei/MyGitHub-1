'''
Update @2011/9/8 by cwang@ruckuswireless.com
Update Content:
    Add TCID to test cases in order to report to testlink directly.
'''
import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration():
    test_cfgs = []
    input_cfg = defineInputConfig()
    

    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial test environment of test, call 2 ZD up'
    test_cfgs.append(({'zd1_ip_addr':input_cfg['zd1_ip_addr'], 'zd2_ip_addr':input_cfg['zd2_ip_addr'],
                       'share_secret':input_cfg['share_secret'],'sw_ip':input_cfg['sw_ip']},
                       test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "Get the Active ZD before test"
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_Standby_ZD'
    common_name = "Get the Standby ZD before test"
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_AP_In_Active_ZD'
    common_name = 'Get the Active ZD and the connected APs before test'
    test_cfgs.append(({'ap_active_zd':'former_active'},test_name,common_name,0,False))

    test_name = 'CB_ZD_SR_Swap'
    common_name = '[Smart Redundancy Swapping Active to Active]Verify ZDs change state from Active(Standby) to Active(Standby) properly'
    test_cfgs.append(({'type':'active to active','shut_down_zd2':False}, test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Swap'
    common_name = '[Smart Redundancy Swapping Active to Standby]Verify ZDs change state from Active(Standby) to Standby(Active) properly'
    test_cfgs.append(({'type':'active to standby','shut_down_zd2':False}, test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "Get the Active ZD after test"
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_Standby_ZD'
    common_name = "Get the Standby ZD after test"
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_AP_In_Active_ZD'
    common_name = 'Get the Active ZD and the connected APs after test'
    test_cfgs.append(({'ap_active_zd':'former_standby'},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Check_AP_Rehome'
    common_name = "[Smart Redundancy Swapping Active to Standby]Check the AP rehome"
    test_cfgs.append(({},test_name,common_name,1,False))

    test_name = 'CB_ZD_SR_AP_Rehome_Disable_Port'
    common_name = "[Smart Redundancy Swapping Active to Standby]Cut down network service for 5 sec on Active ZD, APs should still managed by Active ZD"
    test_cfgs.append(({},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy after test'
    test_cfgs.append(({},test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = "Clear up the Smart Redundancy test environment"
    test_cfgs.append(({},test_name, common_name,0,True))

    return test_cfgs

def defineInputConfig():
    test_conf = {'zd1_ip_addr':'192.168.0.2',
                 'zd2_ip_addr':'192.168.0.3',
                 'sw_ip':'192.168.0.253'
                 }

    test_conf['share_secret'] = _generate_secret_key(random.randint(5,15))
    return test_conf
 
def _generate_secret_key(n):
    al=list('abcdefghijklmnopqrstuvwxyz0123456789') 
    st='' 
    for i in range(n):
        index = random.randint(0,35) 
        st = st + al[index] 
    return st

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'ZD Smart Redundancy Swapping'
    ts = testsuite.get_testsuite(ts_name, 'Verify ZDs change state between Active and Standby properly', combotest=True)
    test_cfgs = defineTestConfiguration()

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