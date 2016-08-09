"""
Author: cwang
Email: cwang@ruckuswireless.com
"""

import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def build_user_reboot_tcs(cfg):
    tcs = []   
    alarm_setting = dict(
        email_addr = 'lab@example.net',
        server_name = '192.168.0.252', 
        server_port = 25, 
        username = 'lab', 
        password = 'lab4man1', 
        setting_name = 'ALARM-TRIGGER-IP-AUTH')
    
    tcs.append(({'mail_folder':cfg.get('mail_folder')},
                'CB_ZD_Clear_Alarm_MailBox',
                'Remove all email from Mail server',
                0,
                False
                ))
    
    tcs.append(({'alarm_cfg':alarm_setting},
                'CB_ZD_CLI_Configure_Alarm',
                'Enable Alarm Settings',
                0,
                False
                ))
    
    tcid = "[Warm restart with reason (user reboot)]"
    tcs.append(({},
                'CB_ZD_Clear_Alarm_Log_On_ZD',
                '%sClear Alarm logging on ZD' % tcid,
                0,
                False
                ))
        
    tcs.append(({},
                'CB_ZD_CLI_Reboot_ZD',
                '%sReboot ZD' % tcid,
                1,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Waiting_Alarm_Trigger',
                '%sWait for Alarm trigger' % tcid,
                2,
                False))
    
    tcs.append(({'mail_folder': cfg['mail_folder'], 
                 'mail_to': alarm_setting['email_addr'], 
                 'is_test_mail': False},
                'CB_ZD_Verify_Alarm_Mail_On_Server',
                '%sVerify alarm mail on server' % tcid,
                2,
                False
                ))
    
    tcid = "[warm restart with reason (watchdog timeout)]"
    
    tcs.append(({},
                'CB_ZD_Clear_Alarm_Log_On_ZD',
                '%sClear Alarm logging on ZD' % tcid,
                0,
                False
                ))
        
    tcs.append(({},
                'CB_ZD_CLI_Watchdog_Timeout',
                '%skillall -9 wd_feeder' % tcid,
                1,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Waiting_Alarm_Trigger',
                '%sWait for Alarm trigger' % tcid,
                2,
                False))
    
    tcs.append(({'mail_folder': cfg['mail_folder'], 
                 'mail_to': alarm_setting['email_addr'], 
                 'is_test_mail': False},
                'CB_ZD_Verify_Alarm_Mail_On_Server',
                '%sVerify alarm mail on server' % tcid,
                2,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_Alarm_Setting',
                'Remove Alarm Setting',
                0,
                True
                ))
    
    return tcs
    
def create_testsuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 testsuite_name = "Email Alarm Trigger - Reboot",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    tcfg = dict(
        mail_folder = '/home/lab/Maildir/new'
    )
    
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify email alarm trigger-Reboot",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
    test_cfgs = build_user_reboot_tcs(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
       
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_testsuite(**_dict)
    