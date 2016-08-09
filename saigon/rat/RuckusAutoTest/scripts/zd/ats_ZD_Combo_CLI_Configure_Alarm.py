'''
@author: serena.tan@ruckuswireless.com

Description: This test suite is used to verify whether the configure alarm commands in ZD CLI work well.

'''


import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_alarm_settings():
    alarm_cfg_list = []
    
    alarm_cfg_list.append(dict(email_addr = 'lab@example.net', smtp_server = '192.168.0.252', server_port = '25',
                               username = '', password = '', tls_option = False, starttls_option = False,
                               cfg_name = 'Email Alarm with Server IP'))
    
    alarm_cfg_list.append(dict(email_addr = 'lab@example.net', smtp_server = '192.168.0.252', server_port = '25',
                               username = 'lab', password = 'lab4man1', tls_option = False, starttls_option = False,
                               cfg_name = 'Email Alarm with Server IP - Auth'))
    
    alarm_cfg_list.append(dict(email_addr = 'lab@example.net', smtp_server = '192.168.0.252', server_port = '25',
                               username = 'lab', password = 'lab4man1', tls_option = True, starttls_option = True,
                               cfg_name = 'Email Alarm with Server IP - Auth - TLS'))

    alarm_cfg_list.append(dict(email_addr = 'lab@example.net', smtp_server = 'www.example.net', server_port = '25',
                               username = '', password = '', tls_option = False, starttls_option = False,
                               cfg_name = 'Email Alarm Using NameServer'))
    
    alarm_cfg_list.append(dict(email_addr = 'lab@example.net', smtp_server = 'www.example.net', server_port = '25',
                               username = 'lab', password = 'lab4man1', tls_option = False, starttls_option = False,
                               cfg_name = 'Email Alarm Using NameServer - Auth'))
    
    alarm_cfg_list.append(dict(email_addr = 'lab@example.net', smtp_server = 'www.example.net', server_port = '25',
                               username = 'lab', password = 'lab4man1', tls_option = True, starttls_option = True,
                               cfg_name = 'Email Alarm Using NameServer - Auth - TLS'))

    return alarm_cfg_list


def define_test_cfg(cfg):
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Find_Station'
    common_name = 'Get the station'    
    test_cfgs.append(( {'target_station':cfg['target_station'],}, test_name, common_name, 0, False))

    for alarm_cfg in cfg['alarm_cfg_list']:
        test_name = 'CB_ZD_Remove_Alarm_Setting'
        common_name = '[%s] Remove alarm settings from ZD GUI' % alarm_cfg['cfg_name'] 
        test_cfgs.append(({}, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Clear_Alarm_MailBox'
        common_name = '[%s] Remove all mails from mail server' % alarm_cfg['cfg_name']   
        test_cfgs.append(({'mail_folder': cfg['mail_folder']}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_CLI_Configure_Alarm'
        common_name = '[%s] Configure alarm settings in ZD CLI' % alarm_cfg['cfg_name'] 
        test_cfgs.append(({'alarm_cfg': alarm_cfg}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Get_Alarm_Info'
        common_name = '[%s] Get alarm settings from ZD GUI' % alarm_cfg['cfg_name'] 
        test_cfgs.append(({}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_CLI_Verify_Alarm_Cfg_In_GUI'
        common_name = '[%s] Verify alarm settings in ZD GUI' % alarm_cfg['cfg_name'] 
        test_cfgs.append(({'alarm_cfg': alarm_cfg}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Alarm_Setting_On_ZD'
        common_name = '[%s] Verify alarm settings with test button' % alarm_cfg['cfg_name']  
        test_cfgs.append(({}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Alarm_Mail_On_Server'
        common_name = '[%s] Verify the test mail on mail server' % alarm_cfg['cfg_name']   
        test_cfgs.append(({'mail_folder': cfg['mail_folder'], 'mail_to': alarm_cfg['email_addr'], 'is_test_mail': True}, 
                          test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Clear_Alarm_MailBox'
        common_name = '[%s] Remove all mails from mail server' % alarm_cfg['cfg_name']
        test_cfgs.append(({}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD'
        common_name = '[%s] Clear all alarm logs from ZD GUI' % alarm_cfg['cfg_name'] 
        test_cfgs.append(({}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Create_Spoofing_Wlan'
        common_name = '[%s] Create a spoofing WLAN in ZD GUI' % alarm_cfg['cfg_name']
        test_cfgs.append(({'wlan_cfg_list':[cfg['wlan_cfg']]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Waiting_Alarm_Trigger'
        common_name = '[%s] Wait for alarm trigger' % alarm_cfg['cfg_name']
        test_cfgs.append(({}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Alarm_Mail_On_Server'
        common_name = '[%s] Verify alarm mails on mail server' % alarm_cfg['cfg_name']   
        test_cfgs.append(({'mail_folder': cfg['mail_folder'], 'mail_to': alarm_cfg['email_addr'], 'is_test_mail': False}, 
                          test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_Alarm_Setting'
    common_name = 'Remove alarm settings from ZD GUI after test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD GUI after test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
    else:
        target_sta = sta_ip_list[attrs["station"][0]]

    alarm_cfg_list = define_alarm_settings() 
    
    wlan_cfg = {'ssid': 'zdcli_alarm_wlan',
                'auth': 'open',
                'encryption': 'none'
                }
    
    tcfg = dict(target_station = target_sta,
                mail_folder = '/home/lab/Maildir/new', 
                alarm_cfg_list = alarm_cfg_list,
                wlan_cfg = wlan_cfg
                )

    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    
    else:
        ts_name = "ZD CLI - Configure Alarm"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify zd cli configure alarm commands",
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
    
    