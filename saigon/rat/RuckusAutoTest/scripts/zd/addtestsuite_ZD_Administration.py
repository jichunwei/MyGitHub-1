import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _tcid(base_id, description):
    return u'TCID:09.01.%02d - %s' % (base_id, description)


def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "ZD Administration"
    ts = testsuite.get_testsuite(ts_name,
                      "Verify the configuration of administrator account")

    test_name = "ZD_Administrator_Username_Password"
    
    common_name = _tcid(1, "Change admin username")
    test_params = "{'verify_username':True}"
    test_order = 1
    testsuite.addTestCase(ts, test_name, common_name, test_params, test_order)         
    
    common_name = _tcid(2, "Change admin password")
    test_params = "{'verify_password':True}"
    test_order += 1
    testsuite.addTestCase(ts, test_name, common_name, test_params, test_order)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)
