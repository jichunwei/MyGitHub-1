import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(base_id):
    return u"TCID:01.01.05.%02d" %base_id

def getCommonName(tcid, test_desc):
    return u"%s-%s" % (tcid, test_desc)

def makeTestParams(tbcfg):
    test_params = []
    test_params.append(({'user':{'username':'testuser', 'password':'testpass'}},
                        "ZD_System_Create_User",
                        tcid(1),
                        "Create new user with default role"))
    test_params.append(({'user':{'username':'testuser', 'password':'testpass'}, 'exist_user':'existuser'},
                        "ZD_System_Clone_User",
                        tcid(2),
                        "Clone new user using existing user"))
    test_params.append(({'username':'testuser'},
                        "ZD_System_Delete_User",
                        tcid(3),
                        "Delete existing user"))
    test_params.append(({},
                        "ZD_System_Delete_User",
                        tcid(4),
                        "Delete all existing users"))

    # default we will not import scalability/stress tests
    if tbcfg.has_key('doSSTests') and tbcfg['doSSTests']:
        test_params.append(({'max_users': 1024},
                            "ZD_System_Create_User",
                            tcid(5),
                            "Create max number of users 1024"))

    return test_params

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "System - Users"
    ts = testsuite.get_testsuite(ts_name,
                      "Verify the ability of the ZD to create or delete users account",
                      interactive_mode = attrs["interactive_mode"])
    test_cfgs = makeTestParams(tbcfg)
    test_order = 1
    test_added = 0
    for test_params, test_name, tcid, test_desc in test_cfgs:
        common_name=getCommonName(tcid, test_desc)
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)

