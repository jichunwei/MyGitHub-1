'''
tacacs plus server cli test
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
    
    test_name = 'CB_ZD_Clear_Event' 
    common_name = 'clear zd all event through Web'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Config_AAA_Server' 
    common_name = 'create tacacs plus server via CLI'
    test_cfgs.append((tcfg['tacplus_cfg'], test_name, common_name, 0, False))
    
    test_case_name='[Create Tacacs Plus Server]'
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = '%scheck create server event log'%test_case_name
    test_cfgs.append(({'event':'MSG_AUTHSVR_created','server_name':tcfg['tacplus_cfg']['server_name'],'te_addr':'Local Host'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AAA_Configuration'
    common_name = '%sverify tacacs plus server configuration in web UI'%test_case_name
    param_cfg = {tcfg['tacplus_cfg']['server_name']:tcfg['tacplus_cfg']
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Clear_Event' 
    common_name = '%sclear zd all event through Web'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZDCLI_Config_AAA_Server' 
    common_name = 'modify tacacs plus server via CLI'
    test_cfgs.append((tcfg['tacplus_cfg2'], test_name, common_name, 0, False))
    
    test_case_name='[Modify Tacacs Plus Server]'
    
    test_name = 'CB_ZD_Check_Event' 
    common_name = '%scheck create server event log'%test_case_name
    test_cfgs.append(({'event':'MSG_AUTHSVR_modified','server_name':tcfg['tacplus_cfg2']['server_name'],'te_addr':'Local Host'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AAA_Configuration'
    common_name = '%sverify tacacs plus server configuration in web UI'%test_case_name
    param_cfg = {tcfg['tacplus_cfg2']['server_name']:tcfg['tacplus_cfg2']
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'select auth server for zd admin,not fallback'
    param_cfg = dict(tcfg['tacaplus_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  

    test_case_name='[Telnet Login And Auto Logout]'
    test_name = 'CB_ZD_Open_Telnet_Server'
    common_name = '%sopen telnet server in zd' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZDCLI_Admin_Auto_Logout'
    common_name = '%stelnet login by tacacs plus server operator user and auto logout ' % test_case_name
    test_cfgs.append(({'telnet_check':True,'username':tcfg['operator_user'],'password':tcfg['operator_password']},test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Close_Telnet_Server'
    common_name = '%sclose telnet server in zd' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, True)) 
    
    test_case_name='[SSH Login And Auto Logout]'
    test_name = 'CB_ZDCLI_Admin_Auto_Logout'
    common_name = '%sSSH CLI login mgmt if by super in tacacs plus server,no fallback and auto logout test' % test_case_name
    param_cfg ={'logout_first':True,'username':tcfg['super_user'],'password':tcfg['super_password'],'ip':'192.168.0.5','relogin':True}
    test_cfgs.append((param_cfg,test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = '%sselect auth server for zd admin,with fallback'%test_case_name
    param_cfg = dict(tcfg['tacaplus_admin2'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  

    test_name = 'CB_ZDCLI_Admin_Auto_Logout'
    common_name = '%sSSH CLI login physical ip by monitor user in tacacs plus server and auto logout test' % test_case_name
    param_cfg ={'logout_first':False,'username':tcfg['monitor_user'],'password':tcfg['monitor_password']}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))  
    
    test_case_name='[tacacs plus configuration]'
    test_name = 'CB_ZDCLI_Config_AAA_Server' 
    common_name = 'edit tacacs plus server by not invalid via CLI'
    test_cfgs.append((tcfg['tacplus_cfg3'], test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AAA_Configuration'
    common_name = '%sverify tacacs plus server configuration in web UI'%test_case_name
    param_cfg = {tcfg['tacplus_cfg2']['server_name']:tcfg['tacplus_cfg2']
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Cfg_Admin_Info'
    common_name = 'set zd auth with local admin'
    param_cfg = dict(tcfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))  

    test_name = 'CB_ZD_Clear_Event' 
    common_name = 'clear zd all event through Web before remove tacacs plus server'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZDCLI_Remove_AAA_Server'
    common_name = 'remove tacacs server %s after all test' % (tcfg['tacplus_cfg']['server_name'])
    test_cfgs.append(({'name':tcfg['tacplus_cfg2']['server_name']}, test_name, common_name, 0, True)) 
    
    test_case_name='[remove tacacs plus server]'
    test_name = 'CB_ZD_Check_Event' 
    common_name = '%scheck create server event log'%test_case_name
    test_cfgs.append(({'event':'MSG_AUTHSVR_deleted','server_name':tcfg['tacplus_cfg2']['server_name'],'te_addr':'Local Host'}, test_name, common_name, 1, False))
    
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
        testsuite_name="TACACS PLUS Authentication and Authorization CLI"
    )
    attrs.update(kwargs)
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="TACACS PLUS Authentication and Authorization CLI"
    server_ip_addr = '192.168.0.250'
    tacplus_cfg={
               'server_name':'tacplus_server_cli_1',
               'server_type':'tacacs_plus',
               'server_addr':server_ip_addr,
               'server_port':'490',
               'tacacs_auth_secret':'ruckus2',
               'tacacs_service':'abcdefghijklmnopqrstuvwx121234567890abcdefghijklmnopqrstuvwxyz12'
               }
    
    tacplus_cfg2={
                  'name':'tacplus_server_cli_1',
                  'server_name':'tacplus_server_cli',
                  'server_type':'tacacs_plus',
                  'server_addr':server_ip_addr,
                  'server_port':'49',
                  'tacacs_auth_secret':'ruckus',
                  'tacacs_service':'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12'
                  }
    
    
    tacplus_cfg3={
                  'server_name':'tacplus_server_cli',
                  'server_type':'tacacs_plus',
                  'server_addr':'255.255.255.255',
                  'server_port':'65536',#@ZJ 20140916 ZF-10063
                  'tacacs_auth_secret':'',
                  'tacacs_service':''
                  }
    
    super_user='test5'
    super_password='lab4man1'
    tacaplus_admin={'auth_method':'external',
                 'auth_server':tacplus_cfg2['server_name'],
                 'fallback_local':False,
                 }
    
    tacaplus_admin2={'auth_method':'external',
                 'auth_server':tacplus_cfg2['server_name'],
                 'fallback_local':True,
                 'admin_name':'admin',
                 'admin_old_pass':'admin',
                 'admin_pass1':'admin',
                 'admin_pass2':'admin',
                 'login_info':{'re_login':True, 'username':'test5','password':'lab4man1'}
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
                tacplus_cfg2=tacplus_cfg2,
                tacplus_cfg3=tacplus_cfg3,
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
                tacaplus_admin2=tacaplus_admin2,
                )
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
#    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "TACACS PLUS Authentication and Authorization CLI", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
