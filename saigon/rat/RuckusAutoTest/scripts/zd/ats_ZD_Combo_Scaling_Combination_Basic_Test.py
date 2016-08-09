'''
Created on 2010-6-12
@author: cwang@ruckuswireless.com
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    pre_name = 'Verify ap all connect at the begining'
        
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs are connected including RuckusAP and SIMAP' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    pre_name = 'restore to full CFG'
    test_name = 'CB_ZD_Restore'
    common_name = '[%s]:Restore ZD to full configurations' %pre_name
    param_cfg = dict(restore_file_path = cfg['full_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    pre_name = 'process check after restore'
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '[%s]:apmgr and stamgr daemon pid mark.' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    pre_name = 'Verify ap all connect after restore full CFG'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs after restoring' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
        
    pre_name = 'search AP function'
    test_name = 'CB_ZD_Search_APs'
    common_name = '[%s]:Test search APs functionality from ZD' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
        
    pre_name = 'sort AP function'
    test_name = 'CB_ZD_Sort_APs'
    common_name = '[%s]:Test sort APs functionality from ZD' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
        
    pre_name = 'ap CFG Max value check'
    test_name = 'CB_ZDCLI_Scaling_Config_AP_Setting'
    common_name = '[%s]:Set APs configuration with Maximum value' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    

    pre_name = 'check ap all connect with max value configuration'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs are connected including RuckusAP and SIMAP when set ap configuration to maximum' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    pre_name = 'check ap name with max value configuration'
    test_name = 'CB_Scaling_Verify_AP_Side_Device_Name_From_ZDCLI'
    common_name = '[%s]:Check APs device name with Maximum value' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    

    pre_name = 'check ap gps with max value configuration'
    test_name = 'CB_Scaling_Verify_AP_Side_Gps_Coordinates_From_ZDCLI'
    common_name = '[%s]:Check APs device gps with Maximum value' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    #skip location setting, bug#17492
#    test_name = 'CB_Scaling_Verify_AP_Side_Device_Location_From_ZDCLI'
#    common_name = 'Check APs device location with Maximum value'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    #verify DPSK from WEBUI    
    pre_name = 'check guest pass under full cfg'
    test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
    common_name = '[%s]:Verify 9999 guest passes under ZD WEBUI'  %pre_name
    test_cfgs.append(( {'total_nums':'9999'}, test_name, common_name, 1, False))
    
    #Verify DPSK from WEBUI    
    pre_name = 'check muti dpsk full cfg'
    test_name = 'CB_ZD_Verify_Multi_DPSK'
    common_name = '[%s]:Verify 5000 DPSK under ZD WEBUI'  %pre_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))         

    pre_name = 'process check after operation'
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '[%s]:apmgr and stamgr daemon pid checking.' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    pre_name = 'backup batch configuration'
    test_name = 'CB_Scaling_Backup_Config'
    common_name = '[%s]:Backup ZD under batch configurations' %pre_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))    
    
    pre_name = 'restore batch configuration'
    test_name = 'CB_ZD_Restore'
    common_name = '[%s]:Restore ZD under batch configurations' %pre_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))    
    
    #Verify DPSK from WEBUI    
    pre_name = 'check guest pass under batch CFG'
    test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
    common_name = '[%s]:Verify 9999 guest passes under zd webui after system restore' %pre_name
    test_cfgs.append(( {'total_nums':'9999'}, test_name, common_name, 1, False))
        
    #Verify DPSK from WEBUI
    pre_name = 'check dpsk under batch CFG'
    test_name = 'CB_ZD_Verify_Multi_DPSK'
    common_name = '[%s]:Verify 5000 dpsk under zd webui after system restore'  %pre_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    pre_name = 'check aps all connect under batch CFG'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Verify all of aps are connected after system restore' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
        
    pre_name = 'restore empty CFG'
    test_name = 'CB_ZD_Restore'
    common_name = '[%s]:Restore ZD to empty configurations' %pre_name
    param_cfg = dict(restore_file_path = cfg['empty_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    pre_name = 'check aps all connect under empty CFG'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Re-check all of APs after restoring' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))   
    
    return test_cfgs    

def define_test_params(tbcfg, cfg):
    cfg['timeout'] = 1800 * 3    
#    import os
#    file = os.path.join(os.path.expanduser('~'), r"Desktop\full_cfg.bak")
#    cfg['full_config_path'] = file
#    file = os.path.join(os.path.expanduser('~'), r"Desktop\empty_cfg.bak")
#    cfg['empty_config_path'] = file    
#    
    import os
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\full_cfg.bak" )    
    cfg['full_config_path'] = file
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\empty_cfg.bak" )    
    cfg['empty_config_path'] = file      

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
#    sta_ip_list = tbcfg['sta_ip_list']    
        
    ts_name = 'Maximum APs - Combination Test -Basic'
    ts = testsuite.get_testsuite(ts_name, 'Maximum APs - Combination Test -Basic', combotest=True)
    cfg = dict()
    define_test_params(tbcfg, cfg)
    test_cfgs = define_test_cfg(cfg)

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
    _dict['tbtype'] = 'ZD_Scaling'
    createTestSuite(**_dict)
