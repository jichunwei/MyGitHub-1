'''
Update@2011/9/8, by cwang@ruckuswireless.com
Update content:
    1) Append TCID to test cases so that report to test link directly.
    2) Update Level hierarchical for test cases.
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
                       'share_secret':input_cfg['share_secret']},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Clear_Event'
    common_name = 'Clear Event Log'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[Enable Smart Redundancy]Enable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name,1,False))

    test_name = 'CB_ZD_SR_Check_Event'
    common_name = '[Checking Enable Smart Redundancy Event]Verify there is {Enable} message'
    test_cfgs.append(({'find_string':'Smart Redundancy is [enabled]'},
                      test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Check_State_Bar'
    common_name = '[Checking Smart Redundancy Status Bar]Check the State bar Status'
    test_cfgs.append(({},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Check_Dashboard'
    common_name = '[Checking Smart Redundancy Widget Dashboard]Check Widget in Dashboard'
    test_cfgs.append(({},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[Disable Smart Redundancy]Disable Smart Redundancy '
    test_cfgs.append(({},test_name, common_name, 1, False))
       
    test_name = 'CB_ZD_SR_Check_Event'
    common_name = '[Checking Disabled Event]Verify there is Disabled message'
    test_cfgs.append(({'find_string':'Smart Redundancy is [disabled]'},
                      test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Enable_Different_Share_Secret'
    common_name = '[Testing Shared Secret Function]Enable DIFFERENT share secret'
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Check_Event'
    common_name = '[Testing Shared Secret Function]Verify mismatched message'
    test_cfgs.append(({'find_string':'[Smart Redundancy] Failed! Shared Secrets are mismatched'},
                      test_name, common_name,2, False))
    
    test_name = 'CB_ZD_SR_Enable_Wrong_Peer_IP'
    common_name = '[Testing Wrong Peer IP]Enable wrong peer IP address'
    test_cfgs.append(({'ip_addr':'1.1.1.1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy after test'
    test_cfgs.append(({},test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = "Clear up the Smart Redundancy test environment"
    test_cfgs.append(({},test_name, common_name,0,False)) 

    return test_cfgs


def defineInputConfig():
    test_conf = {'zd1_ip_addr':'192.168.0.2',
                 'zd2_ip_addr':'192.168.0.3',
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

    ts_name = 'Enable and disable smart redundancy'
    ts = testsuite.get_testsuite(ts_name, 'Verify the ZD Smart Redundancy can be enabled/disable via Web UI', combotest=True)
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
