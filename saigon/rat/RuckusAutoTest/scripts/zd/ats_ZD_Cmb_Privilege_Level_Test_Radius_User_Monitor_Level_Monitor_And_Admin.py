'''
verify the privilege level of monitor user is correct
monitor user can only monitor ZD and unable to see any in configuration page
'''


import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    user_cfg = tcfg['user']
    local_user_cfg = tcfg['local_user_cfg']
    
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all roles from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Single_Role' 
    common_name = 'create one monitor role'
    test_cfgs.append(({'role_cfg':tcfg['role']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User' 
    common_name = 'create one monitor user'
    test_cfgs.append((local_user_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = 'create Radius server via WebUI'
    test_cfgs.append(({'auth_ser_cfg_list':[tcfg['server_cfg']]}, test_name, common_name, 0, False))
    
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
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select auth server for zd admin'
    param_cfg = dict(tcfg['server_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  

    test_name = 'CB_ZD_Test_Login' 
    common_name = 'login zd web by Radius monitor user'
    test_cfgs.append(({'login_name':user_cfg['username'],'login_pass':user_cfg['password'],'restore_zd_user':True}, test_name, common_name, 0, False))
    
    #@author: yuyanan @since:2014-8-28 optimize :parameter ap tag replace ap mac
    test_case_name='[check ap connection]'
    test_name = 'CB_ZD_Privilage_Level_Ping_AP' 
    common_name = '%smonitor user ping ap should successfully'%test_case_name
    test_cfgs.append(({'ap_tag':tcfg['ap_tag']}, test_name, common_name, 1,False))
    
    test_case_name='[delete dpsk]'
    test_name = 'CB_ZD_Privilage_Level_Remove_DPSK' 
    common_name = '%smonitor user can not remove dpsk'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[show blocked clients]'
    test_name = 'CB_ZD_Privilage_Level_Show_Block_Clients' 
    common_name = '%smonitor user can not show blocked clients'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[delete guest pass]'
    test_name = 'CB_ZD_Privilage_Level_Remove_Guest_Pass' 
    common_name = '%smonitor user can not remove guest pass'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[clear all event]'
    test_name = 'CB_ZD_Privilage_Level_Clear_All_Event' 
    common_name = '%smonitor user can not clear all event'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[change real time monitor status]'
    test_name = 'CB_ZD_Privilage_Level_Change_Real_Time_Monitor_Status' 
    common_name = '%smonitor user can not change real time monitor status'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[change language]'
    test_name = 'CB_ZD_Privilage_Level_Change_Language' 
    common_name = '%smonitor user can not change language'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[change session timeout]'
    test_name = 'CB_ZD_Privilage_Level_Change_Session_Timeout' 
    common_name = '%smonitor user can not change session timeout'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[set debug log level]'
    test_name = 'CB_ZD_Privilage_Level_Set_Debug_Log' 
    common_name = '%smonitor user can not set debug log level'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
    test_case_name='[set remote trouble shooting]'
    test_name = 'CB_ZD_Privilage_Level_set_remote_trouble_shooting' 
    common_name = '%smonitor user can not set remote trouble shooting'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 1,False))
    
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
    param_cfg = {'username':tcfg['local_user_cfg']['username']}
    test_cfgs.append((param_cfg, test_name, common_name, 0,True))  
    
    test_name = 'CB_ZD_Remove_Roles'
    common_name = 'remove all new created role' 
    param_cfg = dict(role_list=[tcfg['role']['rolename']])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select local admin for zd admin to remove configuration'
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))  

    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = 'remove radius server %s ' % (tcfg['server_cfg']['server_name'])
    param_cfg = dict(auth_ser_name_list = [tcfg['server_cfg']['server_name']])
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
        testsuite_name="Monitor level Radius User privilege level test-Monitor and Admin"
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
   
    role_cfg ={"rolename": "monitor_role", 
              "specify_wlan": "", 
              "guestpass": True, 
              "description": "",
              "group_attr": "0123456789", 
              "zd_admin": "limited",}
    
#    ldap_role=dict(role_name = 'ldap_admin', 
#               allow_zd_admin = True, 
#               zd_admin_mode = 'super',
#               group_attr='ruckus')
#    
    local_user_cfg =dict(  username = 'monitor_user',
                     password = 'monitor_user',
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
                    'username': local_user_cfg['username'],
                    'password': local_user_cfg['password'],                                     
                        }
    
    radius_cfg={
                'server_name':'radius_server',
                'server_type':'radius',
                'server_addr':'192.168.0.252',
                'server_port':'1812',
                'radius_auth_secret':'1234567890',
                }
    radius_admin={'auth_method':'external',
                 'auth_server':radius_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    radius_user = 'rad.cisco.user'
    radius_password = 'rad.cisco.user'
    

    
    user_cfg =dict(  username = radius_user,
                     password = radius_password,)
        
    
    local_admin = {'auth_method':'local',
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="Monitor level Radius User privilege level test-Monitor and Admin"

    tcfg = dict(
                dest_ip= '192.168.0.252',
                role = role_cfg,
                user = user_cfg,
                dpsk_wlan=dpsk_wlan,
                gen_dpsk_para = gen_dpsk_para,
                gp_wlan=gp_wlan,
                guest_gen_para=guest_gen_para,
                server_cfg = radius_cfg,
                server_admin = radius_admin,
                local_admin = local_admin,
                local_user_cfg = local_user_cfg,
                ap_tag = active_ap,#@author: yuyanan @since:2014-8-28 optimize :parameter ap tag replace ap mac
                )
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "Monitor level Radius User privilege level test-Monitor and Admin", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
