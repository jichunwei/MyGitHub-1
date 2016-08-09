'''
tacacs plus admin combination with radius/ad/ldap authentication
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = [] 
    
    test_name = 'CB_ZD_CLI_Configure_Roles' 
    common_name = 'Add two roles for user in ldap/radius/ad/local server admin zd'
    test_cfgs.append(({'role_cfg_list':tcfg['role_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'create one local user'
    test_cfgs.append((tcfg['loc_user_cfg'],test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = 'create tacacs plus/ad/radius/ldap server via WebUI'
    test_cfgs.append(({'auth_ser_cfg_list':tcfg['auth_ser_cfg_list']}, test_name, common_name, 0, False))
 
    test_case_name='[combined with local user]'   
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect tacaca plus auth server for zd admin'%test_case_name
    param_cfg = dict(tcfg['tacaplus_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by operator user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be operator after user log in'%test_case_name
    test_cfgs.append(({'level':'operator'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by local user in zd'%test_case_name
    test_cfgs.append(({'login_name':tcfg['loc_user'],'login_pass':tcfg['loc_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be super after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_case_name='[combined with ad server]'  
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd by local admin to select tacacs plus server'%test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 1, False))
         
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect tacaca plus auth server for zd admin'%test_case_name
    param_cfg = dict(tcfg['tacaplus_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by operator user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be operator after user log in'%test_case_name
    test_cfgs.append(({'level':'operator'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd by local admin to select auth server'%test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect ad auth server for zd admin'%test_case_name
    param_cfg = dict(tcfg['ad_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by ad user in zd'%test_case_name
    test_cfgs.append(({'login_name':tcfg['ad_user'],'login_pass':tcfg['ad_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be super after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_case_name='[combined with radius server]'    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd by local admin to select tacacs plus server'%test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 1, False))
         
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect tacaca plus auth server for zd admin'%test_case_name
    param_cfg = dict(tcfg['tacaplus_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by operator user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be operator after user log in'%test_case_name
    test_cfgs.append(({'level':'operator'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd by local admin to select auth server'%test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect radius auth server for zd admin'%test_case_name
    param_cfg = dict(tcfg['radius_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by ad user in zd'%test_case_name
    test_cfgs.append(({'login_name':tcfg['radius_user'],'login_pass':tcfg['radius_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be super after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_case_name='[combined with ldap server]'  
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd by local admin to select tacacs plus server'%test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 1, False))
          
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect tacaca plus auth server for zd admin'%test_case_name
    param_cfg = dict(tcfg['tacaplus_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by operator user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be operator after user log in'%test_case_name
    test_cfgs.append(({'level':'operator'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd by local admin to select auth server'%test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect ldap auth server for zd admin'%test_case_name
    param_cfg = dict(tcfg['ldap_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by ad user in zd'%test_case_name
    test_cfgs.append(({'login_name':tcfg['ldap_user'],'login_pass':tcfg['ldap_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be super after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = 'login zd by local admin to clean config'
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 0,True))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'set zd auth with local admin'
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0,True))  
    
    test_name = 'CB_ZD_Remove_Local_User'
    common_name = 'remove the new created user'
    param_cfg = {'username':tcfg['loc_user']}
    test_cfgs.append((param_cfg, test_name, common_name, 0,True))  
    
    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = 'remove all new created auth servers after all test' 
    param_cfg = dict(auth_ser_name_list = tcfg['auth_ser_name_list'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_Roles'
    common_name = 'remove all new created roles after all test' 
    param_cfg = dict(role_list=tcfg['rolename_list'])
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
        testsuite_name="TACACS PLUS Authentication and Authorization combin with other server"
    )
    attrs.update(kwargs)
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="TACACS PLUS Authentication and Authorization combin with other server"
    ldap_role=dict(role_name = 'ldap_admin', 
                   allow_zd_admin = True, 
                   zd_admin_mode = 'super',
                   group_attr='ruckus')
    other_server_role=dict(role_name = 'zd_admin', 
                   allow_zd_admin = True, 
                   zd_admin_mode = 'super',
                   group_attr='0123456789')
    
    role_list=[ldap_role,other_server_role]
    rolename_list=[ldap_role['role_name'],other_server_role['role_name']]
    
    
    tacaplus_server_ip_addr = '192.168.0.250'
    tacplus_cfg={
               'server_name':'tacaplus',
               'server_type':'tacacs_plus',
               'server_addr':tacaplus_server_ip_addr,
               'server_port':'49',
               'tacacs_auth_secret':'ruckus',
               'tacacs_service':'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12'
               }
    tacaplus_admin={'auth_method':'external',
                 'auth_server':tacplus_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    operator_user='test2'
    operator_password='lab4man1'
    local_admin = {'auth_method':'local',
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    ldap_cfg={
                'server_name':'ldap_server',
                'server_type':'ldap',
                'server_addr':'192.168.0.252',
                'server_port':'389',
                'ldap_search_base':'dc=example,dc=net',
                'ldap_admin_dn':'cn=Manager,dc=example,dc=net',
                'ldap_admin_pwd':'lab4man1',
                }
    ldap_admin={'auth_method':'external',
                 'auth_server':ldap_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    ad_cfg={
                'server_name':'ad_server',
                'server_type':'ad',
                'server_addr':'192.168.0.250',
                'server_port':'389',
                'win_domain_name':'rat.ruckuswireless.com',
                }
    ad_admin={'auth_method':'external',
                 'auth_server':ad_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
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
    ad_user = 'ad.user'
    ad_password= 'ad.user'
    radius_user = 'rad.cisco.user'
    radius_password = 'rad.cisco.user'
    ldap_user = 'test.ldap.user'
    ldap_password = 'test.ldap.user'
    
    loc_user_cfg=dict(username = 'loc_admin_user',
                      password = 'loc_admin_user',
                      fullname = '',
                      role = other_server_role['role_name'],)
    
    tcfg = dict(tacplus_cfg=tacplus_cfg,
                tacaplus_admin=tacaplus_admin,
                operator_user=operator_user,
                operator_password=operator_password,
                local_admin=local_admin,
                role_list=role_list,
                ldap_cfg=ldap_cfg,
                ldap_admin=ldap_admin,
                ad_cfg=ad_cfg,
                ad_admin=ad_admin,
                radius_cfg=radius_cfg,
                radius_admin=radius_admin,
                ad_user = ad_user,
                ad_password=ad_password,
                radius_user = radius_user,
                radius_password = radius_password,
                ldap_user = ldap_user,
                ldap_password = ldap_password,
                loc_user_cfg=loc_user_cfg,
                loc_user = loc_user_cfg['username'],
                loc_password = loc_user_cfg['password'],
                auth_ser_cfg_list=[tacplus_cfg,ldap_cfg,radius_cfg,ad_cfg],
                auth_ser_name_list = [tacplus_cfg['server_name'],ldap_cfg['server_name'],radius_cfg['server_name'],ad_cfg['server_name']],
                rolename_list=rolename_list,
                )
    
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "TACACS PLUS Authentication and Authorization combin with other server", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
