''' 
Do Backup and Restore against Smart Redundancy with WLAN/WLANGROUP/User/ROLE etc. configuration.

Created by louis
Updated by chris at 2011-11-3
Running in ZD_SM test bed other then "ZD_Scaling" or "ZD_Stations" 
'''


import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as constant


GP_RANGE = (1, 144000)


def define_gp_hotspot_profile_cfgs():
    hotspot_cfg_list = []
    hotspot_cfg_list.append(dict(name = 'profile-gp-%s' % time.strftime("%H%M%S"),
                                 login_page = 'http://192.168.0.250/login.html',
                                 idle_timeout = random.randint(GP_RANGE[0], GP_RANGE[1])))
    
    return hotspot_cfg_list
        
        
def define_gp_wlan_cfgs():
    wlan_cfg_list = []
    wlan_cfg_list.append(dict(ssid = "web-gp-%s" % time.strftime("%H%M%S"),
                              auth = "open", encryption = "none", 
                              do_webauth = True, 
                              do_grace_period = True,
                              grace_period = random.randint(GP_RANGE[0], GP_RANGE[1])))
    
    wlan_cfg_list.append(dict(ssid = "guest-gp-%s" % time.strftime("%H%M%S"),
                              auth = "open", encryption = "none", 
                              type = "guest",
                              do_grace_period = True,
                              grace_period = random.randint(GP_RANGE[0], GP_RANGE[1])))
    
    return wlan_cfg_list


def defineInputConfig():
    test_conf = {'zd1_ip_addr':'192.168.0.2',
                 'zd2_ip_addr':'192.168.0.3',
                 }
    test_conf['share_secret'] = _generate_secret_key(random.randint(5,15))
    
    return test_conf
 
 
def _generate_secret_key(n):
    al=list('abcdefghijklmnopqrstuvwxyz0123456789') 
    st = ''
    for i in range(n):
        index = random.randint(0, 35) 
        st = st + al[index] 
        
    return st


def define_wlan_conf():
    wlan_cfg_list = []
    open_wlan = {
                 'ssid': 'rat-role-open-none',
                 'auth': 'open',
                 'encryption' : 'none',     
                 'do_webauth' : True     
                }
    wlan_cfg_list.append(open_wlan)
    
    open_wlan2 = {
                  'ssid': 'rat-open-none-without-role',
                  'auth': 'open',
                  'encryption' : 'none',  
                  'do_webauth' : True              
                 }
    wlan_cfg_list.append(open_wlan2)
    
    open_wpa_tkip = {
                    'ssid':'dpsk-test', 
                    'auth':'open',
                    'encryption':'TKIP',
                    'wpa_ver':'WPA',
                    'do_dynamic_psk':True,
                    'key_string':'open-WPA-TKIP'
                    }
    wlan_cfg_list.append(open_wpa_tkip)
    
    open_none_guess = {
                       'ssid': 'guest-test',
                       'auth': 'open',
                       'encryption' : 'none',     
                       'type':'guest'
                       }
    wlan_cfg_list.append(open_none_guess)
    
    return wlan_cfg_list


def defineTestConfiguration():
    test_cfgs = []
    input_cfg = defineInputConfig()
    wlan_cfg_list = define_wlan_conf()
    gp_wlan_cfg_list = define_gp_wlan_cfgs()
    gp_profile_list = define_gp_hotspot_profile_cfgs()
    
    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial test environment'
    test_cfgs.append(({'zd1_ip_addr': input_cfg['zd1_ip_addr'], 
                       'zd2_ip_addr': input_cfg['zd2_ip_addr'],
                       'share_secret': input_cfg['share_secret']},
                       test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy'
    test_cfgs.append(({},test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = 'Get the Active ZD.'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Set_Active_ZD'
    common_name = "Coordinate Active ZD and Standby ZD."
    test_cfgs.append(({},test_name,common_name,0,False))
    
    
    test_name = 'CB_Scaling_RemoveZDAllConfig'
    common_name = '[Backup in SM-Full]Remove all the Configurations'
    test_cfgs.append(({},test_name, common_name,1,False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[Backup in SM-Full]Create "OPEN-NONE" WLANs'
    test_cfgs.append(({'wlan_cfg_list':wlan_cfg_list},test_name, common_name, 2, False))
    
    role_cfg = {"rolename": "rat-role", 
                "rat-role": "", 
                "guestpass": '', 
                "description": "",
                "group_attr": "", 
                "zd_admin": ""}
    
    test_name = 'CB_ZD_Create_Single_Role'
    common_name = '[Backup in SM-Full]Create a Single Role on ZD named rat-role'
    test_cfgs.append(({'role_cfg':role_cfg},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = '[Backup in SM-Full]Create a Local user rat.local.user'
    test_cfgs.append(({'username':'rat.local.user','password':'rat.local.user'},
                      test_name, common_name,2,False))
    
    wgs_cfg = dict(ap_rp = {'bg': {'wlangroups': 'rat-restore-wlangroup'}},
                   name = 'rat-restore-wlangroup',
                   description = 'rat-restore-wlangroup',)
    
    test_name = 'CB_ZD_Create_Wlan_Group'
    common_name = '[Backup in SM-Full]Create a Wlan Group'
    test_cfgs.append(({'wgs_cfg':wgs_cfg},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Create_L2_ACLs'
    common_name = '[Backup in SM-Full]Create a L2 ACL'
    test_cfgs.append(({'num_of_mac':1},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Create_L3_ACLs'
    common_name = '[Backup in SM-Full]Create a L3 ACL'
    test_cfgs.append(({'num_of_acls':1,
                       'num_of_rules':1,
                       },test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = '[Backup in SM-Full]Create a hotspot profile with grace period'
    test_cfgs.append(({'hotspot_profiles_list': gp_profile_list}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[Backup in SM-Full]Create WLANs with grace period'
    test_cfgs.append(({'wlan_cfg_list': gp_wlan_cfg_list}, 
                      test_name, common_name, 0, False))
    
    save_to = constant.save_to
    test_name = 'CB_ZD_Backup'
    common_name = '[Backup in SM-Full]Backup System'
    test_cfgs.append(({'save_to':save_to},test_name, common_name,2,False)) 
    
    test_name = 'CB_Scaling_RemoveZDAllConfig'
    common_name = '[Restore in SM-Full]Remove all the Configurations'
    test_cfgs.append(({},test_name, common_name,1,False)) 
    
    test_name = 'CB_ZD_Restore'
    common_name = '[Restore in SM-Full]Restore the backup file'
    test_cfgs.append(({},test_name, common_name,2,False)) 
    
    
    test_name = 'CB_ZD_Verify_L3_ACLs_Info'
    common_name = '[Restore in SM-Full]Verify L3 ACL has restored correctly'
    test_cfgs.append(({},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Verify_Local_User'
    common_name = '[Restore in SM-Full]Verify users which are restored to original configuration'
    test_cfgs.append(({},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Verify_Wlan_Groups_Info'
    common_name = '[Restore in SM-Full]Verify WLAN Group rat-restore-wlangroup exist'
    test_cfgs.append(({},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Verify_Wlans_Info'
    common_name = '[Restore in SM-Full]Verify WLANs which are restored to original configuration'
    test_cfgs.append(({},test_name, common_name,2,False)) 
    
    for profile_cfg in gp_profile_list:
        test_name = 'CB_ZD_Verify_Grace_Period_In_GUI'
        common_name = "[Restore in SM-Full]Verify grace period in profile: %s" % profile_cfg['name']
        test_params = {'hotspot_name': profile_cfg['name'],
                       'grace_period': profile_cfg['idle_timeout']}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    for wlan_cfg in gp_wlan_cfg_list:
        test_name = 'CB_ZD_Verify_Grace_Period_In_GUI'
        common_name = "[Restore in SM-Full]Verify grace period in WLAN: %s" % wlan_cfg['ssid']
        test_params = {'wlan_name': wlan_cfg['ssid'],
                       'grace_period': wlan_cfg['grace_period']}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = "Clear up the Smart Redundancy test environment"
    test_cfgs.append(({},test_name, common_name,0,False)) 

    return test_cfgs


def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'Backup and  Restore by full mode under ZD smart redundancy'
    ts = testsuite.get_testsuite(ts_name, 'Verify ZD can backup restore by full mode under ZD smart redundancy ENV', combotest=True)
    test_cfgs = defineTestConfiguration()

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
    createTestSuite(**_dict)
