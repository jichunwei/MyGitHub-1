import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(base_id, target_sta_radio):
    return u"TCID:01.01.06.%02d.%d" % (base_id,const.get_radio_id(target_sta_radio)) 

def getCommonName(tcid, test_desc):
    return u"%s-%s" % (tcid, test_desc)

def makeTestParams(test_sta, target_sta_radio):
    test_params=[]
    test_params.append(({'role':{'rolename':'testrole', 'allow_all_wlan':True, 'allow_generate_guestpass':False},
                         'test_station':test_sta},
                        "ZD_System_Create_Role",
                        tcid(1, target_sta_radio),
                        "Create new role with allow all wlan access"))
    test_params.append(({'role':{'rolename':'testrole', 'allow_all_wlan':False, 'allow_generate_guestpass':False},
                         'test_station':test_sta},
                        "ZD_System_Create_Role",
                        tcid(2, target_sta_radio),
                        "Create new role with specific wlan access"))
    test_params.append(({'role':{'rolename':'testrole', 'allow_all_wlan':True, 'allow_generate_guestpass':True},
                         'test_station':test_sta},
                        "ZD_System_Create_Role",
                        tcid(3, target_sta_radio),
                        "Create new role allowing guest pass generation"))
    test_params.append(({'rolename':'roletest', 'exist_role':'existrole'},
                        "ZD_System_Clone_Role",
                        tcid(4, target_sta_radio),
                        "Clone new role"))
    test_params.append(({'rolename':'roletest'},
                        "ZD_System_Delete_Role",
                        tcid(5,target_sta_radio),
                        "Delete existing role"))
    test_params.append(({},
                        "ZD_System_Delete_Role",
                        tcid(6,target_sta_radio),
                        "Delete all roles"))
    return test_params

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name="System - Roles"
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]    
    ts = testsuite.get_testsuite(ts_name,
                      "Verify the ability of the ZD to create or delete the roles properly",
                      interactive_mode = attrs["interactive_mode"])
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]        
    
    test_cfgs = makeTestParams(target_sta, target_sta_radio)
    test_order = 1
    test_added = 0
    for test_params, test_name, tcid, test_desc in test_cfgs:
        common_name=getCommonName(tcid, test_desc)
        test_params['target_sta_radio'] = target_sta_radio
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
