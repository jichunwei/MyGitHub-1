import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

# AP's model and its reference ID are defined at common/lib_Constant.py
# via module const which is defined at libZD_TestSuite.py
def tcid(baseId, description, ap_model=None):
    if ap_model:
        aptcid = const.get_ap_model_id(ap_model)
        ap_model = ap_model.upper()
        return u'TCID:05.01.02.%02d.%02d - %s - %s' % (baseId, aptcid, description, ap_model)
    else:
        return u'TCID:05.01.02.%02d - %s' % (baseId, description)

# retrun list of tuple(test_param, common_name)
def get_test_cfg1(target_sta):
    test_cfgs = \
    [  (  dict(  ip='20.0.2.252/255.255.255.0',
                 target_station=target_sta,
                 vlan_id='2'),
          tcid(1, 'VLAN Cnfiguration - Guest Access - test Vlan on Guest Access enabled Wlan'))
    ]
    return test_cfgs

# AP specific test cases
# retrun list of tuple(test_param, common_name)
def get_test_cfg2(target_sta, ap_sym_id, ap_model):
    test_cfgs = \
    [  (  dict(  ip='20.0.2.252/255.255.255.0',
                 target_station=target_sta,
                 active_ip=ap_sym_id,
                 vlan_id='2'),
          tcid(2, 'VLAN Cnfiguration - Guest Access - verify on vlan 2', ap_model))
    ]
    return test_cfgs

def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def make_test_suite(**kwargs):
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    target_sta = testsuite.getTargetStation(sta_ip_list)

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    ts = testsuite.get_testsuite('VLAN Configuration - Guest Access',
                      'Verify the feature VLAN configuration - Guest access.')
    test_name = 'ZD_VLAN_GuestAccess'

    test_order = 1
    test_added = 0
    for test_params, common_name in get_test_cfg1(target_sta): 
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    for ap_sym_id in active_ap_list:
        active_ap = ap_sym_dict[ap_sym_id]
        for test_params, common_name in get_test_cfg2(target_sta, ap_sym_id, active_ap['model']): 
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)


if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)


