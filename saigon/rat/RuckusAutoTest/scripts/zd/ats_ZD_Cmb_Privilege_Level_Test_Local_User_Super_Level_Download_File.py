'''

'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    user_cfg = tcfg['user']
    
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all roles from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Single_Role' 
    common_name = 'create one super role'
    test_cfgs.append(({'role_cfg':tcfg['role']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User' 
    common_name = 'create one supper user'
    test_cfgs.append((tcfg['user'], test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a dpsk wlan,guest wlan on ZD'
    test_cfgs.append(({'wlan_cfg_list':[tcfg['dpsk_wlan'],tcfg['gp_wlan']],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Multi_DPSK'
    common_name = 'Create 5 DPSK'  
    test_cfgs.append((tcfg['gen_dpsk_para'], test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Multi_Guest_Passes'
    common_name = 'Create 5 guest passes'   
    test_cfgs.append((tcfg['guest_gen_para'], test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = 'login zd web by local super user'
    test_cfgs.append(({'login_name':user_cfg['username'],'login_pass':user_cfg['password'],'restore_zd_user':True}, test_name, common_name, 0, False))
    
    #@author: yuyanan @since:2014-8-28 optimize :parameter ap tag replace ap mac
    test_case_name='[Save AP system info]'
    test_name = 'CB_ZD_Download_AP_Sys_Info' 
    common_name = '%ssave ap system info'%test_case_name
    test_cfgs.append(({'ap_tag':tcfg['ap_tag']}, test_name, common_name, 1,False))
    
    test_case_name='[Save Debug Info]'
    test_name = 'CB_ZD_Save_Debug_Info' 
    common_name = '%ssave debug info'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 1,False))
    
    test_case_name='[Save Sys Info]'
    test_name = 'CB_ZD_Save_Debug_Info' 
    common_name = '%ssave system info'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 1,False))
    
    test_case_name='[download registration request file]'
    test_name = 'CB_ZD_Download_Registration_File' 
    common_name = '%sDownload registration request file'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 1,False))
    
    test_case_name='[backup ZD configuration]'
    test_name = 'CB_ZD_Backup' 
    common_name = '%sbackup configure file' %test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_case_name='[download guest pass record]'
    test_name = 'CB_ZD_Download_GuestPasses_Record'
    common_name = '%s Export guest passes to CSV file' % test_case_name
    test_params = {'username': tcfg['user']['username'], 
                   'password': tcfg['user']['password']}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 
    
    test_case_name='[download exist dpsk]'
    test_name = 'CB_ZD_Downlaod_DPSK_Record'
    common_name = '%s Export dpsk file' % test_case_name
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = 'login zd web by admin to clean configuration'
    test_cfgs.append(({'login_name':'admin','login_pass':'admin'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = 'Remove all DPSK from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = 'Remove all guest passes from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_Wlan'
    common_name = "Remove guest pass wlan"  
    test_cfgs.append(({'ssid': tcfg['gp_wlan']['ssid']}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_Wlan'
    common_name = "Remove dpsk pass wlan"  
    test_cfgs.append(({'ssid': tcfg['dpsk_wlan']['ssid']}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_Local_User'
    common_name = 'remove the new created user'
    param_cfg = {'username':tcfg['user']['username']}
    test_cfgs.append((param_cfg, test_name, common_name, 0,True))  
    
    test_name = 'CB_ZD_Remove_Roles'
    common_name = 'remove all new created role' 
    param_cfg = dict(role_list=[tcfg['role']['rolename']])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')


def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="super level Local User privilege level test-Download File"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an AP to do ping: ")
            if active_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % active_ap
            else:
                break
            
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
   
    role_cfg ={"rolename": "super_role", 
              "specify_wlan": "", 
              "guestpass": True, 
              "description": "",
              "group_attr": "", 
              "zd_admin": "full"}
    
    user_cfg =dict(  username = 'super_user',
                     password = 'super_user',
                     fullname = '',
                     role =role_cfg['rolename'],)
    
    dpsk_wlan = {'ssid': 'wlan-dpsk',
                    'auth': 'PSK',
                    'wpa_ver': 'WPA2',
                    'encryption': 'AES',
                    'type': 'standard',
                    'key_string': '1234567890',
                    'key_index': '',
                    'auth_svr': '',
                    'do_zero_it': True,
                    'do_dynamic_psk': True,                 
                    }
    
    gen_dpsk_para={'number_of_dpsk': 5,
                    'repeat_cnt': 1,                
                    'psk_expiration': 'Unlimited',
                    'expected_response_time': 30,
                    'wlan_cfg':dpsk_wlan}
    gp_wlan = {'ssid': 'wlan-guestpass',
                      'type': 'guest', 
                      'auth': 'open',
                      'encryption' : 'none',                
                      }
    guest_gen_para={'number_profile': '5',
                        'duration': '999',                        
                        'repeat_cnt': 1,   
                        'username': user_cfg['username'],
                        'password': user_cfg['password'],                                       
                        }
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="super level Local User privilege level test-Download File"

    tcfg = dict(
                target_sta = target_sta,
                dest_ip= '192.168.0.252',
                role = role_cfg,
                user = user_cfg,
                dpsk_wlan=dpsk_wlan,
                gen_dpsk_para = gen_dpsk_para,
                gp_wlan=gp_wlan,
                guest_gen_para=guest_gen_para,
                ap_tag = active_ap,
                )
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "super level Local User privilege level test-Download File", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    make_test_suite(**_dict)
    
