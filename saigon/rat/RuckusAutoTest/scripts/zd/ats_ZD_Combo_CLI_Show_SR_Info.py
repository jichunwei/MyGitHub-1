import sys
import random
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration():
    test_cfgs = []
    input_cfg = defineInputConfig()
    
    ex_id = "[Smart redundancy Configure from GUI, Check from CLI]"
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_SR'
    common_name = '%s1.Show SR Information on one ZD CLI' % ex_id
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_No_SR_Info'
    common_name = '%s2. Verify there is no SR information on CLI' % ex_id
    test_cfgs.append(({},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_CLI_Show_SR'
    common_name = '%s3.Show SR Information on another ZD CLI' % ex_id
    test_cfgs.append(({'zdcli':'zdcli2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_No_SR_Info'
    common_name = '%s4. Verify there is no SR information on CLI' % ex_id
    test_cfgs.append(({},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%s5. Enable Smart Redundancy via ZD GUI' % ex_id
    test_cfgs.append(({},test_name,common_name,2,False))

    test_name = 'CB_ZD_CLI_Show_SR'
    common_name = '%s6.Show SR Information on one ZD CLI' % ex_id
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Get_Info'
    common_name = '%s7.Get Smart Redundancy Information on one ZD' % ex_id
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SR_Info'
    common_name = '%s8. Verify one ZD SR information' % ex_id
    test_cfgs.append(({},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_CLI_Show_SR'
    common_name = '%s9.Show SR Information on another CLI' % ex_id
    test_cfgs.append(({'zdcli':'zdcli2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Get_Info'
    common_name = '%s10.Get Smart Redundancy Information on another ZD' % ex_id
    test_cfgs.append(({'zd':'zd2'},test_name, common_name, 2, False))
       
    test_name = 'CB_ZD_CLI_Verify_SR_Info'
    common_name = '%s11. Verify SR information are the same' % ex_id
    test_cfgs.append(({},test_name,common_name,2,False))
    
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
                 }
    test_conf['share_secret'] = _generate_secret_key(random.randint(1,15))
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

    ts_name = 'TCID: x - Show SR Information'
    ts = testsuite.get_testsuite(ts_name, 'Verify ZD CLI show SR information correct', combotest=True)
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
