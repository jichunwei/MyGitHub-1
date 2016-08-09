'''
tacacs plus admin basic function
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = [] 
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment' 
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'both ZD enable SR and ready to do test' 
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_Create_Authentication_Server' 
    common_name = 'create tacacs plus server via WebUI'
    test_cfgs.append(({'auth_ser_cfg_list':[tcfg['super_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select tacacs plus server for zd admin'
    param_cfg = dict(tcfg['super_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  

    test_case_name='[login active/standby zd by user in tacacs plus server]'
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify active zd web can be logged in by user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True,'zd':'active'}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify standby zd web can be logged in by user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True,'zd':'standby'}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%scheck the privilege level after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_case_name='[login active/standby zd after failover]'
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%sFailover active ZD' % (test_case_name)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify active zd web can be logged in by user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True,'zd':'active'}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '%sverify standby zd web can be logged in by user in tacacs server'%test_case_name
    test_cfgs.append(({'login_name':tcfg['super_user'],'login_pass':tcfg['super_password'],'restore_zd_user':True,'zd':'standby'}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Privilege_Level' 
    common_name = '%scheck the privilege level after user log in'%test_case_name
    test_cfgs.append(({'level':'super'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select auth server for zd admin'
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))  

    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = 'remove tacacs server %s after all test' % (tcfg['super_cfg']['server_name'])
    param_cfg = dict(auth_ser_name_list = [tcfg['super_cfg']['server_name']])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD'
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
        testsuite_name="TACACS PLUS Authentication and Authorization SR"
    )
    attrs.update(kwargs)
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="TACACS PLUS Authentication and Authorization SR"
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
                local_admin=local_admin,
                )
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "TACACS PLUS Authentication and Authorization SR", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
