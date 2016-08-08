'''
Created on Jan 24, 2014

@author: Jacky Luh

Description: 
    Generate guest pass and sent to the email box.
    Generate guest pass and snet ot the SMS info by the cell phone [can not implement by the auto script]
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

test_cfgs = {'active_ap': '', 'station': ''}
sta_ipaddr = '192.168.1.11'
dest_ip = '172.16.10.252'
target_url = 'http://172.16.10.252/'
username = 'test_local'
password = 'test_local'
wlan_name = "rat-wlan-guestaccess-%s" % (time.strftime("%H%M%S"))
wlan_cfg = {'name': wlan_name,
             'ssid': wlan_name,
             'auth': "open",
             'encryption': "none",
             'type': 'guest',
             'do_tunnel': False,
             }
wg_cfg = {'wg_name': 'wlan-wg-ng', 
          'description': 'utest-wg-22ng',
          'wlan_member': {wlan_cfg['name']: {}} 
          }

ap_cfg = {'radio_ng': {'wlangroups': 'wlan-wg-ng'}}

guest_policy = {'guestaccess_policy_cfg': dict(enable_share_guestpass = True,
                                               use_guestpass_auth = True,
                                               use_tou = False,
                                               redirect_url = '',
                                               email_content = '(GUEST NAME)|(GUEST PASS)|(EXPIRED TIME)|(WLAN NAME)'),
                'guestpass_policy_cfg': dict(is_first_use_expired = False,
                                             valid_day = '5'),
                'generate_guestpass_cfg': dict(type = "single",
                                               guest_fullname = "Guest-Auth",
                                               duration = "5",
                                               duration_unit = "Days",
                                               key = "",
                                               wlan = wlan_cfg['ssid'],
                                               email = '',
                                               remarks = "",
                                               is_shared = "YES",
                                               auth_ser = '',
                                               username = username,
                                               password = password),
                #updated by jluh, since@2014-07-03
                'multi_expect_guestpass_cfg': dict(expect_guestpass = 'ZVQPT-ROABD',
                                                  expect_fullname = "Guest-Auth")
                }


def define_test_configuration(id, **conf_dict):
    test_cfgs = []
    smtp_server_ip_addr = conf_dict['smtp_server_ip_addr']
    from_email = conf_dict['from_email']
    dest_email = conf_dict['dest_email']
    tc_cfg_list = [("[Generated Single Guest Pass and Sent to Email Box]",
                       "[Generated Single Guest Pass with Invalid Email Format]"),
                      ("[Generated Multi Guest Pass and Sent to Email Box]",
                       "[Generated Multi Guest Pass with Invalid Email Format]")]     
    
    test_name = 'CB_ZD_Clean_Up_Test_Configs'
    common_name = 'Clean up all test configs before the testing'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_Components'
    common_name = 'Create active components(ZD, AP, Station)'
    param_cfg = {'station': '192.168.1.11',
                 'ap': 'AP_01',
                 'linuxpc': smtp_server_ip_addr}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Guest_User_and_Profile'
    common_name = 'Create the guest user and profile'
    param_cfg = {'username': username,
                 'password': password,
                 'g_prof_cfg': guest_policy['guestaccess_policy_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    test_name = 'CB_ZD_Create_Smtp_Server'
    common_name = 'Create the smtp server for the email box'
    param_cfg = {'smtp_serv_cfg': dict(from_email_addr = from_email, 
                                       smtp_server = smtp_server_ip_addr, 
                                       server_name = smtp_server_ip_addr,
                                       server_port = '25',
                                       username = 'lab', 
                                       password = 'lab4man1', 
                                       tls_option = False, 
                                       starttls_option = False,
                                       cfg_name = 'Smtp Server with Server IP')}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Guest_Wlan_and_Wlangroup'
    common_name = 'Create the guest wlan and wlangroup'
    param_cfg = {'wlan_cfg': wlan_cfg,
                 'wg_cfg': wg_cfg,
                 'ap_cfg': ap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    if 'Multi' in tc_cfg_list[id][0]:
        guest_policy['generate_guestpass_cfg'].update({'type': 'multiple'})
    guest_policy['generate_guestpass_cfg'].update({'email': dest_email})
    
    test_name = 'CB_ZD_Generate_Guest_Pass_with_Email'
    common_name = '%sGenerate the guest pass and sent to the email box' \
                   % tc_cfg_list[id][0]
    param_cfg = {'email_format': 'valid',
                 'g_pass_cfg': guest_policy['generate_guestpass_cfg'],
                 #updated by jluh, since@2014-07-03
                 'multi_expe_gp_cfg': guest_policy['multi_expect_guestpass_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Verify_Active_Email_for_Expected_Guest_Pass'
    common_name = '%sCheck the email box for the guest pass email and the guest pass' \
                   % tc_cfg_list[id][0]
    param_cfg = {'email_format': 'valid',
                 'email': dest_email}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Station_Associate_Guest_Wlan'
    common_name = '%sStation associated the guest wlan' \
                   % tc_cfg_list[id][0]
    test_params = {'wlan_cfg': wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_for_Expected_Status'
    common_name = '%sVerify the station unauthorized status before the guest authentication' \
                   % tc_cfg_list[id][0]
    param_cfg = {'status': 'unauthorized'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Perform_Guest_Auth'
    common_name = '%sPerform the guest authentication with the guest pass' \
                   % tc_cfg_list[id][0]
    param_cfg = guest_policy['guestaccess_policy_cfg']
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_for_Expected_Status'
    common_name = '%sVerify the station unauthorized status after the guest authentication' \
                   % tc_cfg_list[id][0]
    param_cfg = {'status': 'authorized'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    if id == 0:
        test_name = 'CB_ZD_Create_Guest_User_and_Profile'
        common_name = '%sThe content can not be saved with the invalid email format' \
                       % tc_cfg_list[id][1]
        param_cfg = {'email_format': 'invalid',
                     'g_prof_cfg': {'invalid_email_content': '(GUEST NAME)|(GUEST PASS)'}}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    elif id == 1:
        test_name = 'CB_ZD_Generate_Guest_Pass_with_Email'
        common_name = '%sThe csv file can not be imported with the invalid email format' \
                        % tc_cfg_list[id][1]
        param_cfg = {'email_format': 'invalid',
                     'g_pass_cfg': guest_policy['generate_guestpass_cfg'],
                     #updated by jluh, since@2014-07-03
                     'multi_expe_gp_cfg': guest_policy['multi_expect_guestpass_cfg']}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    else:
        pass 
    
    test_name = 'CB_ZD_Clean_Up_Test_Configs'
    common_name = 'Clean up all test configs in the test suite'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))            
    
    return test_cfgs


def create_test_suite(**kwargs):
    ts_name_list = ['Generate single guest pass and sent to the email box',
                    'Generate multi guest pass and sent to the email box',
                    ]
    i = 0
    smtp_server_ip_addr = raw_input("Email Server ip address : [press [Enter], default: '192.168.0.252']").lower()
    if not smtp_server_ip_addr:
        smtp_server_ip_addr = '192.168.0.252'
    from_email = raw_input("From Email : [press [Enter], default: 'lab@example.net']").lower()
    if not from_email:
        from_email = 'lab@example.net'
    dest_email = raw_input("Inbox Email : [press [Enter], default: 'super@example.net']").lower()
    if not dest_email:
        dest_email = 'super@example.net'
        
    conf_dict = {'smtp_server_ip_addr': smtp_server_ip_addr,
                 'from_email': from_email,
                 'dest_email': dest_email}
        
    for ts_name in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, ts_name, combotest=True)
        test_cfgs = define_test_configuration(i, **conf_dict)
        i += 1
    
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
    create_test_suite(**_dict)
    