'''
Description:

Created on 2011-08-25
@author: serena.tan@ruckuswireless.com
'''


import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfgs(tcfg):
    test_cfgs = []

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
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a guest access wlan'
    test_cfgs.append(({'wlan_cfg_list': [tcfg['wlan_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create a local user'
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    
    com_name = '[Guest pass can be printed by different formats]'
    
    test_name = 'CB_ZD_Download_GuestPass_Printout_Sample'
    common_name = '%s Download guestpass printout sample' % com_name
    test_cfgs.append(({'sample_filename': 'guestpass_print.html'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Customize_GuestPass_Printout_Sample'
    common_name = '%s Customize guestpass printout sample' % com_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Guest_Pass_Printout'
    common_name = '%s Create a guestpass printout' % com_name
    test_params = {'guestpass_printout_cfg': {'name': 'New English',
                                              'description': 'New Guest Pass Printout in English'}}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Print',
                   'validate_gprints': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_GuestPass_Printout'
    common_name = '%s Verify the guestpass printout' % com_name
    test_cfgs.append(({}, test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_Remove_GuestPass_Printout_By_Name'
    common_name = '%s Remove the created guestpass printout' % com_name
    test_cfgs.append(({'gprint_name_list': ['New English']}, test_name, common_name, 2, False))   
    
    
    com_name = '[Automatically generated guest pass can be deleted]'

    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass automatically' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Auto'}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_GuestPass_Info_On_WebUI'
    common_name = '%s Verify the guest pass on ZD WebUI' % com_name
    test_params = {'expected_webui_info': {'Rat_Guest_Auto': [tcfg['local_user_cfg']['username'], 
                                                             tcfg['wlan_cfg']['ssid']]}}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_GuestPass_By_GuestName'
    common_name = '%s Remove the generated guest pass' % com_name
    test_cfgs.append(({'guest_name': 'Rat_Guest_Auto', 'load_time': 1}, test_name, common_name, 2, False))
    
   
    com_name = '[Manually generated guest pass can be imported to ZD]' 

    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass manually' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Manu',
                   'use_static_key': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_GuestPass_Info_On_WebUI'
    common_name = '%s Verify the guest pass on ZD WebUI' % com_name
    test_params = {'expected_webui_info': {'Rat_Guest_Manu': [tcfg['local_user_cfg']['username'], 
                                                              tcfg['wlan_cfg']['ssid']]}}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    
    com_name = '[Manually generated guest pass can be deleted]'

    test_name = 'CB_ZD_Remove_GuestPass_By_GuestName'
    common_name = '%s Remove the generated guest pass' % com_name
    test_cfgs.append(({'guest_name': 'Rat_Guest_Manu', 'load_time': 1}, test_name, common_name, 2, False))
    
    
    com_name = '[Duplicate guest name and guest pass can not be imported to ZD]' 
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Dup'}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_GuestPass_Duplicate_Generate'
    common_name = '%s Verify duplicate guest pass generate' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'wlan': tcfg['wlan_cfg']['ssid']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    
    com_name = '[Guest passes can be exported to CSV file]'
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = '%s Remove all guest passes' % com_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Create_Multi_Guest_Passes'
    common_name = '%s Generate multiple guest passes' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'auth_ser': 'Local Database',
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'number_profile': 10, 'repeat_cnt': 1}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Download_GuestPasses_Record'
    common_name = '%s Export guest passes to CSV file' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Verify_GuestPass_In_Record_File'
    common_name = '%s Verify guest passes in the CSV file' % com_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    

    com_name = '[Maximum guest passes can be generated]'
    
    test_name = 'CB_ZD_Verify_GuestPass_Maxium_Generate'
    common_name = '%s Generate maximum guest passes' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'auth_ser': 'Local Database',
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'number_profile': 100,
                   'max_gp_allowable': 1250}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = '%s Remove all guest passes' % com_name
    test_cfgs.append(({'load_time': 5}, test_name, common_name, 0, False))
  
    
    com_name = '[Guest pass expiration - from creation]'

    test_name = 'CB_ZD_Set_GuestPass_Policy'
    common_name = '%s Set the guest pass policy' % com_name
    test_params = {'auth_serv': "Local Database", 
                   'is_first_use_expired': False}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Exp1',
                   'duration': 2,
                   'duration_unit': 'Days'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Expire_GuestPass'
    common_name = '%s Expire the guest pass' % com_name
    test_params = {'is_first_use_expired': False,
                   'has_been_used': False,
                   'duration': 2,
                   'duration_unit': 'Days',
                   'guest_name': 'Rat_Guest_Exp1'
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = '%s Set the guest access policy' % com_name
    test_params = {'use_guestpass_auth': True, 
                   'use_tou': False, 
                   'redirect_url': ''}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all wlans from station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['target_sta']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate station' % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 'wlan_cfg': tcfg['wlan_cfg']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%s Get station Wifi address' % com_name
    test_cfgs.append(({'sta_tag': tcfg['target_sta']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_Invalid_GuestPass'
    common_name = "%s Perform guest auth in station" % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 
                   'use_tou': False, 
                   'redirect_url': '', 
                   'no_auth': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%s Verify station info on ZD' % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 
                   'status': 'Unauthorized', 
                   'wlan_cfg': tcfg['wlan_cfg']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    
    com_name = '[Guest pass expiration - from first use]'
    
    test_name = 'CB_ZD_Set_GuestPass_Policy'
    common_name = '%s Set the guest pass policy' % com_name
    test_params = {'auth_serv': "Local Database",
                   'is_first_use_expired': True,
                   'valid_day': '5'}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass' % com_name
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password'],
                   'wlan': tcfg['wlan_cfg']['ssid'],
                   'guest_fullname': 'Rat_Guest_Exp2',
                   'duration': 2,
                   'duration_unit': 'Days'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = '%s Set the guest access policy' % com_name
    test_params = {'use_guestpass_auth': True, 
                   'use_tou': False, 
                   'redirect_url': ''}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all wlans from station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['target_sta']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate station' % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 'wlan_cfg': tcfg['wlan_cfg']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%s Get station Wifi address' % com_name
    test_cfgs.append(({'sta_tag': tcfg['target_sta']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = "%s Perform guest auth in station before guest pass expired" % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 
                   'use_tou': False, 
                   'redirect_url': '', 
                   'no_auth': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%s Verify station info on ZD after guest auth' % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 
                   'status': 'Authorized', 
                   'wlan_cfg': tcfg['wlan_cfg'], 
                   'guest_name': 'Rat_Guest_Exp2',
                   'use_guestpass_auth': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_GuestPass_Expire_Time_On_WebUI'
    common_name = '%s Verify guest pass expire time on ZD WebUI' % com_name
    test_params = {'is_first_use_expired': True,
                   'has_been_used': True,
                   'duration': 2,
                   'duration_unit': 'Days',
                   'guest_name': 'Rat_Guest_Exp2'
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Expire_GuestPass'
    common_name = '%s Expire the guest pass' % com_name
    test_params = {'is_first_use_expired': True,
                   'has_been_used': True,
                   'duration': 2,
                   'duration_unit': 'Days',
                   'guest_name': 'Rat_Guest_Exp2'
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Active_Clients'
    common_name = '%s Remove all active clients from ZD' % com_name
    test_cfgs.append(({}, test_name, common_name, 2, False))    
    
    test_name = 'CB_Station_Verify_Invalid_GuestPass'
    common_name = "%s Perform guest auth in station after guest pass expired" % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 
                   'use_tou': False, 
                   'redirect_url': '', 
                   'no_auth': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%s Verify station info on ZD after guest pass expired' % com_name
    test_params = {'sta_tag': tcfg['target_sta'], 
                   'status': 'Unauthorized', 
                   'wlan_cfg': tcfg['wlan_cfg']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Close the browser in station to clean up'
    test_cfgs.append(({'sta_tag': tcfg['target_sta']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = 'Remove all guest passes from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
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
    
    wlan_cfg = dict(ssid = "rat-wlan-guestpass-%s" % (time.strftime("%H%M%S")),
                    auth = "open", encryption = "none", type = 'guest')
    
    tcfg = dict(local_user_cfg = local_user_cfg,
                wlan_cfg = wlan_cfg,
                target_sta = target_sta
                )
    
    test_cfgs = define_test_cfgs(tcfg)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Guest Pass Generation - Basic Test"

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
