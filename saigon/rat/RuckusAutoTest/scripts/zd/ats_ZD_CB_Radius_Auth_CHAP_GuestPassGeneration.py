'''
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfgs(tcfg):
    test_cfgs = []

    ras_cfg = tcfg['ras_cfg']

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create the target station'
    test_params = {'sta_tag': tcfg['target_sta'], 'sta_ip_addr': tcfg['target_sta']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in station'
    test_cfgs.append(({'sta_tag': tcfg['target_sta']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Radius_Server_Auth_Method'
    common_name = 'Test Radius Authentication Server'
    param_cfg = {'server_name': ras_cfg['server_name'], 
                 'user': tcfg['username'], 'password':tcfg['password'], 
                 'invalid_user': 'rad.cisco', 'invalid_password':'rad.cisco',
                 'radius_auth_method': ras_cfg['radius_auth_method'],}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))                  

    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a guest access wlan'
    test_cfgs.append(({'wlan_cfg_list': [tcfg['wlan_cfg']]}, test_name, common_name, 0, False))
    
    com_name = '[Automatically generated guest pass can be deleted]'

    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass automatically' % com_name
    test_params = {'username': tcfg['username'], 
                   'password': tcfg['password'],
                   'auth_ser': tcfg['auth_ser'], 
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Auto'}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_GuestPass_Info_On_WebUI'
    common_name = '%s Verify the guest pass on ZD WebUI' % com_name
    test_params = {'expected_webui_info': {'Rat_Guest_Auto': [tcfg['username'], 
                                                             tcfg['wlan_cfg']['ssid']]}}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_GuestPass_By_GuestName'
    common_name = '%s Remove the generated guest pass' % com_name
    test_cfgs.append(({'guest_name': 'Rat_Guest_Auto', 'load_time': 1}, test_name, common_name, 2, False))
    
   
    com_name = '[Manually generated guest pass can be deleted]' 

    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass manually' % com_name
    test_params = {'username': tcfg['username'], 
                   'password': tcfg['password'],
                   'auth_ser': tcfg['auth_ser'], 
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Manu',
                   'use_static_key': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_GuestPass_Info_On_WebUI'
    common_name = '%s Verify the guest pass on ZD WebUI' % com_name
    test_params = {'expected_webui_info': {'Rat_Guest_Manu': [tcfg['username'], 
                                                              tcfg['wlan_cfg']['ssid']]}}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_GuestPass_By_GuestName'
    common_name = '%s Remove the generated guest pass' % com_name
    test_cfgs.append(({'guest_name': 'Rat_Guest_Manu', 'load_time': 1}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Close the browser in station to clean up'
    test_cfgs.append(({'sta_tag': tcfg['target_sta']}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = 'Remove all guest passes from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_GuestPassGen_Select_Auth_Server'
    common_name = 'Select authentication server to original value'
    test_cfgs.append(({'guestpassgen_auth_serv':'Local Database'}, test_name, common_name, 0, True))    

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove AAA Servers from GUI at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))         
    
    return test_cfgs
        
        
def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 ts_name = ""
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    target_sta = testsuite.getTargetStation(sta_ip_list)

    local_user_cfg = dict(username = 'rat_guest_pass', password = 'rat_guest_pass')
    
    ras_name = 'ruckus-radius-%s' % (time.strftime("%H%M%S"),)

    wlan_cfg = dict(ssid = "rat-wlan-guestpass-%s" % (time.strftime("%H%M%S")),
                    auth = "open", encryption = "none", type = 'guest')

    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    username = 'ras.local.user'
    password = 'ras.local.user'
            
    tcfg = {'ras_cfg': {'server_addr': ras_ip_addr,
                        'server_port' : '1812',
                        'server_name' : ras_name,
                        'radius_auth_secret': '1234567890',
                        'radius_auth_method': 'chap',
                        },
                'local_user_cfg': local_user_cfg,
                'wlan_cfg': wlan_cfg,
                'target_sta': target_sta,
                'username': username,
                'password': password,
                'auth_ser': ras_name,
                }
    
    test_cfgs = define_test_cfgs(tcfg)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Guest Pass Generation - Radius Auth CHAP"

    ts = testsuite.get_testsuite(ts_name,
                                 "Verify The Basic Function of Guest Pass Generation",
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