'''
verify the privilege level of super user is correct
super user can do every thing
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
#    loc_user_cfg = tcfg['local_user_cfg']
    user_cfg = tcfg['user']
    ap_tag = tcfg['ap_tag']
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_L2_ACLs'
    common_name = 'Remove all L2 ACLs'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all roles from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_case_name=''
#    test_name = 'CB_ZD_Create_Single_Role' 
#    common_name = '%screate one operator role'%test_case_name
#    test_cfgs.append(({'role_cfg':tcfg['role']}, test_name, common_name, 0, False))
#    
    test_name = 'CB_ZD_Create_Single_Role' 
    common_name = '%screate role for edit'%test_case_name
    test_cfgs.append(({'role_cfg':tcfg['role_list'][0]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Single_Role' 
    common_name = '%screate role for delete'%test_case_name
    test_cfgs.append(({'role_cfg':tcfg['role_list'][1]}, test_name, common_name, 0, False))
#    
#    test_name = 'CB_ZD_Create_Local_User' 
#    common_name = '%screate one operator user'%test_case_name
#    test_cfgs.append((loc_user_cfg, test_name, common_name, 0, False))
#    

    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = 'create tacacs plus server via WebUI for operator user'
    test_cfgs.append(({'auth_ser_cfg_list':[tcfg['server_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a dpsk wlan,guest wlan on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[tcfg['dpsk_wlan'],tcfg['gp_wlan']],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlan_Group'
    common_name = '%sCreate a wlangroup on ZD' % (test_case_name)
    test_cfgs.append(({'wgs_cfg': tcfg['wgs_cfg1']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlan_Group'
    common_name = '%sCreate another wlangroup on ZD' % (test_case_name)
    test_cfgs.append(({'wgs_cfg': tcfg['wgs_cfg2']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = '%screate two ad server via WebUI' % (test_case_name)
    test_cfgs.append(({'auth_ser_cfg_list':tcfg['test_server_list']}, test_name, common_name, 0, False))
 
    test_name = 'CB_ZD_Create_L2_ACLs' 
    common_name = '%screate two L2 ACLs via WebUI' % (test_case_name)
    test_para = {'num_of_acl_entries':2,
                 'acl_name_list':tcfg['acl_name_list'],
                 'num_of_mac':1,
                 'target_station':tcfg['target_sta']
                 }
    test_cfgs.append((test_para, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User' 
    common_name = '%screate one local user for edit test' % (test_case_name)
    test_para = {'username':tcfg['user_list'][0],'password':tcfg['user_list'][0]}
    test_cfgs.append((test_para, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User' 
    common_name = '%screate one local user for delete test' % (test_case_name)
    test_para = {'username':tcfg['user_list'][1],'password':tcfg['user_list'][1]}
    test_cfgs.append((test_para, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Hotspot_Profiles' 
    common_name = '%screate two hotspot profile' % (test_case_name)
    test_para = {'hotspot_profiles_list':tcfg['hotspot_list']}
    test_cfgs.append((test_para, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select auth server for zd admin'
    param_cfg = dict(tcfg['server_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd web by Tacacs Plus super user' % test_case_name
    test_cfgs.append(({'login_name':user_cfg['username'],'login_pass':user_cfg['password'],'restore_zd_user':True}, test_name, common_name, 0, False))
    
    test_case_name='[change system name]'
    test_name = 'CB_ZD_Privilage_Level_Change_System_Name' 
    common_name = '%sosuper user can change system name'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[create wlan]'
    test_name = 'CB_ZD_Privilage_Level_Create_Wlan' 
    common_name = '%ssuper user can create wlan'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_name = 'CB_ZD_Remove_Wlan'
    common_name = "%sRemove new created wlan by super user"%test_case_name  
    test_cfgs.append(({'ssid':'privilage_test_wlan'}, test_name, common_name, 2, True))
    #the ssid is hardcode in lib file
    
    test_case_name='[edit wlan]'
    test_name = 'CB_ZD_Privilage_Level_Edit_Wlan' 
    common_name = '%ssuper user can edit wlan'%test_case_name
    test_cfgs.append(({'level':'super','ssid':tcfg['gp_wlan']['ssid']}, test_name, common_name, 1,False))
    
    test_name = 'CB_ZD_Remove_Wlan'
    common_name = "%sRemove edited wlan by super user"%test_case_name  
    test_cfgs.append(({'ssid':'privilage_test_edit_wlan'}, test_name, common_name, 2, True))
    #the ssid is hardcode in lib file
    
    test_case_name='[create wlan group]'
    test_name = 'CB_ZD_Privilage_Level_Create_Wlan_Grp' 
    common_name = '%ssuper user can create wlan group'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_name = 'CB_ZD_Remove_Wlan_Group'
    common_name = "%sRemove new created wlangroup"%test_case_name 
    test_cfgs.append(({'wg_name':'privilage_level_test'}, test_name, common_name, 2, True))
    
    test_case_name='[Edit wlan group]'
    test_name = 'CB_ZD_Privilage_Level_Edit_Wlan_Grp' 
    common_name = '%ssuper user can Edit wlan group'%test_case_name
    test_cfgs.append(({'level':'super','wlan_grp_name':tcfg['wgs_cfg1']['name']}, test_name, common_name, 1,False))
    
    test_name = 'CB_ZD_Remove_Wlan_Group'
    common_name = "%sRemove edited wlangroup"%test_case_name 
    test_cfgs.append(({'wg_name':tcfg['wgs_cfg1']['name']+'edit'}, test_name, common_name,2, True))
    
    test_case_name='[Delete wlan group]'
    test_name = 'CB_ZD_Privilage_Level_Delete_Wlan_Grp' 
    common_name = '%ssuper user can Delete wlan group'%test_case_name
    test_cfgs.append(({'level':'super','wlan_grp_name':tcfg['wgs_cfg2']['name']}, test_name, common_name, 1,False))
    
    #@author: yuyanan @since: 2014-8-28 bug:zf-9639 behavior change
    #test_case_name='[Set Auto Delete Expired DPSK]'
    #test_name = 'CB_ZD_Privilage_Level_Set_Auto_Delete_Expired_DPSK' 
    #common_name = '%ssuper user can set auto delete expired dpsk'%test_case_name
    #test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Generate DPSK]'
    test_name = 'CB_ZD_Privilage_Level_Generate_DPSK' 
    common_name = '%ssuper user can generate dpsk'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[delete wlan]'
    test_name = 'CB_ZD_Privilage_Level_Delete_Wlan' 
    common_name = '%ssuper user can delete wlan'%test_case_name
    test_cfgs.append(({'level':'super','ssid':tcfg['dpsk_wlan']['ssid']}, test_name, common_name, 1,False))
    
    test_case_name='[Set ZeroIT Auth Server]'
    test_name = 'CB_ZD_Privilage_Level_Set_Zero_IT_Auth_Server' 
    common_name = '%ssuper user can set Zero IT auth server'%test_case_name
    test_cfgs.append(({'level':'super','server':tcfg['test_server_list'][0]['server_name']}, test_name, common_name, 1,False))
    
    test_case_name='[Set Limited ZD Discovery]'
    test_name = 'CB_ZD_Privilage_Level_Set_Limited_ZD_Discovery' 
    common_name = '%ssuper user can set limited zd discovery'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    #@author: yuyanan @since: 2014-8-28 optimize:parameters ap tag replace ap mac
    test_case_name='[Set AP Channalization]'
    test_name = 'CB_ZD_Privilage_Level_Set_AP_Channalization' 
    common_name = '%ssuper user can set AP Channalization'%test_case_name
    test_cfgs.append(({'level':'super','ap_tag':ap_tag}, test_name, common_name, 1,False))
    
    test_case_name='[Create L2 ACL]'
    test_name = 'CB_ZD_Privilage_Level_Create_L2_ACL' 
    common_name = '%ssuper user can create L2 ACL'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Edit L2 ACL]'
    test_name = 'CB_ZD_Privilage_Level_Edit_L2_ACL' 
    common_name = '%ssuper user can edit L2 ACL'%test_case_name
    test_cfgs.append(({'level':'super','acl_name':tcfg['acl_name_list'][0]}, test_name, common_name, 1,False))
    
    test_case_name='[Remove L2 ACL]'
    test_name = 'CB_ZD_Privilage_Level_Delete_L2_ACL' 
    common_name = '%ssuper user can remove L2 ACL'%test_case_name
    test_cfgs.append(({'level':'super','acl_name':tcfg['acl_name_list'][1]}, test_name, common_name, 1,False))
    
    test_case_name='[Creat User]'
    test_name = 'CB_ZD_Privilage_Level_Create_User' 
    common_name = '%ssuper user can Create user'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Edit User]'
    test_name = 'CB_ZD_Privilage_Level_Edit_User' 
    common_name = '%ssuper user can edit user'%test_case_name
    test_cfgs.append(({'level':'super','user_name':tcfg['user_list'][0]}, test_name, common_name, 1,False))
    
    test_case_name='[Remove User]'
    test_name = 'CB_ZD_Privilage_Level_Del_User' 
    common_name = '%ssuper user can delete user'%test_case_name
    test_cfgs.append(({'level':'super','user_name':tcfg['user_list'][1]}, test_name, common_name, 1,False))
    
    test_case_name='[Create Role]'
    test_name = 'CB_ZD_Privilage_Level_Create_Role' 
    common_name = '%ssuper user can Create Role'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_name = 'CB_ZD_Remove_Roles'
    common_name = '%sremove new created role'%test_case_name
    param_cfg = dict(role_list=['role_pri_add'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
    
    test_case_name='[Edit Role]'
    test_name = 'CB_ZD_Privilage_Level_Edit_Role' 
    common_name = '%ssuper user can edit Role'%test_case_name
    test_cfgs.append(({'level':'super','role_name':tcfg['role_list'][0]['rolename']}, test_name, common_name, 1,False))
    
    test_name = 'CB_ZD_Remove_Roles'
    common_name = '%sremove all edited role'%test_case_name 
    param_cfg = dict(role_list=['role_pri_edit'])
    test_cfgs.append((param_cfg, test_name, common_name,2, True)) 
    
    test_case_name='[Remove Role]'
    test_name = 'CB_ZD_Privilage_Level_Del_Role' 
    common_name = '%ssuper user can remove Role'%test_case_name
    test_cfgs.append(({'level':'super','role_name':tcfg['role_list'][1]['rolename']}, test_name, common_name, 1,False))
    
    test_case_name='[Change Guest Pass Generate Auth Server]'
    test_name = 'CB_ZD_Privilage_Level_Select_Guest_Pass_Auth_Server' 
    common_name = '%ssuper user can not change guest pass generate auth server'%test_case_name
    test_cfgs.append(({'level':'super','server':tcfg['test_server_list'][0]['server_name']}, test_name, common_name, 1,False))
    
    test_case_name='[Create Hotspot profile]'
    test_name = 'CB_ZD_Privilage_Level_Create_Hotspot' 
    common_name = '%ssuper user can create hotspot profile'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Edit Hotspot profile]'
    test_name = 'CB_ZD_Privilage_Level_Edit_Hotspot' 
    common_name = '%ssuper user can edit hotspot profile'%test_case_name
    test_cfgs.append(({'level':'super','hotspot_name':tcfg['hotspot_list'][0]['name']}, test_name, common_name, 1,False))
    
    test_case_name='[Remove Hotspot profile]'
    test_name = 'CB_ZD_Privilage_Level_Del_Hotspot' 
    common_name = '%ssuper user can delete hotspot profile'%test_case_name
    test_cfgs.append(({'level':'super','hotspot_name':tcfg['hotspot_list'][1]['name']}, test_name, common_name, 1,False))
    
    test_case_name='[Set Rogue DHCP Detection]'
    test_name = 'CB_ZD_Privilage_Level_Set_Rogue_DHCP_Detection' 
    common_name = '%ssuper user can set rogue DHCP detection'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Set Background Scan]'
    test_name = 'CB_ZD_Privilage_Level_Set_Background_Scan' 
    common_name = '%ssuper user can set background scan'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Set Email Alarm]'
    test_name = 'CB_ZD_Privilage_Level_Set_Email_Alarm' 
    common_name = '%ssuper user can set email alarm'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Create AAA Server]'
    test_name = 'CB_ZD_Privilage_Level_Create_AAA' 
    common_name = '%ssuper user can create aaa server'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 1,False))
    
    test_case_name='[Edit AAA Server]'
    test_name = 'CB_ZD_Privilage_Level_Edit_AAA' 
    common_name = '%ssuper user can edit aaa server'%test_case_name
    test_para = {'level':'super','server_name':tcfg['test_server_list'][0]['server_name']}
    test_cfgs.append((test_para, test_name, common_name, 1,False))
    
    test_case_name='[Remove AAA Server]'
    test_name = 'CB_ZD_Privilage_Level_Del_AAA' 
    common_name = '%ssuper user can remove aaa server'%test_case_name
    test_para = {'level':'super','server_name':tcfg['test_server_list'][1]['server_name']}
    test_cfgs.append((test_para, test_name, common_name, 1,False))
    
    test_case_name=''
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd web by admin to clean configuration' % test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'set zd auth with local admin'
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0,True))  
    
    test_name = 'CB_ZD_GuestPassGen_Select_Auth_Server'
    common_name = 'Select guest pass generation authentication server to Local Database'
    test_cfgs.append(({'guestpassgen_auth_serv':'Local Database'}, test_name, common_name, 0, False))    
 
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    common_name = 'Select Zeroit authentication server to Local Database'
    test_cfgs.append(({'zero_it_auth_serv': 'Local Database'}, test_name, common_name, 0, False))    
       
#
#    test_name = 'CB_ZD_Remove_Wlan'
#    common_name = "Remove guest pass wlan"  
#    test_cfgs.append(({'ssid': tcfg['gp_wlan']['ssid']}, test_name, common_name, 0, True))
#    
#    test_name = 'CB_ZD_Remove_Wlan'
#    common_name = "Remove dpsk pass wlan"  
#    test_cfgs.append(({'ssid': tcfg['dpsk_wlan']['ssid']}, test_name, common_name, 0, True))
#    

#zj 2014-0326 fix ZF-7545
#    test_name = 'CB_ZD_Remove_Local_User'
#    common_name = 'remove the new created user'
#    param_cfg = {'username':tcfg['user']['username']}
#    test_cfgs.append((param_cfg, test_name, common_name, 0,True))  
   
    test_name = 'CB_ZD_Remove_All_Users' 
    common_name = '%sremove all local users' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 0, True))
  
    test_name = 'CB_ZD_Remove_Roles'
    common_name = 'remove all new created role' 
    param_cfg = dict(role_list=[tcfg['role']['rolename']])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_All_L2_ACLs' 
    common_name = '%sremove all L2 acls' % (test_case_name)
    test_cfgs.append(({'remove_wlan':False}, test_name, common_name, 0, True))
 
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles' 
    common_name = '%sremove all hotspot profiles' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Authentication_Server' 
    common_name = '%sremove all aaa servers' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
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
        testsuite_name="Super level Tacacs Plus User privilege level test-Configure"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an AP to do set channlization: ")
            if active_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % active_ap
            
            else:
                active_ap_mac=ap_sym_dict[active_ap]['mac']
                print('active_ap_mac is %s'% active_ap_mac)
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
    role_cfg1 ={"rolename": "role_pri_test1", 
              "specify_wlan": "", 
              "guestpass": True, 
              "description": "",
              "group_attr": "", 
              "zd_admin": "operation"}
    role_cfg2 ={"rolename": "role_pri_test2", 
              "specify_wlan": "", 
              "guestpass": True, 
              "description": "",
              "group_attr": "", 
              "zd_admin": "operation"}
    
    loc_user_cfg =dict(  username = 'super_user',
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
    
    gp_wlan = {'ssid': 'wlan-guestpass',
                      'type': 'guest', 
                      'auth': 'open',
                      'encryption' : 'none',                
                      }
    
    wlangroup_cfg1 = dict(
        name = 'wg_privilage_test',
        description = 'wg_privilage_test',
        wlan_member = [],
        vlan_override = False,
    )
    wlangroup_cfg2 = dict(
        name = 'wg_privilage_test_2',
        description = 'wg_privilage_test',
        wlan_member = [],
        vlan_override = False,
    )
    
    ad_cfg1={
            'server_name':'ad_server1',
            'server_type':'ad',
            'server_addr':'192.168.0.250',
            'server_port':'389',
            'win_domain_name':'rat.ruckuswireless.com',
            }
    
    ad_cfg2={
            'server_name':'ad_server2',
            'server_type':'ad',
            'server_addr':'192.168.0.250',
            'server_port':'389',
            'win_domain_name':'rat.ruckuswireless.com',
            }
    
    test_server_list = [ad_cfg1,ad_cfg2]
    
    hotspot_cfg1 = {'name':'hotspot_1_privilagr_test',
                     'login_page':'http://192.168.0.252'}
    hotspot_cfg2 = {'name':'hotspot_2_privilagr_test',
                     'login_page':'http://192.168.0.252'}
    
    hotspot_list = [hotspot_cfg1,hotspot_cfg2]
    
    server_ip_addr = '192.168.0.250'
    super_cfg={
               'server_name':'super_user_server',
               'server_type':'tacacs_plus',
               'server_addr':server_ip_addr,
               'server_port':'49',
               'tacacs_auth_secret':'ruckus',
               'tacacs_service':'ap-login'
               }
    super_user='test1'
    super_password='lab4man1'
    super_admin={'auth_method':'external',
                 'auth_server':super_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    user_cfg =dict(  username = super_user,
                     password = super_password,)
        
    
    local_admin = {'auth_method':'local',
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="Super level Tacacs Plus User privilege level test-Configure"

    tcfg = dict(
                ap_mac = active_ap_mac,
                target_sta = target_sta,
                dest_ip= '192.168.0.252',
                role = role_cfg,
                loc_user = loc_user_cfg,
                dpsk_wlan=dpsk_wlan,
#                gen_dpsk_para = gen_dpsk_para,
                gp_wlan=gp_wlan,
#                guest_gen_para=guest_gen_para,
                wgs_cfg1 = wlangroup_cfg1,
                wgs_cfg2 = wlangroup_cfg2,
                test_server_list = test_server_list,
                acl_name_list=['acl_privilage_1','acl_privilage_2'],
                user_list = ['user_pri_test1','user_pri_test2'],
                role_list = [role_cfg1,role_cfg2],
                hotspot_list = hotspot_list,
                server_cfg = super_cfg,
                server_admin = super_admin,
                local_admin = local_admin,
                local_user_cfg = loc_user_cfg,
                user = user_cfg,
                ap_tag = active_ap,#@author:yuyanan @since:2014-8-28 optimize:ap mac from ap tag
                )
    
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "Super level Tacacs Plus User privilege level test-Configure", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
