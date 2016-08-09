import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(id, description):
    return "TCID:15.01.%02d - %s" % (id, description)

def getTestParams(test_feature, kwargs = {}):
    test_params = {'test_feature': test_feature, 'max_wgs':1,
                   'target_ip': '192.168.0.252',
                   'wgs_cfg': {'name': 'rat-wlan-group',
                               'description': 'rat-wlan-group'}}
    test_params.update(kwargs)
    return test_params

def getDefaultParams():
    default_params = {'max_wgs': 31,
                      'clone_name': 'rat-wlan-group-cloned',
                      'new_description':'new wlangroup description',
                      'target_ip': '192.168.0.252'
                      }
    return default_params

def getCustomParam(params_name, default_value, msg, isNumber = False):
    custom_param = raw_input("%s: [enter = '%s'] " % (msg, default_value))
    try:
        if isNumber:
            if custom_param.strip(): custom_param = int(custom_param)
            else: custom_param = default_value
        else:
            if custom_param.strip(): custom_param = custom_param.strip()
            else: custom_param = default_value
    except:
        print 'Invalid value! The test will use the default value: %d' % default_value

    return custom_param

def getWlanGroupTestParams(ap_list, target_station, **kwargs):
    default_params = getDefaultParams()
    default_params.update(kwargs)

    test_params_list = \
    [
        getTestParams('max_wlan_group',{'max_wgs' : default_params['max_wgs'], 'ap_list' : ap_list, 'target_station' : target_station}),
        getTestParams('clone_wlan_group',{'clone_name': default_params['clone_name'], 'ap_list': ap_list, 'target_station': target_station}),
        getTestParams('edit_wlangroup_description', {'new_description': default_params['new_description'],'ap_list': ap_list, 'target_station': target_station}),
        getTestParams('edit_wlan_member', {'ap_list': ap_list, 'target_station': target_station})
    ]
    return test_params_list

def getWlanGroupCommName(test_order):
    common_name_list = \
    [    '', # skip index 0
         tcid(test_order,'Create/Delete 32 WLAN Groups'),
         tcid(test_order,'Clone Wlan Groups'),
         tcid(test_order,'Edit Wlan Group description'),
         tcid(test_order,'Create/Delete the WlAN of WLAN Groups')
    ]
    return common_name_list[test_order]

def showNotice():
    msg = "Please select 2 APs under test (separate by comma)"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    while True:
        target_station = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        if target_station: break
        print "Pick at least one station as your target"

    showNotice()
    ap_list = testsuite.getActiveAp(ap_sym_dict)
    print ap_list

    test_name = 'ZD_WLAN_Groups'
    ts_description = 'Verify Basic feature of WLAN Group on ZD working properly'
    test_order = 1
    test_added = 0
    wlangroup_ts = testsuite.get_testsuite('ZD_WLAN_Groups', ts_description)

    default_params = getDefaultParams()
    for key in default_params.keys():
        if key == "max_wgs":
            default_params[key] = getCustomParam(key, default_params[key], "Enter '%s' value" % key, True)
        else:
            default_params[key] = getCustomParam(key, default_params[key], "Enter '%s' value" % key)

    test_params_list = getWlanGroupTestParams(ap_list, target_station, **default_params)

    for i in range(len(test_params_list)):
        common_name = getWlanGroupCommName(test_order)
        test_params = test_params_list[i]
        testsuite.addTestCase(wlangroup_ts, test_name, common_name, test_params, test_order)
        test_added = test_added + 1
        test_order = test_order + 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, wlangroup_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
