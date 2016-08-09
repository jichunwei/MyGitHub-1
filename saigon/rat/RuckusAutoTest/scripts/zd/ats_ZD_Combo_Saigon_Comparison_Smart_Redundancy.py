'''
Udpate @2011/9/8, by cwang@ruckuswireless.com
Update Content:
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
    common_name = 'Initial Test Environment'
    test_cfgs.append(({'zd1_ip_addr':input_cfg['zd1_ip_addr'], 'zd2_ip_addr':\
                       input_cfg['zd2_ip_addr'],'share_secret':input_cfg['share_secret'],
                       'sw_ip':input_cfg['sw_ip']},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy before test'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '[Testing choice Active ZD rule by MAC]Disable switch port connectet to all ap'
    test_cfgs.append(({'ap_tag':'all','device':'ap'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[Testing choice Active ZD rule by MAC]Enable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name, 2,False))
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[Testing choice Active ZD rule by MAC]ZD with lower MAC address is Active when the ZDs have no APs.'
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
               
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[Testing choice Active ZD rule by MAC]Enable sw port connected to all ap'
    test_cfgs.append(({},test_name, common_name, 2, True))  
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[Testing choice Active ZD rule by MAC]Disable Smart Redundancy for comparison with same AP test'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Adjust_To_Same_AP'
    common_name = '[Testing choice Active ZD rule by MAC]Adjust the 2 ZDs to have the same APs'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[Testing choice Active ZD rule by MAC]Enable Smart Redundancy for comparison with same AP test'
    test_cfgs.append(({},test_name,common_name, 2,False))
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[Testing choice Active ZD rule by MAC]ZD with lower MAC address is Active when the ZDs have the same APs.'
    test_cfgs.append(({'except_state':'active'},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[Testing choice Active ZD rule by MAC]Disable Smart Redundancy after test'
    test_cfgs.append(({}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_SR_Enable'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Enable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name, 1,False))
    
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Get the Active ZD'
    test_cfgs.append(({},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Set_Active_ZD'
    common_name = '[Testing choice Acitve ZD rule by AP Number]set active zd as high mac zd'
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name,common_name,2,False))
        
    test_name = 'CB_Scaling_Waiting'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Waiting ap connect for %d mins ' % 1
    test_cfgs.append(({'timeout':1*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Disable Smart Redundancy for comparison with different APs test'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Check_High_Mac_Has_More_AP'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Make sure the higher MAC address has more AP.'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Enable Smart Redundancy for comparison with different APs test'
    test_cfgs.append(({},test_name,common_name, 2,False))
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Make sure the ZD with lower MAC address is Standby when the ZD has less APs.'
    test_cfgs.append(({'except_state':'standby'},test_name,common_name, 2,False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[Testing choice Acitve ZD rule by AP Number]Disable Smart Redundancy after test'
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
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
    tb_cfg = testsuite.getTestbedConfig(tb)
    
    ts_name = 'Smart Redundancy Active ZD selection Rule'
    
    ts = testsuite.get_testsuite(ts_name, 'Verify ZDs Comparison(AP and MAC)', combotest=True)
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
