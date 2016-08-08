import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

_TC_TEST_NAME = 'ZD_WLAN_Options_Hide_SSID'

def _tcid(baseId, description, ap_model=None):
    if ap_model:
        aptcid = const.get_ap_model_id(ap_model)
        ap_model = ap_model.upper()
        return u'TCID:04.04.%02d.%02d - %s - %s' % (baseId, aptcid, description, ap_model)
    else:
        return u'TCID:04.04.%02d - %s' % (baseId, description)

def makeTestConfig1(target_sta):
    test_cfgs = [
        (   {   'test_option': 'hide ssid',
                'target_station': target_sta},
            _TC_TEST_NAME,
            _tcid(1, "WLAN Options - Hide SSID: enable hide SSID")),
        (   {   'test_option': 'show ssid',
                'target_station': target_sta},
            _TC_TEST_NAME,
            _tcid(1, "WLAN Options - Hide SSID: dsiable hide SSID")),
        
    ]
    return test_cfgs

def makeTestConfig2(target_sta, target_sym_ap, ap_model):
    test_cfgs = [
        (   {   'test_option': 'specific_ap',
                'target_station': target_sta,
                'active_ap': target_sym_ap},
            _TC_TEST_NAME,
            _tcid(1, "WLAN Options - Hide SSID: verify on AP", ap_model)),
    ]
    return test_cfgs

def showNotice():
    msg = "Enter list of APs to be tested. Same model of AP will be skipped."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def make_test_suite(**kwargs):
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    target_sta = testsuite.getTargetStation(sta_ip_list)
    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    ts = testsuite.get_testsuite('WLAN Options - Hide SSID',
                      'Verify Hide SSID options on Zone Director.')

    test_order = 1
    test_added = 1
    for test_param, test_name, common_name in makeTestConfig1(target_sta):
        if testsuite.addTestCase(ts, test_name, common_name, test_param, test_order) > 0:
            test_added += 1
        test_order += 1

    for target_sym_ap in active_ap_list:
        active_ap = ap_sym_dict[target_sym_ap]
        for test_param, test_name, common_name in makeTestConfig2(target_sta, target_sym_ap, active_ap['model']):
            if testsuite.addTestCase(ts, test_name, common_name, test_param, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

 
if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)

