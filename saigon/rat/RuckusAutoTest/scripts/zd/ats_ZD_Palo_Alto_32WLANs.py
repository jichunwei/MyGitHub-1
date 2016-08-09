import sys,time
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (14.01, tcid)

def defineTestConfiguration(target_station, max_num):
    test_cfgs = []

    test_name = 'ZD_Max_Num_Of_WLANs'
    common_name = 'Create/Delete %d WLANs' % max_num
    test_cfgs.append(({'target_station': target_station, 'max_num_of_wlans':max_num}, test_name, common_name, tcid(1)))

    test_name = 'ZD_WLAN_Options'
    common_name = 'Clone WLAN'
    test_cfgs.append(({'testing_feature':'clone wlan'}, test_name, common_name, tcid(2)))
    common_name = 'Edit WLAN'
    test_cfgs.append(({'testing_feature':'edit wlan'}, test_name, common_name, tcid(3)))
    common_name = 'Max length of WLANs'
    test_cfgs.append(({'testing_feature':'max length wlan', 'target_station':target_station}, test_name, common_name, tcid(4)))
    common_name = 'Min length of WLANs'
    test_cfgs.append(({'testing_feature':'min length wlan', 'target_station':target_station}, test_name, common_name, tcid(5)))    
    common_name = 'Random length of WLANs'
    test_cfgs.append(({'testing_feature':'random length wlan', 'target_station':target_station}, test_name, common_name, tcid(6)))
    common_name = 'ExMax length of WLANs'
    test_cfgs.append(({'testing_feature':'ex max length wlan', 'target_station':target_station}, test_name, common_name, tcid(7)))  

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    max_wlan = 32
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(tb_cfg["sta_ip_list"])
        ts_name = '32 WLANs'
        max = raw_input('The max number of WLANs is 32, input another number to change it (enter to skip): ')
        try:
            if max.strip():
                max_wlan = int(max)
        except:
            print 'The max wlans [%s] is invalid! The test will use the default value 32.' % max
    else:
        target_sta = tb_cfg["sta_ip_list"][attrs["sta_id"]]
    test_cfgs = defineTestConfiguration(target_sta, max_wlan)

    tested_wlan_list = [0,31]
    for i in range(4):        
        index = random.randint(1,30)
        while index in tested_wlan_list: 
            index = random.randint(1,30)
            time.sleep(0.1)
        tested_wlan_list.append(index)  
    tested_wlan_list.sort()
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = '32 WLANs'
    ts = testsuite.get_testsuite(ts_name, 'Verify WLAN Options', interactive_mode = attrs["interactive_mode"])

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
