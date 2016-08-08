import sys
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

pp = pprint.PrettyPrinter(indent=4)

def getDescription(id , sta_os = '', sta_radio = '', ap_radio = ''):
    description_list = [
        'Download the SpeedFlex into %s laptop and check performance test' % sta_os,
        'SpeedFlex running with 11%s client associated to 11%s AP' % (sta_radio, ap_radio),
    ]

    return description_list[id]

def getCommonName(id, description):
    return "TCID:25.01.%02d - %s" % (id, description)

def showNotice():
    msg = "Please select one 11g AP and one 11n AP for test (separate by space)"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def get_wlan_cfg(ssid, wlan_params):
    wlan_cfg = dict(
        auth = 'open',
        encryption = 'none',
        ssid = 'rat-accounting'
    )

    wlan_cfg.update(wlan_params)
    return wlan_cfg

def getTestParams(params):
    test_params = dict(
        wlan_cfg = get_wlan_cfg('rat-speedflex', {}),
        target_station = '',
        active_ap = '',
        testcase = '',
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
        print "Pick one station as your target"
    sta_os = raw_input("Select Station Operation System (\"XP\" or \"Vista\") [enter = \"XP\"]: ")
    if sta_os.strip() == "":
        sta_os = "XP"

    sta_radio = raw_input("Select Radio Mode of Wireless Station (\"g\" or \"n\") [enter = \"g\"]: ")
    if sta_radio.strip() == "":
        sta_radio = "g"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]
    ap_radio = 'g'
    default_test_params = dict(
        target_station = target_station,
        active_ap = active_ap,
        sta_radio = sta_radio,
        sta_os = sta_os,
        ap_radio = ap_radio
    )

    test_order = 1
    test_added = 0
    test_name = 'ZD_SpeedFlex'
    ts_description = 'Test Zone Director\'s SpeedFlex Functionality'
    speedflex_ts = testsuite.get_testsuite('ZD_SpeedFlex_Windows%s_11%s_Client' % (sta_os, sta_radio), ts_description)
    for i in [0,1,1]:
        description = getDescription(i, sta_os, sta_radio, ap_radio)
        test_params = default_test_params.copy()
        if i == 0:
            test_params['testcase'] = 'test_download'
            if sta_os == 'Vista': common_name = getCommonName(1, description)
            else: common_name = getCommonName(2, description)
        if i == 1:
            test_params['testcase'] = 'test_running'
            if test_added > 1:
                ap_radio = 'n'
                test_params['active_ap'] = active_ap_list[1]
                test_params['ap_radio'] = ap_radio
                description = getDescription(i, sta_os, sta_radio, ap_radio)
            if sta_radio == 'g': common_name = getCommonName(4, description)
            else: common_name = getCommonName(5, description)

        testsuite.addTestCase(speedflex_ts, test_name, common_name, getTestParams(test_params), test_order)
        test_added = test_added + 1
        test_order = test_order + 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, speedflex_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
