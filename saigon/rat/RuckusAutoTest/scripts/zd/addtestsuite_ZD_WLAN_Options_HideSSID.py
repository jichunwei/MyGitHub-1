import sys
import time
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(base_id, model_id=None):
    if model_id:
        return u'TCID:04.04.%02d.%d' % (base_id, model_id)
    else: return u'TCID:04.04.%02d' % (base_id)

# each test_params is a tuple with 2 elemens: (<test_params dict>, <TCID dict>)
def makeTestParameter():
    test_params = {}
    ssid = "rat-hide-bssid-%s" % time.strftime("%H%M%S")
    _base_id = 1
    test_params[1] = ({'test_option': 'hide ssid'},
                      {'hide ssid': _tcid(_base_id), 'show ssid': _tcid(_base_id+1)})

    test_params[2] = ({'test_option': 'show ssid'},
                      {'hide ssid': _tcid(_base_id), 'show ssid': _tcid(_base_id+1)})

    tcid_base_ap_model = {}
    for ap_model in const.get_all_ap_model_id():
        if ap_model[0] != 'none': tcid_base_ap_model[ap_model[0]] = _tcid(_base_id, ap_model[1])

    test_params[3] = ({'test_option': 'specific_ap'},tcid_base_ap_model)

    return test_params

def getCommonName(tcid, test_param, ap_model = ''):
    common_name = '%s - WLAN Options - Hide SSID: %s'
    desc = 'N/A'
    if test_param['test_option'] == 'hide ssid':
        desc = 'enable hide SSID'
    if test_param['test_option'] == 'show ssid':
        desc = 'disable hide SSID'
    if test_param['test_option'] == 'specific_ap':
        desc = 'verify on %s' % ap_model

    return common_name % (tcid, desc)

def getActiveAPByModel(ap_model, ap_sym_dict):
    """
    Return the first appropriate AP symbolic name in dict which model is 'ap_model'
    """
    for ap_name in ap_sym_dict.keys():
        if ap_sym_dict[ap_name]['model'] == ap_model:
            return ap_name

    return None

def getApModelList(ap_sym_dict):
    ap_model_list = []
    for ap in ap_sym_dict.itervalues():
        if ap['model'] not in ap_model_list:
            ap_model_list.append(ap['model'])

    return sorted(ap_model_list)

def make_test_suite(**kwargs):
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    target_sta = testsuite.getTargetStation(sta_ip_list)

    ts = testsuite.get_testsuite('WLAN Options - Hide SSID',
                      'Verify Hide SSID options on Zone Director.')
    test_ap_models = getApModelList(ap_sym_dict)
    test_params = makeTestParameter()
    test_name = 'ZD_WLAN_Options_Hide_SSID'

    test_order = 1
    test_added = 0
    for test_param, test_id in test_params.itervalues():
        #Add test case to test vlan on WebAuth enabled wlan without any specific AP model.
        test_param['target_station'] = target_sta
        if test_param['test_option'] != 'specific_ap':
            testcase_id = test_id[test_param['test_option']]
            common_name = getCommonName(testcase_id, test_param)
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1
        else:
            for ap_model in test_ap_models:
                test_order += 1
                test_param['active_ap'] = getActiveAPByModel(ap_model, ap_sym_dict)
                testcase_id = test_id[ap_model]
                common_name = getCommonName(testcase_id, test_param, ap_model)
                if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)


def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def make_test_suite_on_ap(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        showNotice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "WLAN Options - Hide SSID"
    ts = testsuite.get_testsuite(ts_name,
                      'Verify Hide SSID options on Zone Director.',
                      interactive_mode = attrs["interactive_mode"])
    test_cfgs = makeTestParameter()
    test_name = 'ZD_WLAN_Options_Hide_SSID'

    test_order = 1
    test_added = 0
    for test_params, test_id in test_cfgs.itervalues():
        #Add test case to test vlan on WebAuth enabled wlan without any specific AP model.
        test_params['target_station'] = target_sta
        test_params['target_sta_radio'] = target_sta_radio
        if test_params['test_option'] != 'specific_ap':
            testcase_id = test_id[test_params['test_option']]
            testcase_id = "%s.%d" % (testcase_id, const.get_radio_id(target_sta_radio))
            common_name = getCommonName(testcase_id, test_params)
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

        else:
            #Add test case to test vlan on WebAuth enabled wlan with specific AP model.
            for ap_id in active_ap_list:
                active_ap = ap_sym_dict[ap_id]
                if re.search('mesh', active_ap['status']):
                    print "By design, skip mesh AP [%s %s]" % (ap_id, ap_sym_dict[ap_id])
                    continue
                ap_model = active_ap['model']
                testcase_id = test_id[ap_model]
                testcase_id = "%s.%d" % (testcase_id, const.get_radio_id(target_sta_radio))
                test_params['active_ap'] = ap_id; # NOT active_ap
                common_name = getCommonName(testcase_id, test_params, ap_model)
                if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    if _dict.has_key('oldtc') and _dict['oldtc']:
        make_test_suite(**_dict)
    else:
        make_test_suite_on_ap(**_dict)

