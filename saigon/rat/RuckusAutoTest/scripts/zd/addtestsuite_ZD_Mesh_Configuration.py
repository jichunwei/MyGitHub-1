import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(baseId, offId):
    return u'TCID:10.03.%02d' % (baseId + offId)

def defineTestID(base_id):
    test_id_list = dict()
    for model, model_id in const._ap_model_id.items():
        test_id_list[model] = tcid(model_id, base_id) 
        
    return  test_id_list    


# each test_params is a tuple with 2 elemens: (<test_params dict>, <TCID dict>)
def getTestCfg():
    # open wlan
    wlan_1 = dict(ssid = 'Open-None', auth = "open", encryption = "none")

    # Open-WEP-128
    wlan_2 = dict(ssid = 'Open-WEP-128', auth = "open", encryption = "WEP-128",
                  key_index = "1" , key_string = utils.make_random_string(26, "hex"))

    # Shared-WEP-64
    wlan_3 = dict(ssid = 'Shared-WEP-64', auth = "shared", encryption = "WEP-64",
                  key_index = "1" , key_string = utils.make_random_string(10, "hex"))

    # WPA-PSK-TKIP
    wlan_4 = dict(ssid = 'WPA-PSK-TKIP', auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                  sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                  key_string = utils.make_random_string(random.randint(8, 63), "hex"))

    # WPA2-PSK-AES
    wlan_5 = dict(ssid = 'WPA2-PSK-AES', auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                  sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                  key_string = utils.make_random_string(random.randint(8, 63), "hex"))

    test_wlan_list = [wlan_1, wlan_2, wlan_3, wlan_4, wlan_5]

    test_params = {}
    baseId = 0
    test_params[1] = (dict(test_wlan_list = test_wlan_list, test_topology = 'root'),
                      defineTestID(baseId))
    baseId = 1
    test_params[2] = (dict(test_wlan_list = test_wlan_list, test_topology = 'root-map'),
                      defineTestID(baseId))

    return test_params

def getCommonName(tcid, model, topo):
    common_name = 'Mesh %s - Configuration propagation to %s %s.' % (tcid, model.upper(), topo.upper())
    return common_name

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
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
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
        target_sta_radio = attrs["station"][1]

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'Mesh Configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify the ability of the ZD to deploy configuration to the whole mesh tree',
                      interactive_mode = attrs["interactive_mode"])

    test_cfgs = getTestCfg()
    test_order = 1
    test_added = 0
    test_name = 'ZD_Mesh_Configuration'
    test_ap_model_list = testsuite.get_ap_modelList(ap_sym_dict.itervalues())

    for model in test_ap_model_list:
        for test_params, test_id in test_cfgs.itervalues():
            test_params['test_ap_model'] = model
            test_params['target_sta_radio'] = target_sta_radio
            testcase_id = test_id[model]
            common_name = getCommonName(testcase_id, model, test_params['test_topology'])
            
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

