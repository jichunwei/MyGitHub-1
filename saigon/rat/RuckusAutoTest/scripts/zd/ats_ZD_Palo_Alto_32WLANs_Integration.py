import sys
import random, time
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (14.02, tcid)

def defineTestConfiguration(target_station, ap_conn_mode):
    test_cfgs = []
    wlan_profile_set = 'set_of_32_open_none_wlans'
    wlan_profile_set_for_guest = 'set_of_32_open_none_wlans'

    if ap_conn_mode =='l3':
        print 'Please use the script "ats_ZD_Palo_Alto_32WLANs_Integration_With_Specific_APs.py" to add test cases for this mode'
        return test_cfgs

    test_name = 'ZD_MultiWlans_Block_Client_Integration'
    common_name = '%s Wlans + Block wireless client' % wlan_profile_set
    test_cfgs.append(({'target_station': target_station, 'wlan_config_set':wlan_profile_set},
                      test_name, common_name, tcid(1)))

    test_name = 'ZD_MultiWlans_ZeroIT_Integration'
    common_name = '%s Wlans + Default Role + ZeroIT' % wlan_profile_set
    test_cfgs.append(({'target_station': target_station, 'wlan_config_set':wlan_profile_set},
                      test_name, common_name, tcid(16)))

    test_name = 'ZD_MultiWlans_GuestAccess_Integration'
    common_name = '%s Wlans + Guest Access' % wlan_profile_set_for_guest
    test_cfgs.append(({'target_station': target_station, 'wlan_config_set':wlan_profile_set},
                      test_name, common_name, tcid(23)))

    test_name = 'ZD_MultiWlans_WebAuth_Integration'
    common_name = '%s Wlans + Web Auth' % wlan_profile_set
    test_cfgs.append(({'target_station': target_station, 'wlan_config_set':wlan_profile_set},
                      test_name, common_name, tcid(24)))

    return test_cfgs

def make_test_suite(**kwargs):
    #tbi = getTestbed(**kwargs)
    #tb_cfg = testsuite.getTestbedConfig(tbi)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']

    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
    
    tested_wlan_list = [0,31]
    for i in range(4):        
        index = random.randint(1,30)
        while index in tested_wlan_list: 
            index = random.randint(1,30)
            time.sleep(0.1)
        tested_wlan_list.append(index)    
    tested_wlan_list.sort()
    ap_conn_mode = ''
    while ap_conn_mode not in ['l2', 'l3']:
        ap_conn_mode = raw_input('Please select the connection mode of APs in your testbed (l2/l3): ')

    ts_name = '32 WLANs - Integration'

    test_cfgs = defineTestConfiguration(target_sta, ap_conn_mode)
    ts = testsuite.get_testsuite(ts_name, 'Verify 32 WLANs Integration')

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        test_params['tested_wlan_list'] = tested_wlan_list
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, cname)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
