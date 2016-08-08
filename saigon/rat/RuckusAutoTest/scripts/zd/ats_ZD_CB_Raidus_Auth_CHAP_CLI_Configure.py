'''
Description: This test suite is used to verify whether the configure AAA server commands in ZD CLI work well.

'''


import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
                
   
def define_aaa_server_cfg_list():
    server_cfg_list = []
    
    server_cfg_list.append(dict(server_name = 'radius_server_1', new_server_name = 'radius_server_1_new', type = 'radius-auth', backup = False, 
                                server_addr = '192.168.0.252', server_port = '1812', radius_secret = '1234567890', radius_auth_method = 'chap',
                                cfg_name = 'Configure RADIUS CHAP Server without Backup'))

    server_cfg_list.append(dict(server_name = 'radius_server_2', new_server_name = 'radius_server_2_new', type = 'radius-auth', backup = True, 
                                server_addr = '192.168.0.252', server_port = '1812', radius_secret = '1234567890', radius_auth_method = 'chap',
                                backup_server_addr = '192.168.0.250', backup_server_port = '1813', backup_radius_secret = '1234567890', 
                                request_timeout = '3', retry_count = '2', retry_interval = '5',
                                cfg_name = 'Configure RADIUS CHAP Server with Backup'))

    return server_cfg_list
       

def define_test_cfg(tcfg):
    test_cfgs = []
   
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove AAA Servers from GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    for server_cfg in tcfg['server_cfg_list']:
        if server_cfg.get('new_server_name'):
            server_name = server_cfg['new_server_name']
        
        else:
            server_name = server_cfg['server_name']
            
        test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
        common_name = '[%s] Configure an AAA server in ZD CLI' % server_cfg['cfg_name']  
        test_cfgs.append(({'server_cfg_list': [server_cfg]}, test_name, common_name, 1, False))
            
        test_name = 'CB_ZD_Get_AAA_Servers'
        common_name = '[%s] Get the AAA server info from ZD GUI' % server_cfg['cfg_name']
        test_cfgs.append(({'server_name_list': [server_name]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Verify_AAA_Server_Cfg_In_GUI'
        common_name = '[%s] Verify the AAA server cfg in ZD GUI' % server_cfg['cfg_name']  
        test_cfgs.append(({'aaa_server_cfg': server_cfg}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA servers from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = {'testsuite_name': ''}
    attrs.update(kwargs)
    
    server_cfg_list = define_aaa_server_cfg_list()
    tcfg = {'server_cfg_list': server_cfg_list}
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else: 
        ts_name = "ZD CLI - Configure Radius CHAP Server" 
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the configure AAA server commands in ZD CLI work well",
                                 combotest=True)
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test cases with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)