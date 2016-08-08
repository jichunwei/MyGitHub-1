'''
Steps
1. make the testbed with given info
2. call all the addtestsuite scripts sequentially

'''
import sys
import re
import copy
from pprint import pprint, pformat
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Debug as bugme

from RuckusAutoTest.scripts.zd import addtestsuites_ZD_System_AP_Control as system_ap_control_ts
from RuckusAutoTest.scripts.zd import addtestsuites_ZD_System_Roles as system_roles_ts
from RuckusAutoTest.scripts.zd import addtestsuites_ZD_System_Services as system_services_ts
from RuckusAutoTest.scripts.zd import addtestsuites_ZD_System_Users as system_users_ts
from RuckusAutoTest.scripts.zd import addtestsuite_Wlan_Option_8BSSIDs as wlan_options_8bssids_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_ACL as wlan_options_acl_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_Administration as administration_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_AP_Classification as ap_classification_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_EncryptionTypes as encryption_types_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_EncryptionTypesWebAuth as encryption_types_webauth_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_GuestAccess as guest_access_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_MapView as map_view_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_RateLimit as rate_limit_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_System as system_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_System_AuthServers as system_authservers_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_VLAN as vlan_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_Zero_IT as zero_it_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_ZeroIT_Misc as zero_it_misc_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_WLAN_Options_HideSSID as wlan_options_hidessid_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_VLAN_GuestAccess as vlan_guest_access_ts
from RuckusAutoTest.scripts.zd import addtestsuite_ZD_VLAN_WebAuth as vlan_webauth_ts

usage = '''
[HELP] This program help you to create netanya.sys tesbed and its testsuites 
It has 2 modes: automatic and interactive

For ex:
  python mk_netanya.sys-ts.py zd=192.168.0.2 sta_11na=192.168.1.10
'''

unaccepted_cfg_error = '''
ERROR: You have just input some parameters which is not supported by this script:
   %s
'''

required_params_not_found_error = '''
ERROR: You need at least one of the stations: sta_11g, sta_11ng, sta_11na
'''

default_cfg = dict(
    zd = '192.168.0.2',
    shell_key = '!v54!',
)

accepted_ks = default_cfg.keys()
stations = ['sta_11g', 'sta_11ng', 'sta_11na', 'sta_11a']
accepted_ks += stations

guest_access_cfg = dict(
    name = 'netanya.sys',
    testsuite_name = "System AP Control",
    interactive_mode = False,
)

def get_input_interactively():
    '''
    . prompt the operator and get the inputs
    '''
    print 'not written yet, do it yourself'
    exit()

def is_required_params_input(input):
    '''
    . required zd and at least one of the station
    '''

    for i in input.iterkeys():
        if i in stations: # found at least one station
            return True

    return False

def get_running_mode(input):
    '''
    . did operator input the required information? if not, then prompt them
    '''
    unaccepted_cfg = [i for i in input if i not in accepted_ks]
    if unaccepted_cfg:
        print unaccepted_cfg_error % unaccepted_cfg
        return 'usage'

    if not len(input): # nothing input, interactive mode
        return 'interactive'

    if not is_required_params_input(input):
        print required_params_not_found_error
        return 'usage'

    return 'auto'

def get_stations_with_type(input):
    '''
    . return station (ip, type) in a list
      something likes: [(192.168.1.11, 11n), ... ]
    '''
    return [(sta_ip, sta_k.split('sta_11')[1])
            for sta_k, sta_ip in input.iteritems() if sta_k in stations]

def get_stations(input):
    '''
    . return station ips in a list
    '''
    return [sta_ip for sta_ip, sta_k in get_stations_with_type(input)]

def generate_testbed(input):
    cfg = dict(
        name = 'netanya.sys',
        location = 'ruckus',
        owner = 'auto@ruckuswireless.com',
        Mesh = True,
    )
    cfg['sta_ip_list'] = get_stations(input)

    return testsuite.getMeshTestbed(**cfg)

def generate_testsuite(input):
    '''
    . generating 2 testsuites: ZD_Odessa_GuestAccess and ZD_Odessa_WebAuth
    '''
    stations_with_types = get_stations_with_type(input)
#        ga_cfg['sta_id'] = i
#        ga_cfg['testsuite_name'] += ' - %s' % stations_with_types[i][1]    
    default_ts_cfg = {'name': 'netanya.sys', 'interactive_mode': False}
    
    # Generate test suites which are not require station
    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "System - Roles"
    system_ap_control_ts.make_test_suite(**ts_cfg)      

    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "System - Services"
    ts_cfg['targetap'] = True
    system_services_ts.make_test_suite(**ts_cfg)     

    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "System - Users"
    system_users_ts.make_test_suite(**ts_cfg)     

    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "WLAN Options - ACL"
    wlan_options_acl_ts.make_test_suite(**ts_cfg)     

    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "ZD Administration"
    administration_ts.make_test_suite(**ts_cfg)     

    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "MAP View"
    ts_cfg['max_size'] = 2
    map_view_ts.make_test_suite(**ts_cfg)
    
    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "System Basic"    
    system_ts.make_test_suite(**ts_cfg)     

    ts_cfg = copy.deepcopy(default_ts_cfg)
    ts_cfg['testsuite_name'] = "System - Authentication Servers"    
    system_authservers_ts.make_test_suite(**ts_cfg)    
         

    # Generate test suites which are require station
    for i in range(len(stations_with_types)):
        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "System - Roles - STA-11%s" % stations_with_types[i][1] 
        system_roles_ts.make_test_suite(**ts_cfg)      

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "WLAN Options - 8BSSIDs - STA-11%s" % stations_with_types[i][1] 
        wlan_options_8bssids_ts.make_test_suite(**ts_cfg)      

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "QoS SmartCast - STA-11%s" % stations_with_types[i][1]
        ts_cfg['targetap'] = True 
        ap_classification_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        if stations_with_types[i][1] in ['g', 'ng']: 
            ts_cfg['sta_11g'] = (i, stations_with_types[i][1])
            ts_cfg['sta_11n'] = (i, stations_with_types[i][1])
        elif stations_with_types[i][1] in ['na']: 
            ts_cfg['sta_11n'] = (i, stations_with_types[i][1])
        elif stations_with_types[i][1] in ['g']:
            ts_cfg['sta_11g'] = (i, stations_with_types[i][1])
        else: 
            print required_params_not_found_error
        ts_cfg['testsuite_name'] = "WLAN Options - Wireless Client Isolation - STA-11%s" % stations_with_types[i][1]
        ts_cfg['targetap'] = True 
        ap_classification_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "Encryption Types - STA-11%s" % stations_with_types[i][1] 
        encryption_types_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "Encryption Types - Web Auth - STA-11%s" % stations_with_types[i][1]
        ts_cfg['targetap'] = True  
        encryption_types_webauth_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "WLAN Types - Guest Access - STA-11%s" % stations_with_types[i][1]
        ts_cfg['targetap'] = True  
        guest_access_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "WLAN Option - Rate Limiting - STA-11%s" % stations_with_types[i][1]          
        rate_limit_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "VLAN configuration - STA-11%s" % stations_with_types[i][1]          
        vlan_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['sta_xp'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "Zero-IT Activation - STA-11%s" % stations_with_types[i][1]          
        zero_it_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['testsuite_name'] = "Zero-IT Activation - Misc - STA-11%s" % stations_with_types[i][1]          
        zero_it_misc_ts.make_test_suite(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1]) 
        ts_cfg['targetap'] = True       
        ts_cfg['testsuite_name'] = "WLAN Options - Hide SSID - STA-11%s" % stations_with_types[i][1]          
        wlan_options_hidessid_ts.make_test_suite_on_ap(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['targetap'] = True
        ts_cfg['testsuite_name'] = "VLAN Configuration - Guest Access - STA-11%s" % stations_with_types[i][1]          
        vlan_guest_access_ts.make_test_suite_on_ap(**ts_cfg)   

        ts_cfg = copy.deepcopy(default_ts_cfg)
        ts_cfg['station'] = (i, stations_with_types[i][1])
        ts_cfg['targetap'] = True
        ts_cfg['testsuite_name'] = "VLAN Configuration - WebAuth - STA-11%s" % stations_with_types[i][1]          
        vlan_webauth_ts.make_test_suite_on_ap(**ts_cfg)   
       

if __name__ == '__main__':
    input = kwlist.as_dict(sys.argv[1:])
    running_mode = get_running_mode(input)

    if running_mode == 'usage':
        print usage
        exit()

    if running_mode == 'interactive': # get the input now
        input = get_input_interactively()

    cfg = copy.deepcopy(default_cfg)
    cfg.update(input)
    print('Your config:\n%s' % pformat(cfg))
    # interactive or auto will reach here, call the generation code
    generate_testbed(cfg)
    generate_testsuite(cfg)
    exit()
