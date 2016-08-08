import sys
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

pp = pprint.PrettyPrinter(indent=4)

def getCommonName(id, ap_model_id, ap_role_id, description, ap_type):
    return "TCID:16.01.%02d.%s.%s - %s - %s" % (id, ap_model_id, ap_role_id, description, ap_type)

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

def defineTestParams(active_ap, active_ap_conf, target_station):
    test_params_list = []
    ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
    ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
    ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
    default_test_params = {'active_ap': active_ap, 'target_station': target_station}

    description = 'Enable/Disable accounting server only support EAP mode'
    common_name = getCommonName(1, ap_model_id, ap_role_id, description, ap_type)
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'enable_disable_account_server'
    test_params_list.append((test_params, common_name))

    description = 'Invalid accounting server port'
    common_name = getCommonName(2, ap_model_id, ap_role_id, description, ap_type)
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'invalid_accounting_server_info'
    test_params['acct_info']['svr_port'] = '1800'
    test_params_list.append((test_params, common_name))

    description = 'Invalid accounting server IP'
    common_name = getCommonName(3, ap_model_id, ap_role_id, description, ap_type)
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'invalid_accounting_server_info'
    test_params['acct_info']['svr_addr'] = '192.168.0.160'
    test_params_list.append((test_params, common_name))

    description = 'Invalid accounting server secret'
    common_name = getCommonName(4, ap_model_id, ap_role_id, description, ap_type)
    test_params = getTestParams(default_test_params.copy())
    test_params['acct_info']['svr_info'] = '192.168.0.160'
    test_params['test_feature'] = 'invalid_accounting_server_info'
    test_params_list.append((test_params, common_name))

    description = 'Interrim udpate time'
    common_name = getCommonName(6, ap_model_id, ap_role_id, description, ap_type)
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'interim_update'
    test_params_list.append((test_params, common_name))

    description = 'Accounting trap when client associated/dissociate'
    common_name = getCommonName(8, ap_model_id, ap_role_id, description, ap_type)
    test_params = getTestParams(default_test_params.copy())
    test_params['test_feature'] = 'sta_join_leave'
    test_params_list.append((test_params, common_name))

    return test_params_list

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs['interactive_mode']:
        while True:
            target_station = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
            if target_station: break
            print "Pick at least one station as your target"

        showNotice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_station = sta_ip_list[attrs["sta_id"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    test_cfgs = []
    for active_ap in active_ap_list:
        test_cfgs.extend(defineTestParams(active_ap, ap_sym_dict[active_ap], target_station))

    test_order = 1
    test_added = 0
    test_name = 'ZD_Accounting'
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    ts_description = 'Test Zone Director\'s Accounting Functionality'
    ts = testsuite.get_testsuite('ZD_Accounting', ts_description, interactive_mode = attrs["interactive_mode"])

    for test_params, common_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
