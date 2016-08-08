"""
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com

This suite is use to verify the reboot reason in the events of ZD, includes:
    - AP Application reboot
    - AP User reboot
    - ZD Warm reboot

The event is verified on ZD webUI and syslog server.  
"""

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(cfg):
    test_cfgs = []
    
    tc1_name = '[AP Application reboot]'
    tc2_name = '[AP User reboot]'
    tc3_name = '[ZD Warm reboot]'
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Select the test AP'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'active_ap': cfg['active_ap']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_Syslog'
    common_name = 'Configure the syslog server on ZD WebUI'
    test_cfgs.append(({'server_ip': cfg['syslog_ser_ip']}, test_name, common_name, 0, False))
    
    test_name = 'CB_LinuxPC_Config_Syslog'
    common_name = 'Start and remove all syslog logs on Linux server'
    #@author: Tsx,#@since 20150428 zf-12925
    test_cfgs.append(({'restart_server':True,'clear_log': True}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Events'
    common_name = '%s remove all ZD events' % tc1_name
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Reboot_AP'
    common_name = '%s reboot AP via ZD WebUI' % tc1_name
    test_cfgs.append(({'ap_tag': 'AP1',
                       'reboot': 'by zd'}, test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%s verify AP re join to ZD after reboot' % tc1_name
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Reboot_Reason'
    common_name = '%s verify AP join event on ZD WebUI' % tc1_name
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_reason': 'ap application reboot'}, test_name, common_name, 1, False))
   
    test_name = 'CB_LinuxPC_Verify_Syslog_Messages'
    common_name = '%s verify AP join events on syslog sever' % tc1_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Events'
    common_name = '%s remove all ZD events' % tc2_name
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Reboot_AP'
    common_name = '%s reboot AP via AP CLI' % tc2_name
    test_cfgs.append(({'ap_tag': 'AP1',
                       'reboot': 'by ap'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%s verify AP re join to ZD after reboot' % tc2_name
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Reboot_Reason'
    common_name = '%s verify AP join event on ZD WebUI' % tc2_name
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_reason': 'ap user reboot'}, test_name, common_name, 1, False))
   
    test_name = 'CB_LinuxPC_Verify_Syslog_Messages'
    common_name = '%s verify AP join events on syslog sever' % tc2_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Events'
    common_name = '%s remove all ZD events' % tc3_name
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Reboot'
    common_name = '%s reboot ZD' % tc3_name
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%s verify AP re join to ZD after reboot' % tc3_name
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Reboot_Reason'
    common_name = '%s verify ZD reboot events on ZD WebUI' % tc3_name
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_reason': 'zd warm reboot'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Reboot_Reason'
    common_name = '%s verify AP join event on ZD WebUI' % tc3_name
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_reason': ['ap heartbeat loss','ap user reboot']}, test_name, common_name, 1, False))
    
    test_name = 'CB_LinuxPC_Verify_Syslog_Messages'
    common_name = '%s verify ZD reboot events on syslog sever' % tc3_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Config_Syslog'
    common_name = 'Restore syslog server setting on ZD WebUI'
    test_cfgs.append(({'cleanup': True}, test_name, common_name, 0, True))
    
    return test_cfgs

def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']    
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]
    
    setting_cfg = {'active_ap': active_ap,
                   'syslog_ser_ip': '192.168.0.252'}
    
    test_cfgs = define_test_cfg(setting_cfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "Reboot reason in join event"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the reboot reason is shown in the join event",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
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
    
