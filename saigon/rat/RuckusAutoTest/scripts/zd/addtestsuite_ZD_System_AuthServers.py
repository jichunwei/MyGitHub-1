import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(base_id):
    return u"TCID:01.01.04.%02d" % base_id

def getCommonName(tcid, test_desc):
    return u"%s-%s" % (tcid, test_desc)

def makeTestParams(tbcfg, attrs = {}):
    default = {'rad_server':'192.168.0.252', \
              'rad_port':'1812', \
              'rad_secret':'1234567890', \
              'ad_server':'192.168.0.250', \
              'ad_port':'389', \
              'ad_domain':'rat.ruckuswireless.com'}
    test_params = []
    if attrs["interactive_mode"]:
        new_rad_server = raw_input('Input radius server, press Enter to default(%s)' % default['rad_server'])
        new_rad_port = raw_input('Input radius port, press Enter to default(%s)' % default['rad_port'])
        new_rad_secret = raw_input('Input radius secret, press Enter to default(%s)' % default['rad_secret'])
        new_ad_server = raw_input('Input ad server, press Enter to default(%s)' % default['ad_server'])
        new_ad_port = raw_input('Input ad port, press Enter to default(%s)' % default['ad_port'])
        new_ad_domain = raw_input('Input ad domain, press Enter to default(%s)' % default['ad_domain'])
    else:
        new_rad_server = ""
        new_rad_port = ""
        new_rad_secret = ""
        new_ad_server = ""
        new_ad_port = ""
        new_ad_domain = ""

    rad_server = default['rad_server'] if new_rad_server == "" else new_rad_server
    rad_port = default['rad_port'] if new_rad_port == "" else new_rad_port
    rad_secret = default['rad_secret'] if new_rad_secret == "" else new_rad_secret
    ad_server = default['ad_server'] if  new_ad_server == "" else new_ad_server
    ad_port = default['ad_port'] if  new_ad_port == "" else new_ad_port
    ad_domain = default['ad_domain'] if new_ad_domain == "" else new_ad_domain

    test_params.append(({"server":rad_server, "port":rad_port, "secret":rad_secret, "server_name":"radius_server"},
        "ZD_System_Create_Auth_Server",
        tcid(1),
        "Create Radius Server",))
    test_params.append(({"server":rad_server, "port":rad_port, "secret":rad_secret, "server_name":"radius_server"},
        "ZD_System_Clone_Auth_Server",
        tcid(2),
        "Clone existing Radius Server",))
    test_params.append(({"server":ad_server, "port":ad_port, "domain":ad_domain, "server_name":"AD_Server"},
        "ZD_System_Create_Auth_Server",
        tcid(3),
        "Create AD server",))
    test_params.append(({"server":ad_server, "port":ad_port, "domain":ad_domain, "server_name":"AD_Server"},
        "ZD_System_Clone_Auth_Server",
        tcid(4),
        "Clone existing AD Server",))
    # default we will not import scalability/stress tests
    if tbcfg.has_key('doSSTests') and tbcfg['doSSTests']:
        test_params.append(({"server":rad_server, "port":rad_port, "secret":rad_secret, "server_name":"radius_server",
                             "number_server":100},
            "ZD_System_Create_Auth_Server",
            tcid(5),
            "Create Max number of Authen Server",))
    test_params.append(({"server":rad_server, "port":rad_port, "secret":rad_secret, "server_name":"radius_server",
                         "number_server":2, "delete_server":"2"},
        "ZD_System_Delete_Auth_Server",
        tcid(6),
        "Delete existing server",))
    test_params.append(({"server":rad_server, "port":rad_port, "secret":rad_secret, "server_name":"radius_server",
                         "number_server":2, "delete_server":"all"},
        "ZD_System_Delete_Auth_Server",
        tcid(7),
        "Delete all server",))
    test_params.append(({"user":"local.user", "password":"local.user", "server_name":"Local Database"},
        "ZD_System_Test_Auth_Server",
        tcid(8),
        "Test Authenticate against Local Database",))
    test_params.append(({"server":rad_server, "port":rad_port, "secret":rad_secret, "server_name":"radius_server",
                         "user":"ras.local.user", "password":"ras.local.user"},
        "ZD_System_Test_Auth_Server",
        tcid(9),
        "Test Authenticate against Radius Server",))
    test_params.append(({"server":ad_server, "port":ad_port, "domain":ad_domain, "server_name":"AD_Server",
                         "user":"rat", "password":"1234567890"},
        "ZD_System_Test_Auth_Server",
        tcid(10),
        "Test Authenticate against AD",))
    return test_params

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = None,
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "System - Authentication Servers"
    ts = testsuite.get_testsuite("System - Authentication Servers",
                      "Verify create, clone, delete and test authentication server setting on Zone Director")
    test_cfgs = makeTestParams(tbcfg, attrs)
    test_order = 1
    test_added = 0
    for test_params, test_name, tcid, test_desc in test_cfgs:
        common_name = getCommonName(tcid, test_desc)
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

