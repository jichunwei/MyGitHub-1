# Copyright (C) 2013 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Mar 2013

This testsuite is configure to allow testing follow test cases - which are belong to Syslog enhancement:


Note:
Please update the upgrade configuration for test case upgrade to new build  
"""

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

level_dict = {'emerg': '0', 'alert': '1', 'crit': '2', 'err': '3',
              'warning': '4', 'notice': '5', 'info': '6', 'debug': '7'}
level_path_dict = {'emerg': '/var/log/test-emerg.log', 'alert': '/var/log/test-alert.log', 
                   'crit': '/var/log/test-crit.log', 'err': '/var/log/test-err.log',
                   'warning': '/var/log/test-warning.log', 'notice': '/var/log/test-notice.log', 
                   'info': '/var/log/test-info.log', 'debug': '/var/log/test-debug.log'}
facility_path_dict = {'keep': '/var/log/local0.log', 'local0': '/var/log/local0.log', 'local7': '/var/log/local7.log',
                      'local1': '/var/log/local1.log', 'local2': '/var/log/local2.log', 'local3': '/var/log/local3.log',
                      'local4': '/var/log/local4.log', 'local5': '/var/log/local5.log', 'local6': '/var/log/local6.log',}

def define_test_cfg(active_ap):
    test_cfgs = []
    ap_tag = 'AP1'
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_params = {'active_ap': active_ap,
                   'ap_tag': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    tcname = 'Configure Remote Syslog Server IP'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': None, 'zd_priority_level': None,
                  'ap_facility_name': None, 'ap_priority_level': None}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'zd', ap_tag, False))
    
    # Option setting for ZD
    tcname = 'ZD Syslog with keep facility and level debug'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'keep', 'zd_priority_level': 'debug',
                  'ap_facility_name': 'local6', 'ap_priority_level': 'emerg'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'zd', ap_tag, True))
    
    tcname = 'ZD Syslog with local0 facility and level info'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local0', 'zd_priority_level': 'info',
                  'ap_facility_name': 'local5', 'ap_priority_level': 'emerg'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'zd', ap_tag, True))
    
    tcname = 'ZD Syslog with local1 facility and level notice'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local1', 'zd_priority_level': 'notice',
                  'ap_facility_name': 'local3', 'ap_priority_level': 'crit'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'zd', ap_tag, True))
    
    tcname = 'ZD Syslog with local4 facility and level warning'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local4', 'zd_priority_level': 'warning',
                  'ap_facility_name': 'local2', 'ap_priority_level': 'alert'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'zd', ap_tag, True))
    
    tcname = 'ZD Syslog with local7 facility and level err'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local7', 'zd_priority_level': 'err',
                  'ap_facility_name': 'keep', 'ap_priority_level': 'emerg'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'zd', ap_tag, True))
    
    # Option setting for APs
    tcname = 'AP Syslog with keep facility and level debug'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'keep', 'zd_priority_level': 'emerg',
                  'ap_facility_name': 'keep', 'ap_priority_level': 'debug'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'ap', ap_tag, True))
    
    tcname = 'AP Syslog with local0 facility and level info'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local2', 'zd_priority_level': 'emerg',
                  'ap_facility_name': 'local0', 'ap_priority_level': 'info'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'ap', ap_tag, True))
    
    tcname = 'AP Syslog with local1 facility and level notice'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local3', 'zd_priority_level': 'crit',
                  'ap_facility_name': 'local1', 'ap_priority_level': 'notice'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'ap', ap_tag, True))
    
    tcname = 'AP Syslog with local4 facility and level warning'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local5', 'zd_priority_level': 'alert',
                  'ap_facility_name': 'local4', 'ap_priority_level': 'warning'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'ap', ap_tag, True))
    
    tcname = 'AP Syslog with local7 facility and level err'
    syslog_cfg = {'remote_syslog_ip': '192.168.0.252', 
                  'zd_facility_name': 'local6', 'zd_priority_level': 'emerg',
                  'ap_facility_name': 'local7', 'ap_priority_level': 'err'}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'ap', ap_tag, True))
    
    tcname = 'Disable Remote Syslog Server'
    syslog_cfg = {'enable_remote_syslog': False}
    test_cfgs.extend(_create_cb_test_cases(tcname, syslog_cfg.copy(), 'zd', ap_tag, False))
    
    return test_cfgs

def _create_cb_test_cases(tcname, syslog_cfg, expected_from, ap_tag, verify_log):
    test_cfgs = []
    if syslog_cfg.get('enable_remote_syslog') == False\
    or not syslog_cfg['zd_priority_level']\
    or not syslog_cfg['zd_facility_name']\
    or not syslog_cfg['ap_facility_name']\
    or not syslog_cfg['ap_facility_name']:
        level = ''
        facility_path = []
    elif expected_from == 'zd':
        level = level_dict[syslog_cfg['zd_priority_level']]
        facility_path = [facility_path_dict[syslog_cfg['zd_facility_name']]]
    else:
        level = level_dict[syslog_cfg['ap_priority_level']]
        facility_path = [facility_path_dict[syslog_cfg['ap_facility_name']]]
    
    lower_level_paths = [level_path_dict[key] for key in level_dict.keys() if level_dict[key] <= level]
    higher_level_paths = [level_path_dict[key] for key in level_dict.keys() if level_dict[key] > level]
    
    test_name = 'CB_ZD_CLI_Configure_Syslog'
    common_name = '[%s] Configure Syslog setting' % tcname
    test_params = {'syslog_cfg': syslog_cfg}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Syslog_Setting'
    common_name = '[%s] Verify Syslog setting on ZD and AP' % tcname
    test_params = {'expected_syslog_cfg': syslog_cfg,
                   'ap_tag': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    if not verify_log or int(level) < 3:
        return test_cfgs
    
    if expected_from == 'zd':
        test_name = 'CB_ZDCLI_Enable_All_Debug_Log'
        common_name = '[%s] Enable all debug log on ZD' % tcname
        test_params = {}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    else:
        test_name = 'CB_AP_CLI_Enable_All_Debug_Log'
        common_name = '[%s] Enable all debug log on AP' % tcname
        test_params = {'ap_tag': ap_tag}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    params = {} if expected_from == 'zd' else {'ap_tag': ap_tag} 
    
    test_name = 'CB_LinuxPC_Config_Syslog'
    common_name = '[%s] Clear all logs on remote server' % tcname
    test_params = {'clear_log': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Reboot_AP'
    common_name = '[%s] Reboot AP to trigger logs' % tcname
    test_params = {'ap_tag': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '[%s] Wait for AP rejoin system' % tcname
    test_params = {'ap_tag': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_LinuxPC_Verify_Syslog_Record'
    common_name = '[%s] Verify the logs is sent to server with facility name' % tcname
    test_params = params.copy() 
    test_params.update({'expected_log_file_paths': facility_path})
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    if lower_level_paths:
        test_name = 'CB_LinuxPC_Verify_Syslog_Record'
        common_name = '[%s] Verify the logs with lower level is sent to remote server' % tcname
        test_params = params.copy() 
        test_params.update({'expected_log_file_paths': lower_level_paths, 'is_optional': True})
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    if higher_level_paths:
        test_name = 'CB_LinuxPC_Verify_Syslog_Record'
        common_name = '[%s] Verify the logs with higher level is not sent to remote server' % tcname
        test_params = params.copy() 
        test_params.update({'expected_log_file_paths': higher_level_paths, 'is_empty': True})
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    return test_cfgs
    

def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = testsuite.getActiveAp(ap_sym_dict)[0]            

        
    test_cfgs = define_test_cfg(active_ap)
        
    ts_name = "Syslog Enhancement"
    ts = testsuite.get_testsuite(ts_name, "Verify the syslog enhancement feature", combotest=True)
    
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