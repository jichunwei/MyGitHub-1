'''
Description:

Created on 2011-08-25
@author: serena.tan@ruckuswireless.com
'''


import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_aaa_server_cfgs():
    ras_cfg = dict(
        server_name = 'RADIUS',
        server_addr = '192.168.0.252',
        radius_auth_secret = '1234567890',
        server_port = '1812',
        username = 'ras.local.user',
        password = 'ras.local.user'
        )

    ad_cfg = dict(
        server_name = 'ACTIVE_DIRECTORY',
        server_addr = '192.168.0.250',
        server_port = '389',
        win_domain_name = 'rat.ruckuswireless.com',
        username = 'ad.user',
        password = 'ad.user'
        )

    ldap_cfg = dict(
        server_name = 'LDAP_SERVER',
        server_addr = '192.168.0.252',
        server_port = '389',
        ldap_search_base = 'dc=example,dc=net',
        ldap_admin_dn = 'cn=Manager,dc=example,dc=net',
        ldap_admin_pwd = 'lab4man1',
        username = 'test.ldap.user',
        password = 'test.ldap.user'
        )
    
    aaa_server_cfgs = dict(ras_cfg = ras_cfg, ad_cfg = ad_cfg, ldap_cfg = ldap_cfg)
    
    return aaa_server_cfgs


def define_guestpass_generate_cfgs(aaa_server_cfgs, local_user_cfg):
    cfgs = []
    
    cfgs.append(dict(auth_ser = 'Local Database',
                     username = local_user_cfg['username'], 
                     password = local_user_cfg['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = False,
                     set_name = 'Import CSV file with predefined usernames - Local'))
    
    cfgs.append(dict(auth_ser = aaa_server_cfgs['ras_cfg']['server_name'],
                     username = aaa_server_cfgs['ras_cfg']['username'],
                     password = aaa_server_cfgs['ras_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = False,
                     set_name = 'Import CSV file with predefined usernames - Radius'))
    
    cfgs.append(dict(auth_ser = aaa_server_cfgs['ldap_cfg']['server_name'],
                     username = aaa_server_cfgs['ldap_cfg']['username'],
                     password = aaa_server_cfgs['ldap_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = False,
                     set_name = 'Import CSV file with predefined usernames - LDAP'))

    cfgs.append(dict(auth_ser = aaa_server_cfgs['ldap_cfg']['server_name'],
                     username = aaa_server_cfgs['ldap_cfg']['username'],
                     password = aaa_server_cfgs['ldap_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = False,
                     set_name = 'Import CSV file with predefined usernames - AD'))

    cfgs.append(dict(auth_ser = 'Local Database',
                     username = local_user_cfg['username'], 
                     password = local_user_cfg['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = True,
                     set_name = 'Import CSV file with predefined usernames and guestpasses - Local'))
    
    cfgs.append(dict(auth_ser = aaa_server_cfgs['ras_cfg']['server_name'],
                     username = aaa_server_cfgs['ras_cfg']['username'],
                     password = aaa_server_cfgs['ras_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = True,
                     set_name = 'Import CSV file with predefined usernames and guestpasses - Radius'))
    
    cfgs.append(dict(auth_ser = aaa_server_cfgs['ldap_cfg']['server_name'],
                     username = aaa_server_cfgs['ldap_cfg']['username'],
                     password = aaa_server_cfgs['ldap_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = True,
                     set_name = 'Import CSV file with predefined usernames and guestpasses - LDAP'))

    cfgs.append(dict(auth_ser = aaa_server_cfgs['ldap_cfg']['server_name'],
                     username = aaa_server_cfgs['ldap_cfg']['username'],
                     password = aaa_server_cfgs['ldap_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = True, predefine_guestpass = True,
                     set_name = 'Import CSV file with predefined usernames and guestpasses - AD'))

    cfgs.append(dict(auth_ser = 'Local Database',
                     username = local_user_cfg['username'], 
                     password = local_user_cfg['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = False, predefine_guestpass = False,
                     set_name = 'Generate usernames and guestpasses automatically - Local'))
    
    cfgs.append(dict(auth_ser = aaa_server_cfgs['ras_cfg']['server_name'],
                     username = aaa_server_cfgs['ras_cfg']['username'],
                     password = aaa_server_cfgs['ras_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = False, predefine_guestpass = False,
                     set_name = 'Generate usernames and guestpasses automatically - Radius'))
    
    cfgs.append(dict(auth_ser = aaa_server_cfgs['ldap_cfg']['server_name'],
                     username = aaa_server_cfgs['ldap_cfg']['username'],
                     password = aaa_server_cfgs['ldap_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = False, predefine_guestpass = False,
                     set_name = 'Generate usernames and guestpasses automatically - LDAP'))

    cfgs.append(dict(auth_ser = aaa_server_cfgs['ldap_cfg']['server_name'],
                     username = aaa_server_cfgs['ldap_cfg']['username'],
                     password = aaa_server_cfgs['ldap_cfg']['password'],
                     number_profile = 10, repeat_cnt = 1,
                     import_csv_file = False, predefine_guestpass = False,
                     set_name = 'Generate usernames and guestpasses automatically - AD'))
    
    return cfgs


def define_guestpass_generate_test_cfgs(tcfg, generate_cfg):
    test_cfgs = []
    com_name = '[%s]' % generate_cfg['set_name']

    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = '%s Remove all guest passes from ZD' % com_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    if generate_cfg['import_csv_file']:
        test_name = 'CB_ZD_Generate_GuestPass_CSV_Profile'
        common_name = '%s Generate CSV profile' % com_name
        test_params = {'number_profile': generate_cfg['number_profile'],
                       'username': generate_cfg['username'],
                       'wlan_cfg': tcfg['wlan_cfg'],
                       'predefine_guestpass': generate_cfg['predefine_guestpass']
                       }
        test_cfgs.append((test_params, test_name, common_name, 2, False)) 
        
        test_name = 'CB_ZD_Generate_Multi_GuestPass_By_CSV_Profile'
        common_name = '%s Generate guest passes by CSV profile' % com_name
        test_params = {'auth_ser': generate_cfg['auth_ser'],
                       'username': generate_cfg['username'],
                       'password': generate_cfg['password'],
                       'wlan': tcfg['wlan_cfg']['ssid']
                       }
        test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
        test_name = 'CB_ZD_Verify_GuestPass_Info_On_WebUI'
        common_name = '%s Verify guest passes on WebUI' % com_name
        test_cfgs.append(({}, test_name, common_name, 2, False))
            
        if generate_cfg['predefine_guestpass']:
            test_name = 'CB_ZD_Download_GuestPasses_Record'
            common_name = '%s Download guest passes record' % com_name
            test_params = dict(username = generate_cfg['username'],
                               password = generate_cfg['password'])
            test_cfgs.append((test_params, test_name, common_name, 2, False)) 
            
            test_name = 'CB_ZD_Verify_GuestPass_In_Record_File'
            common_name = '%s Verify guest passes in record file' % com_name
            test_cfgs.append(({}, test_name, common_name, 2, False))
    
    else:
        test_name = 'CB_ZD_Create_Multi_Guest_Passes'
        common_name = '%s Generate guest passes automatically' % com_name
        test_params = {'wlan': tcfg['wlan_cfg']['ssid'],
                       'number_profile': generate_cfg['number_profile'],
                       'repeat_cnt':  generate_cfg['repeat_cnt'],
                       'username': generate_cfg['username'],
                       'password': generate_cfg['password'],
                       'auth_ser': generate_cfg['auth_ser']}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
        common_name = '%s Verify guest passes on WebUI' % com_name
        test_params = {'wlan_cfg': tcfg['wlan_cfg'],
                       'chk_detail': True}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    return test_cfgs


def define_test_cfgs(tcfg):
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create AAA Servers'
    test_params = {'auth_ser_cfg_list': tcfg['aaa_server_cfgs'].values()}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a guest access wlan'
    test_cfgs.append(({'wlan_cfg_list': [tcfg['wlan_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create a local user'
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    for guestpass_generate_cfg in tcfg['guestpass_generate_cfgs']:
        test_cfgs.extend(define_guestpass_generate_test_cfgs(tcfg, guestpass_generate_cfg))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    return test_cfgs
        
        
def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 ts_name = ""
                 )
    attrs.update(kwargs)

    aaa_server_cfgs = define_aaa_server_cfgs()
    
    local_user_cfg = dict(username = 'rat_guest_pass', password = 'rat_guest_pass')
    
    wlan_cfg = dict(ssid = "rat-wlan-guestpass-%s" % (time.strftime("%H%M%S")),
                    auth = "open", encryption = "none", type = 'guest')
    
    guestpass_generate_cfgs = define_guestpass_generate_cfgs(aaa_server_cfgs, local_user_cfg)
    
    tcfg = dict(aaa_server_cfgs = aaa_server_cfgs,
                local_user_cfg = local_user_cfg,
                wlan_cfg = wlan_cfg,
                guestpass_generate_cfgs = guestpass_generate_cfgs
                )
    
    test_cfgs = define_test_cfgs(tcfg)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Guest Pass Generation - Batch"

    ts = testsuite.get_testsuite(ts_name,
                                 "Verify Batch Generation of Guest Pass",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest = True)
    
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
    create_test_suite(**_dict)
