import sys

import libZD_TestSuite as testsuite
import RuckusAutoTest.common.lib_Debug as bugme
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(base_id, target_sta_radio, model_id=None):
    if model_id:
        return u'TCID:04.05.%02d.%d.%d' % (base_id, model_id, const.get_radio_id(target_sta_radio))
    else: return u'TCID:04.05.%02d.%d' % (base_id, const.get_radio_id(target_sta_radio))

# each test_params is a tuple with 2 elemens: (<test_params dict>, <TCID>)
def makeTestParameter(target_sta_radio):
    test_params = {}
    _base_id = 1
    test_params[1] = (dict(test_option = 'diff_encrypt'),
                      {'none':_tcid(_base_id, target_sta_radio)})
    _base_id = 2
    test_params[2] = (dict(test_option = 'wep_encrypt'),
                      {'none':_tcid(_base_id, target_sta_radio)})
    _base_id = 2
    tcid_base_ap_model = {}
    for ap_model in const.get_all_ap_model_id():
        if ap_model[0] != 'none': tcid_base_ap_model[ap_model[0]] = _tcid(_base_id, target_sta_radio, ap_model[1])
    test_params[3] = (dict(test_option = 'specific_ap'), tcid_base_ap_model)

    return test_params

def getCommonName(tcid, test_param, ap_model = ''):
    common_name = '%s - WLAN Options - %d BSSIDs: %s'
    desc = 'N/A'
    if test_param['test_option'] == 'diff_encrypt':
        desc = 'verify with different encryption types'
    elif test_param['test_option'] == 'wep_encrypt':
        desc = 'verify with WEP encryptions'
    else:
        desc = 'verify on %s' % ap_model

    return common_name % (tcid, test_param['number_bssid'], desc)

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
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        number_bssid = raw_input('By default, the test applies for 8 BSSIDs. Choice another number: (Enter to skip)')
        try:
            number_bssid = int(number_bssid)
        except:
            number_bssid = 8
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]
        number_bssid = 8

    testsuite_name = 'WLAN Options - %d BSSIDs' % number_bssid
    testsuite_desc = 'Verify the wlan options for %d BSSIDs on the ZD.' % number_bssid

    if attrs["testsuite_name"]: testsuite_name = attrs["testsuite_name"]
    else: testsuite_name = "WLAN Options - %d BSSIDs" % number_bssid
    ts = testsuite.get_testsuite(testsuite_name, testsuite_desc, interactive_mode = attrs["interactive_mode"])
    test_ap_models = getApModelList(ap_sym_dict)
    test_params = makeTestParameter(target_sta_radio)
    test_name = 'ZD_Wlan_Option_8BSSIDs'

    test_order = 0
    test_added = 1

    for test_param, test_id in test_params.itervalues():
        #Add test case to test vlan on WebAuth enabled wlan without any specific AP model.
        test_param['number_bssid'] = number_bssid
        test_param['target_station'] = target_sta
        test_param['target_sta_radio'] = target_sta_radio
        if test_param['test_option'] != 'specific_ap':
            testcase_id = test_id['none']
            common_name = getCommonName(testcase_id, test_param)
            if testsuite.addTestCase(ts, test_name, common_name, test_param, test_order) > 0:
                test_added += 1
            test_order += 1

        else:
            for ap_model in test_ap_models:
                test_param['active_ap'] = getActiveAPByModel(ap_model, ap_sym_dict)
                testcase_id = test_id[ap_model]
                common_name = getCommonName(testcase_id, test_param, ap_model)

                if testsuite.addTestCase(ts, test_name, common_name, test_param, test_order) > 0:
                    test_added += 1
                test_order += 1

        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

