'''
west.li, switch active/standby zd by 
1.disable active zd switch port
2.reboot active zd
3.killall -9 stamgr
4.killall -9 apmgr
'''
import sys
import random
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration():
    test_cfgs = []
 
    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial Test Environment'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy to do test'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = 'make sure the aps in testbed connected after SR enable'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Set_Active_ZD'
    common_name = 'set active zd as zd1'
    test_cfgs.append(({'zd':'zd1'},test_name,common_name,0,False))
        
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = 'Check all of APs are connected after set active zd'
    param_cfg = dict(timeout = 60,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_case_name = '[kill stamgr in active zd]'
    test_name = 'CB_ZD_Kill_Process_In_ZD'
    common_name = '%skill stamgr in active zd'%test_case_name
    test_cfgs.append(({'zdcli':'zdcli1','process_name':'stamgr'},test_name,common_name,1,False))

    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected to new active zd'%test_case_name
    param_cfg = dict(timeout = 3*60,zdcli='zdcli2')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting former active zd up ' % (test_case_name)
    test_cfgs.append(({'timeout':2*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Verify_Active_ZD'
    common_name = '%sverify the active zd is corrected'%test_case_name
    test_cfgs.append(({'expect_zd':'zd2'},test_name,common_name,2,False))
    
    test_case_name = '[kill apmgr in active zd]'
    test_name = 'CB_ZD_Kill_Process_In_ZD'
    common_name = '%skill stamgr in active zd'%test_case_name
    test_cfgs.append(({'zdcli':'zdcli2','process_name':'apmgr'},test_name,common_name,1,False))

    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected to new active zd'%test_case_name
    param_cfg = dict(timeout = 3*60,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting former active zd up ' % (test_case_name)
    test_cfgs.append(({'timeout':2*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Verify_Active_ZD'
    common_name = '%sverify the active zd is corrected'%test_case_name
    test_cfgs.append(({'expect_zd':'zd1'},test_name,common_name,2,False))
    
    test_case_name = '[reboot active zd]'
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%sreboot zd from zdcli'% test_case_name
    test_cfgs.append(( {'timeout':10*60,'zd_tag':'zdcli1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected to new active zd'%test_case_name
    param_cfg = dict(timeout = 3*60,zdcli='zdcli2')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_SR_Verify_Active_ZD'
    common_name = '%sverify the active zd is corrected'%test_case_name
    test_cfgs.append(({'expect_zd':'zd2'},test_name,common_name,2,False))
    
    test_case_name = '[disable active zd switch port]'
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '%sDisable switch port connectet with active zd' % test_case_name
    test_cfgs.append(({'zdcli':'zdcli2','device':'zd'},test_name, common_name, 1, False))   
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected to new active zd'%test_case_name
    param_cfg = dict(timeout = 3*60,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%sEnable sw port connected to zd' % test_case_name
    test_cfgs.append(({'device':'zd'},test_name, common_name, 2, True)) 
    
    test_name = 'CB_ZD_SR_Verify_Active_ZD'
    common_name = '%sverify the active zd is corrected'%test_case_name
    test_cfgs.append(({'expect_zd':'zd1'},test_name,common_name,2,True))
    
    return test_cfgs
#
#def defineInputConfig():
#    test_conf = {'zd1_ip_addr':'192.168.0.2',
#                 'zd2_ip_addr':'192.168.0.3',
#                 'sw_ip':'192.168.0.253'
#                 }
#
#    test_conf['share_secret'] = _generate_secret_key(random.randint(5,15))
#    return test_conf
# 
def _generate_secret_key(n):
    al=list('abcdefghijklmnopqrstuvwxyz0123456789') 
    st='' 
    for i in range(n):
        index = random.randint(0,35) 
        st = st + al[index] 
    return st

def createTestSuite(**kwargs):
#    tb = testsuite.getTestbed2(**kwargs)
#    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'active zd and standby zd switch'
    ts = testsuite.get_testsuite(ts_name, 'active zd and standby zd switch', combotest=True)
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
