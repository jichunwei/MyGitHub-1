'''
create @2011/12/19, by west.li@ruckuswireless.com
1.    one random number between 1 to 1440 set from web UI(3.1.1,3.1.3)
2.    verify the session timeout value from ZDCLI (3.1.4)
3.    one random number between 1 to 1440 set from ZDCLI(3.1.2,3.1.3)
4.    verify the session timeout value from web UI (3.1.4)
5.    set 1,1440/0,1441 from web UI,1,1440 will be set successfully and 0,1441 will fail(3.1.3)
6.    set 1,1440/0,1441 from ZDCLI, 1,1440 will be set successfully and 0,1441 will fail(3.1.3)
7.    reboot the ZD and verify the session time out configuration(3.1.5)
8.    restore ZD to factory configuration, check the session timeout value is 30 minutes(3.2.1)
'''


import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

def defineTestConfiguration(mgmt_if,vlan_id,zd_ip):
    test_cfgs = [] 
    test_name = 'CB_ZD_Add_Mgmt_Acl' 
    common_name = 'Add Management ACL from web UI' 
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mgmt_Interface'
    common_name = 'Enable Management Interface from web UI'
    test_cfgs.append(({'ip_addr':mgmt_if,'vlan':vlan_id},test_name, common_name, 0, False))    
    
    test_case_name='SSH CLI admin Auto logout test'
    test_name = 'CB_ZDCLI_Admin_Auto_Logout'
    common_name = '[%s]SSH CLI should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))    
    
    test_case_name='Telnet CLI admin Auto logout test'
    test_name = 'CB_ZD_Open_Telnet_Server'
    common_name = '[%s]open telnet server in zd' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZDCLI_Admin_Auto_Logout'
    common_name = '[%s]Telnet CLI should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({'telnet_check':True},test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_Close_Telnet_Server'
    common_name = '[%s]close telnet server in zd' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False)) 
    
    test_case_name='Web UI admin Auto logout test'
    test_name = 'CB_ZD_Adimn_Auto_Logout' 
    common_name = '[%s]web ui should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_case_name='Web UI auto logout when auth with Radius Server'
    test_name = 'ZD_Admin_Authentication' 
    common_name = '[%s]set zd auth with radius server-192.168.0.252(rad.cisco.user/rad.cisco.user)' % test_case_name
    test_cfgs.append(({"auth_type":"radius", "auth_srv_addr":"192.168.0.252", "auth_srv_port":"1812", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789", "enable_fallback":True,'skip_clean':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '[%s]login zd web by rad.cisco.user/rad.cisco.user' % test_case_name
    test_cfgs.append(({'login_name':'rad.cisco.user','login_pass':'rad.cisco.user','restore_zd_user':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Adimn_Auto_Logout' 
    common_name = '[%s]web ui should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Authenticate_Use_Admin' 
    common_name = '[%s]config ZD to auth with local admin user' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Test_Login' 
    common_name = '[%s]login zd web by admin/admin' % test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin'}, test_name, common_name, 1, False))
    
    test_case_name='SSHCLI Auto logout test when access zd with mgmt IF'
    test_name = 'CB_ZD_Access_ZD_Web_And_Cli_Through_Mgmt_If' 
    common_name = '[%s]login zd web from mgmt IF' % test_case_name
    test_cfgs.append(({'login_name':'admin','login_pass':'admin'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Admin_Auto_Logout'
    common_name = '[%s]SSH CLI should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))  
    
    test_case_name='WEB Auto logout test when access zd with mgmt IF'
    test_name = 'CB_ZD_Adimn_Auto_Logout' 
    common_name = '[%s]web ui should not logout 30 seconds before the timeout and can logout 30 seconds after timeout' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Set_ZD_Access_IP' 
    common_name = 'login zd web from zd real ip'
    test_cfgs.append(({'zd_ip':zd_ip,'login_name':'admin','login_pass':'admin','web':True,'cli':True,}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Disable_Mgmt_Interface'
    common_name = 'disable Management Interface from web UI'
    test_cfgs.append(({},test_name, common_name, 0, True))    
    
    return test_cfgs
    
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="admin auto logout test"
    )
    attrs.update(kwargs)
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="admin auto logout test"
    
    mgmt_if_enable = raw_input('this testbed enable mgmt vlan or not?"Y" for yes,"N" for No:')
    if mgmt_if_enable=="Y":
        mgmt_if = '192.168.128.5'
        vlan_id = '328'
        zd_ip = '192.168.128.2'
    else:
        mgmt_if = '192.168.0.5'
        vlan_id = '1'
        zd_ip = '192.168.0.2'
    test_cfgs = defineTestConfiguration(mgmt_if,vlan_id,zd_ip)
    ts = testsuite.get_testsuite(ts_name, "admin auto logout test", interactive_mode = attrs["interactive_mode"], combotest=True)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)   
    
    
 
if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
           
    
    
    
    
    