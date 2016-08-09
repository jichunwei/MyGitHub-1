'''
tacacs plus admin conbination with mgmt acl/mgmt if/session timeout/
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = [] 
    
    test_name = 'CB_ZD_Add_Mgmt_Acl' 
    common_name = 'Add Management ACL from web UI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mgmt_Interface'
    common_name = 'Enable Management Interface from web UI'
    test_cfgs.append(({'ip_addr':'192.168.0.5','vlan':1},test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = 'create tacacs plus server via WebUI'
    test_cfgs.append(({'auth_ser_cfg_list':[tcfg['tacplus_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select auth server for zd admin'
    param_cfg = dict(tcfg['tacaplus_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  

    test_case_name='[Management ACL]'
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by monitor user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['monitor_user'],'login_pass':tcfg['monitor_password'],'restore_zd_user':True}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be monitor after user log in'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by operator user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be operator after user log in'%test_case_name
    test_cfgs.append(({'level':'operator'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by super user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be super after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_case_name='[Management IF]'
    test_name = 'CB_ZD_Access_ZD_Web_And_Cli_Through_Mgmt_If' 
    common_name = '%slogin zd web from mgmt IF' % test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','web':True,'cli':False,}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by monitor user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['monitor_user'],'login_pass':tcfg['monitor_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be monitor after user log in'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by operator user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be operator after user log in'%test_case_name
    test_cfgs.append(({'level':'operator'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by super user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be super after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_ZD_Access_IP' 
    common_name = '%slogin zd web from zd real ip' % test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','web':True,'cli':False,}, test_name, common_name, 2, True))
    
    test_case_name='[session timeout]'
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd web by super user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Adimn_Auto_Logout' 
    common_name = '%ssuper user should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd web by monitor user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['monitor_user'],'login_pass':tcfg['monitor_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Adimn_Auto_Logout' 
    common_name = '%smonitor user should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({'set_first':False}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd web by operator user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Adimn_Auto_Logout' 
    common_name = '%soperator usershould not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({'set_first':False}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = 'login zd web by local admin to restore configuration'
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 0, True))
    
    test_case_name='[tacacs+ server configuration test]'
    test_name = 'CB_ZD_Tacacs_Plus_Server_Configuration_Test' 
    common_name = '%stacacs plus server configuration test'%test_case_name
    test_cfgs.append(({'server':tcfg['tacplus_cfg']['server_name']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'set zd auth with local admin'
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))  

    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = 'remove tacacs server %s after all test' % (tcfg['tacplus_cfg']['server_name'])
    param_cfg = dict(auth_ser_name_list = [tcfg['tacplus_cfg']['server_name']])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_Mgmt_Acl' 
    common_name = 'remove Management ACL from web UI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Disable_Mgmt_Interface'
    common_name = 'disable Management Interface from web UI'
    test_cfgs.append(({},test_name, common_name, 0, True))    
    
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
        testsuite_name="TACACS PLUS Authentication and Authorization combin with other feature"
    )
    attrs.update(kwargs)
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="TACACS PLUS Authentication and Authorization combin with other feature"
    server_ip_addr = '192.168.0.250'
    tacplus_cfg={
               'server_name':'super_user_server',
               'server_type':'tacacs_plus',
               'server_addr':server_ip_addr,
               'server_port':'49',
               'tacacs_auth_secret':'ruckus',
               'tacacs_service':'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12'
               }
    super_user='test5'
    super_password='lab4man1'
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
    monitor_user='test3'
    monitor_password='lab4man1'
    no_level_user='test4'
    no_level_password='lab4man1'
    local_admin = {'auth_method':'local',
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    tcfg = dict(tacplus_cfg=tacplus_cfg,
                super_user=super_user,
                super_password=super_password,
                tacaplus_admin=tacaplus_admin,
                operator_user=operator_user,
                operator_password=operator_password,
                monitor_user=monitor_user,
                monitor_password=monitor_password,
                no_level_user=no_level_user,
                no_level_password=no_level_password,
                local_admin=local_admin,
                )
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "TACACS PLUS Authentication and Authorization combin with other feature", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
