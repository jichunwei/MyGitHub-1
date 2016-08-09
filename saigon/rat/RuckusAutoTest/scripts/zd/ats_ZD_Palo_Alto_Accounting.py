import sys
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

pp = pprint.PrettyPrinter(indent=4)

def getDescription(id , option = ''):
    description_list = [
        'Enable/Disable accounting server only support EAP mode',
        'Invalid accounting server port',
        'Invalid accounting server IP',
        'Invalid accounting server secret',
        'Interrim udpate time',
        'Accounting trap when client associated/dissociate'
    ]
    return description_list[id]

def getCommonName(id, description):
    return "TCID:16.01.%02d - %s" % (id, description)

def showNotice():
    msg = "Please select Target AP for test (separate by space)"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def get_wlan_cfg(ssid, wlan_params):
    wlan_cfg = dict(
        auth = 'EAP',
        encryption = 'AES',
        wpa_ver = 'WPA2',
        ssid = 'rat-accounting',
        key_string = ''
    )

    wlan_cfg.update(wlan_params)
    return wlan_cfg

def getTestParams(params):
    auth_info = dict(
     idle_timeout = '10',
     password = 'ras.eap.user',
     session_timeout = 2,
     svr_addr = '192.168.0.252',
     svr_info = '1234567890',
     svr_port = '1812',
     type = 'radius',
     username = 'ras.eap.user'
    )
    acct_info = dict(
        svr_addr = '192.168.10.252',
        svr_port = '1813',
        svr_info = '1234567890',
        interim_update = '5'
    )

    test_params = dict(
        wlan_cfg = get_wlan_cfg('rat-wlangroups-integration', {}),
        target_ip = '192.168.0.252',
        target_station = '',
        auth_info = auth_info,
        acct_info = acct_info,
        active_ap = '',
        test_feature = '',
    )
    test_params.update(params)

    return test_params

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    while True:
        target_station = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
        if target_station: break
        print "Pick at least one station as your target"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]

    default_test_params = dict(
        target_station = target_station,
        active_ap = active_ap
    )

    test_order = 1
    test_added = 0
    test_name = 'ZD_Accounting'
    ts_description = 'Test Zone Director\'s Accounting Functionality'
    accounting_ts = testsuite.get_testsuite('ZD_Accounting', ts_description)

    common_name = getCommonName(1, 'Enable/Disable accounting server only support EAP mode')
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'enable_disable_account_server'
    testsuite.addTestCase(accounting_ts, test_name, common_name, test_params, test_order)
    test_added = test_added + 1
    test_order = test_order + 1

    common_name = getCommonName(2, 'Invalid accounting server port')
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'invalid_accounting_server_info'
    test_params['acct_info']['svr_port'] = '1800'
    testsuite.addTestCase(accounting_ts, test_name, common_name, test_params, test_order)
    test_added = test_added + 1
    test_order = test_order + 1

    common_name = getCommonName(3, 'Invalid accounting server IP')
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'invalid_accounting_server_info'
    test_params['acct_info']['svr_addr'] = '192.168.0.160'
    testsuite.addTestCase(accounting_ts, test_name, common_name, test_params, test_order)
    test_added = test_added + 1
    test_order = test_order + 1

    common_name = getCommonName(4, 'Invalid accounting server secret')
    test_params = getTestParams(default_test_params.copy())
    test_params['acct_info']['svr_info'] = '192.168.0.160'
    test_params['test_feature'] = 'invalid_accounting_server_info'
    testsuite.addTestCase(accounting_ts, test_name, common_name, test_params, test_order)
    test_added = test_added + 1
    test_order = test_order + 1

    common_name = getCommonName(6, 'Interrim udpate time')
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'interim_update'
    testsuite.addTestCase(accounting_ts, test_name, common_name, test_params, test_order)
    test_added = test_added + 1
    test_order = test_order + 1

    common_name = getCommonName(8, 'Accounting trap when client associated/dissociate')
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'sta_join_leave'
    testsuite.addTestCase(accounting_ts, test_name, common_name, test_params, test_order)
    test_added = test_added + 1
    test_order = test_order + 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, accounting_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
