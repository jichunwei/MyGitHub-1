"""
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn 
"""

import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_alarm_settings():
    alarm_settings = []
    
    # Test with server IP 
    # Without Authentication
    alarm_settings.append(dict(email_addr = 'lab@example.net', server_name = '192.168.0.252', setting_name = 'ALARM-TRIGGER-IP'))
    # With Authentication
    alarm_settings.append(dict(
        email_addr = 'lab@example.net',
        server_name = '192.168.0.252', 
        server_port = 25, 
        username = 'lab', 
        password = 'lab4man1', 
        setting_name = 'ALARM-TRIGGER-IP-AUTH'
    ))
    # With Authentication and Encryption
    alarm_settings.append(dict(
        email_addr = 'lab@example.net',
        server_name = '192.168.0.252', 
        server_port = 25, 
        username = 'lab', 
        password = 'lab4man1',
        tls_option = True, 
        starttls_option = True,
        setting_name = 'ALARM-TRIGGER-IP-AUTH-TLS' 
    ))
    
    # Testing with server name 
    # Without authentication
    alarm_settings.append(dict(email_addr = 'lab@example.net', server_name = 'www.example.net', setting_name = 'ALARM-TRIGGER-NAMESERVER'))
    
    # With Authentication
    alarm_settings.append(dict(
        email_addr = 'lab@example.net',
        server_name = 'www.example.net', 
        server_port = 25, 
        username = 'lab', 
        password = 'lab4man1',
        setting_name = 'ALARM-TRIGGER-NAMESERVER-AUTH'
    ))
    
    # With Authentication and Encryption
    alarm_settings.append(dict(
        email_addr = 'lab@example.net',
        server_name = 'www.example.net', 
        server_port = 25, 
        username = 'lab', 
        password = 'lab4man1',
        tls_option = True, 
        starttls_option = True, 
        setting_name = 'ALARM-TRIGGER-NAMESERVER-AUTH-TLS'
    ))
    
    return alarm_settings

def define_test_cfg(cfg):
    test_cfgs = []

    wlan_cfg = dict(ssid = 'rat-alarm-trigger', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False)

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from Zone Director'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Find_Station'
    common_name = 'Get the station'    
    test_cfgs.append(( {'target_station':cfg['target_station'],}, test_name, common_name, 0, False))

    for alarm_setting in cfg['alarm_setting_list']:
        test_name = 'CB_ZD_Clear_Alarm_MailBox'
        common_name = '%s - 1: Remove all email from Mail Server' % alarm_setting['setting_name']   
        test_cfgs.append(({'mail_folder': cfg['mail_folder']}, test_name, common_name, 0, False))
    
        test_name = 'CB_ZD_Config_Alarm_Setting'
        common_name = '%s - 2: Enable Alarm Settings' % alarm_setting['setting_name'] 
        test_cfgs.append(({'alarm_setting': alarm_setting}, test_name, common_name, 0, False))
    
        test_name = 'CB_ZD_Verify_Alarm_Setting_On_ZD'
        common_name = '%s - 3: Verify Alarm Settings with Test Button' % alarm_setting['setting_name']  
        test_cfgs.append(({}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Verify_Alarm_Mail_On_Server'
        common_name = '%s - 4: Verify Alarm Mail on Server' % alarm_setting['setting_name']   
        test_cfgs.append(({'mail_folder': cfg['mail_folder'], 'mail_to': alarm_setting['email_addr'], 'is_test_mail': True}, 
                          test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Clear_Alarm_MailBox'
        common_name = '%s - 5: Remove all email from Mail Server' % alarm_setting['setting_name']
        test_cfgs.append(({}, test_name, common_name, 0, False))
    
        test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD'
        common_name = '%s - 6: Clear all alarm log on Zone Director' % alarm_setting['setting_name'] 
        test_cfgs.append(({}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Create_Spoofing_Wlan'
        common_name = '%s - 7: Create spoofing WLAN' % alarm_setting['setting_name']
        test_cfgs.append(( {'wlan_cfg_list':[wlan_cfg]}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Waiting_Alarm_Trigger'
        common_name = '%s - 8: Wait for Alarm Trigger' % alarm_setting['setting_name']
        test_cfgs.append(({}, test_name, common_name, 0, False))
    
        test_name = 'CB_ZD_Verify_Alarm_Mail_On_Server'
        common_name = '%s - 9: Verify Alarm Mail On Server' % alarm_setting['setting_name']   
        test_cfgs.append(({'mail_folder': cfg['mail_folder'], 'mail_to': alarm_setting['email_addr'], 'is_test_mail': False},
                           test_name, common_name, 0, False))
    
        test_name = 'CB_ZD_Remove_Alarm_Setting'
        common_name = '%s - 10: Remove Alarm Setting' % alarm_setting['setting_name'] 
        test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from Zone Director to Cleanup'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 testsuite_name = "Email Alarm Trigger - Combo",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
    else:
        target_sta = sta_ip_list[attrs["station"][0]]

    tcfg = dict(
        mail_folder = '/home/lab/Maildir/new'
    )
    tcfg['alarm_setting_list'] = define_alarm_settings() 
    tcfg['target_station'] = target_sta

    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify email alarm trigger",
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
    