import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration():
    test_cfgs = []
    input_cfg = defineInputConfig()
    
#    Enter buildstream of zd3k[i.e, ZD3000_8.2.1.0_production or ZD3000_mainline]:
#    baseline_bstream = raw_input("Please enter the baseline build stream(upgrade from)\n [i.e, ZD3000_8.2.1.0_production or ZD3000_mainline]: ")
#    baseline_bno = raw_input("Please enter the baseline build no: ")
#    baseline_full_version = raw_input('Please enter the baseline full version[i.e, 9.0.0.0.22]: ')
#    baselineBuildPath = raw_input('Please enter the full path of baseline build file: ')
    
#    target_bstream = raw_input("Please enter the target build stream(upgrade to)\n [i.e, ZD3000_8.2.1.0_production or ZD3000_mainline]: ")
#    target_bno = raw_input("Please enter the target build no: ")
#    target_full_version = raw_input('Please enter the target full version[i.e, 9.0.0.0.23]: ')
#    targetBuildPath = raw_input('Please enter the full path of target build file: ')
    
    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial test environment of test, call 2 ZD up'
    test_cfgs.append(({'zd1_ip_addr':input_cfg['zd1_ip_addr'], 'zd2_ip_addr':input_cfg['zd2_ip_addr'],
                       'share_secret':input_cfg['share_secret']},
                       test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
#    cfg = dict(zd_build_stream = baseline_bstream,zd_bno = baseline_bno,zd_img_file_path = baselineBuildPath)
#    test_name = 'CB_Scaling_Download_ZD_Image'
#    common_name = 'Download Baseline image file'
#    test_cfgs.append((cfg,test_name,common_name,0,False))
    case_name = '[downgrade the zds separately to base build]'
    test_name = 'CB_ZD_SR_Single_Upgrade'
    common_name = '%sUpgrade one ZD to base line version' % case_name
    test_cfgs.append(({'image_file_path':input_cfg['base_img_file_path']},test_name,common_name,0,False))
    
    case_name = '[enable SR]'
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%sEnable Smart Redundancy' % case_name 
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_AP_In_Active_ZD'
    common_name = '%sGet the Active ZD and the connected APs.' % case_name
    test_cfgs.append(({'ap_active_zd':'former_active'},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Clear_Event'
    common_name = 'Clear Event Log'
    test_cfgs.append(({},test_name,common_name,0,False))
    
#    cfg = dict(zd_build_stream = target_bstream,zd_bno = target_bno ,zd_img_file_path = targetBuildPath)
#    test_name = 'CB_Scaling_Download_ZD_Image'
#    common_name = 'Download Target version image file'
#    test_cfgs.append((cfg,test_name,common_name,0,False))
#    case_name = '[upgrade the zds to target build in SR]'
#    test_name = 'CB_ZD_SR_Upgrade'
#    common_name = '%sUpgrade a Pair of Smart Redundancy from Standby ZD' % case_name
#    test_cfgs.append(({'upgrade_from':'standby','image_file_path':input_cfg['target_img_file_path']},test_name,common_name,1,False))
    case_name = '[upgrade when SR enabled]'
    test_name = 'CB_ZD_SR_Upgrade'
    common_name = '%sUpgrade a Pair of Smart Redundancy from Active ZD' % case_name
    test_cfgs.append(({'image_file_path':input_cfg['target_img_file_path']},test_name,common_name,1,False))
    
    case_name = '[check version]'
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the Standby ZD version, make sure the Standby ZD was upgraded' % case_name
    test_cfgs.append(({'expect_version':input_cfg['target_version_no']},test_name,common_name,2,False))
    
#    test_name = 'CB_ZD_SR_Select_Active_Upgrade'
#    common_name = '[Upgrade testing]Check the Active ZD version, Upgrade Active local device if the version mismatch'
#    test_cfgs.append(({'expect_version':target_full_version,},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the active ZD was upgraded' % case_name
    test_cfgs.append(({'expect_version':input_cfg['target_version_no'],'zd_type':'active'},test_name,common_name,2,False))

    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "Get the Active ZD again"
    test_cfgs.append(({},test_name,common_name,2,False))
    
    case_name='[check ap rehome]'
    test_name = 'CB_ZD_SR_Get_AP_In_Active_ZD'
    common_name = "%sGet All the AP in Active ZD again" % case_name
    test_cfgs.append(({'ap_active_zd':'former_standby'},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Check_AP_Rehome'
    common_name = "%sCheck the AP rehome" % case_name 
    test_cfgs.append(({},test_name,common_name,2,False))
    
    case_name='[check event]'
    test_name = 'CB_ZD_SR_Check_Event'
    common_name = '%sVerify there is ZD image has been upgraded message' % case_name 
    test_cfgs.append(({'find_string':'ZD image has been upgraded'},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Check_Event_On_Single_ZD'
    common_name = '%sCheck active zd event log' % case_name 
    test_cfgs.append(({'find_string':'[Smart Redundancy] System state changed to [Active] due to [system is in active state]'},
                      test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Check_Event_On_Single_ZD'
    common_name = '%sChecking standby zd event log' % case_name 
    test_cfgs.append(({'find_string':'[Smart Redundancy] System state changed to [Standby] due to [peer ZoneDirector is in active state]','zd_type':'standby'},
                      test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = "Clear up the Smart Redundancy test environment"
    test_cfgs.append(({},test_name, common_name,0,False))

    return test_cfgs

def defineInputConfig():
    test_conf = {'zd1_ip_addr':'192.168.0.2',
                 'zd2_ip_addr':'192.168.0.3',
                 'sw_ip':'192.168.0.253'
                 }
    test_conf['share_secret'] = _generate_secret_key(random.randint(5,15))
    
    import os
    file = os.path.join(os.path.expanduser('~'), r"C:\Downloads\ZD3000_9.2.0.0.138.tar.gz" )
    test_conf['base_img_file_path'] = file    
    file = os.path.join(os.path.expanduser('~'), r"C:\Downloads\ZD3000_9.3.0.0.80.tar.gz" )
    test_conf['target_img_file_path'] = file
    test_conf['base_version_no'] = '9.2.0.0.138'
    test_conf['target_version_no'] = '9.3.0.0.80'
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

    ts_name = 'Upgrade Downgrade in Smart Redundancy'
    ts = testsuite.get_testsuite(ts_name, 'Verify ZDs Upgrade properly when the Smart Redundancy was enabled', combotest=True)
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
