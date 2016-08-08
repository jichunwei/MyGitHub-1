'''
tacacs plus admin basic function
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as constant


def define_test_configuration(tcfg):
    test_cfgs = [] 
    
    test_name = 'CB_ZD_Clear_Event' 
    common_name = 'clear zd all event before test begin'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = 'create super user tacacs plus server via WebUI'
    test_cfgs.append(({'auth_ser_cfg_list':[tcfg['super_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = 'check create server event log'
    test_cfgs.append(({'event':'MSG_AUTHSVR_created','server_name':tcfg['super_cfg']['server_name']}, test_name, common_name, 0, False))

    #Case 1
    test_case_name='[super level]'        
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect auth server[super_admin] for zd admin' % test_case_name
    param_cfg = dict(tcfg['super_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can not be logged in by local admin'%test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','expected_fail':True,'restore_zd_user':True}, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = '%scheck log in event log'%test_case_name
    test_cfgs.append(({'event':'MSG_admin_login','user':tcfg['super_user']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = '%scheck log in fail event log'%test_case_name
    test_cfgs.append(({'event':'MSG_admin_login_failed','user':'admin'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%scheck the privilege level after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Clear_Event' 
    common_name = '%sclear zd all events'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select local admin for zd admin' 
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))  
    
    test_name = 'CB_ZD_Update_Authentication_Server' 
    common_name = 'modify tacacs plus server according to operator configuration via WebUI'
    test_cfgs.append(({'old_name':tcfg['super_cfg']['server_name'],'auth_ser_cfg':tcfg['operator_cfg']}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = 'check modify server event log'
    test_cfgs.append(({'event':'MSG_AUTHSVR_modified','server_name':tcfg['operator_cfg']['server_name']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select auth server[operator_admin] for zd admin'
    param_cfg = dict(tcfg['operator_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  

    #Case 2
    test_case_name='[operator level]' 
 
    test_name = 'CB_ZD_Clear_Event' 
    common_name = '%sclear zd all events'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['operator_user'],'login_pass':tcfg['operator_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = '%scheck log out event log'%test_case_name
    test_cfgs.append(({'event':'MSG_admin_logout','user':tcfg['super_user']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%scheck the privilege level after user log in'%test_case_name
    test_cfgs.append(({'level':'operator'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = 'login zd with local admin to config server'
    test_cfgs.append(({'login_name':'admin','login_pass':'admin','restore_zd_user':True}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Clear_Event' 
    common_name = 'clear zd all events after operator level test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Update_Authentication_Server' 
    common_name = 'modify tacacs plus server according to monitor configuration via WebUI'
    test_cfgs.append(({'old_name':tcfg['operator_cfg']['server_name'],'auth_ser_cfg':tcfg['monitor_cfg']}, 
                      test_name, common_name, 0, False))

    #Case 3
    test_case_name='[monitor level]'

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['monitor_user'],'login_pass':tcfg['monitor_password'],'restore_zd_user':True}, 
                      test_name, common_name, 1, False))

    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%scheck the privilege level after user log in'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 2, False))
    
    #Case 4
    test_case_name='[authorization failed]'
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slog in zd by user whoes service name not the same with configuration'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be monitor level'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 2, False))
    
    #Case 5
    test_case_name='[no level specified]'

    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slog in zd by user whoes service name not the same with configuration'%test_case_name
    test_cfgs.append(({'login_name':tcfg['no_level_user'],'login_pass':tcfg['no_level_password'],'restore_zd_user':True}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be monitor level'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 2, False))
    
    #Case 6
    test_case_name='[reboot zd]'
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd with local admin user'%test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Reboot' 
    common_name = '%sreboot zd' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify zd web can be logged in by monitor user after reboot'%test_case_name
    test_cfgs.append(({'login_name':tcfg['monitor_user'],'login_pass':tcfg['monitor_password'],'restore_zd_user':True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level should be monitor level'%test_case_name
    test_cfgs.append(({'level':'monitor'}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = 'login zd with local admin user to configure server'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = 'create unreachable tacacs plus server via WebUI'
    test_cfgs.append(({'auth_ser_cfg_list':[tcfg['unreachable_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select unreachable server[unreachable_admin] for zd admin'
    param_cfg = dict(tcfg['unreachable_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  

    #Case 7
    test_case_name='[server unreachable]'    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%slogin zd with local admin user'%test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%sthe privilege level of local admin should be super level'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    #Case 8
    test_case_name='[backup-restore]'
    test_name = 'CB_ZD_Backup' 
    common_name = '%sbackup configure file with tacacs plus server' %test_case_name
    test_cfgs.append(({'save_to':constant.save_to}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect local zdmin server for zd admin'%test_case_name
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Clear_Event' 
    common_name = '%sclear zd all event'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = '%sremove tacacs server %s and %s for full mode restore' % (test_case_name,tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name'])
    param_cfg = dict(auth_ser_name_list = [tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name']])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = '%scheck remove server event log'%test_case_name
    test_cfgs.append(({'event':'MSG_AUTHSVR_deleted','server_name':tcfg['unreachable_cfg']['server_name']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Restore' 
    common_name = '%srestore configure file by full mode' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Auth_Server_Info'
    common_name = '%sverify tacacs plus server is restored by full mode'%test_case_name
    param_cfg = {tcfg['monitor_cfg']['server_name']:'TACPLUS Authenticating',
                tcfg['unreachable_cfg']['server_name']:'TACPLUS Authenticating'
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_AAA_Configuration'
    common_name = '%sverify tacacs plus server configuration is restored by full mode'%test_case_name
    param_cfg = {tcfg['monitor_cfg']['server_name']:tcfg['monitor_cfg'],
                tcfg['unreachable_cfg']['server_name']:tcfg['unreachable_cfg']
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_Admin_Info'
    common_name = '%sverify admin info is restored by full mode' % (test_case_name)
    param_cfg = dict(tcfg['unreachable_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect local zdmin server for zd admin after full restore'%test_case_name
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = '%sremove tacacs server %s and %s for failover mode restore' % (test_case_name,tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name'])
    param_cfg = dict(auth_ser_name_list = [tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name']])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Restore' 
    common_name = '%srestore configure file by failover mode' % test_case_name
    test_cfgs.append(({'restore_type':'restore_everything_except_ip'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Auth_Server_Info'
    common_name = '%sverify tacacs plus server is restored by failover mode'%test_case_name
    param_cfg = {tcfg['monitor_cfg']['server_name']:'TACPLUS Authenticating',
                tcfg['unreachable_cfg']['server_name']:'TACPLUS Authenticating'
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_AAA_Configuration'
    common_name = '%sverify tacacs plus server configuration is restored by failover mode'%test_case_name
    param_cfg = {tcfg['monitor_cfg']['server_name']:tcfg['monitor_cfg'],
                tcfg['unreachable_cfg']['server_name']:tcfg['unreachable_cfg']
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_Admin_Info'
    common_name = '%sverify admin info is not by failover mode' % (test_case_name)
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = '%sremove tacacs server %s and %s for policy mode restore' % (test_case_name,tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name'])
    param_cfg = dict(auth_ser_name_list = [tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name']])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Restore' 
    common_name = '%srestore configure file by policy mode' % test_case_name
    test_cfgs.append(({'restore_type':'restore_basic_config'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Auth_Server_Info'
    common_name = '%sverify tacacs plus server is restored by policy mode'%test_case_name
    param_cfg = {tcfg['monitor_cfg']['server_name']:'TACPLUS Authenticating',
                tcfg['unreachable_cfg']['server_name']:'TACPLUS Authenticating'
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_AAA_Configuration'
    common_name = '%sverify tacacs plus server configuration is restored by policy mode'%test_case_name
    param_cfg = {tcfg['monitor_cfg']['server_name']:tcfg['monitor_cfg'],
                tcfg['unreachable_cfg']['server_name']:tcfg['unreachable_cfg']
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_Admin_Info'
    common_name = '%sverify admin info is not by policy mode' % (test_case_name)
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    #Case 9
    test_case_name='[Test Authentication Settings]'
    test_name = 'CB_ZD_Test_Authentication_Settings'
    common_name = '%sverify test authentication settings function work well' % (test_case_name)
    param_cfg = {'invalid_username':'monkey',
                 'invalid_password':'dog',
                 'server_name':tcfg['monitor_cfg']['server_name'],
                 'server_type':'tacacs_plus',
                 'user_name':tcfg['monitor_user'],
                 'password':tcfg['monitor_password'],
                 'unreachable_server_name':tcfg['unreachable_cfg']['server_name'],
                 'unreachable_server_type':'tacacs_plus',
                 'unreachable_user_name':tcfg['monitor_user'],
                 'unreachable_password':tcfg['monitor_user'],
                }
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
    
    #Case 10
    test_case_name='[Only for admin auth]'
    test_name = 'CB_ZD_Verify_Server_Only_For_Admin_Auth'
    common_name = '%sverify tacacs+ server only for admin authentication and authorization' % (test_case_name)
    param_cfg = {'server_list':[tcfg['monitor_cfg']['server_name'],tcfg['unreachable_cfg']['server_name']]
                }
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select local admin for zd admin to remove configuration'
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))  

    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = 'remove tacacs server %s and %s after all test' % (tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name'])
    param_cfg = dict(auth_ser_name_list = [tcfg['unreachable_cfg']['server_name'],tcfg['monitor_cfg']['server_name']])
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
        testsuite_name="TACACS PLUS Authentication and Authorization Basic"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="TACACS PLUS Authentication and Authorization Basic"
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
                 'fallback_local':False,
                 }
    
    operator_cfg={
               'server_name':'operator_user_server',
               'server_type':'tacacs_plus',
               'server_addr':server_ip_addr,
               'server_port':'49',
               'tacacs_auth_secret':'ruckus',
               'tacacs_service':'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12'
               }
    operator_user='test2'
    operator_password='lab4man1'
    operator_admin={'auth_method':'external',
                 'auth_server':operator_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    monitor_cfg={
               'server_name':'monitor_user_server',
               'server_type':'tacacs_plus',
               'server_addr':server_ip_addr,
               'server_port':'49',
               'tacacs_auth_secret':'ruckus',
               'tacacs_service':'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12'
               }
    monitor_user='test3'
    monitor_password='lab4man1'
    monitor_admin={'auth_method':'external',
                 'auth_server':monitor_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    no_level_user='test4'
    no_level_password='lab4man1'
    
    
    unreachable_cfg={
               'server_name':'unreachable_server',
               'server_type':'tacacs_plus',
               'server_addr':'172.19.123.123',
               'server_port':'49',
               'tacacs_auth_secret':'ruckus',
               'tacacs_service':'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12'
               }
    unreachable_user='admin'
    unreachable_password='admin'
    unreachable_admin={'auth_method':'external',
                 'auth_server':unreachable_cfg['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    local_admin = {'auth_method':'local',
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin'
                 }
    
    tcfg = dict(super_cfg=super_cfg,
                super_user=super_user,
                super_password=super_password,
                super_admin=super_admin,
                operator_cfg=operator_cfg,
                operator_user=operator_user,
                operator_password=operator_password,
                operator_admin=operator_admin,
                monitor_cfg=monitor_cfg,
                monitor_user=monitor_user,
                monitor_password=monitor_password,
                monitor_admin=monitor_admin,
                no_level_user=no_level_user,
                no_level_password=no_level_password,
                unreachable_cfg=unreachable_cfg,
                unreachable_user=unreachable_user,
                unreachable_password=unreachable_password,
                unreachable_admin=unreachable_admin,
                local_admin=local_admin,
                )
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "TACACS PLUS Authentication and Authorization Basic", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
