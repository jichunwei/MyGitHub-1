import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(baseId, offId, sta_radio):
    return u'TCID:05.01.01.%02d.%d' % (baseId + offId, const.get_radio_id(sta_radio))

# each test_params is a tuple with 2 elements: (<test_params dict>, <TCID>)
def makeTestParameter(sta_radio):
    test_params = {}
    _base_id = 0
    test_params[1] = (dict(ip = "20.0.2.252/255.255.255.0", vlan_id = "2", use_valid_id = True),
                      _tcid(_base_id, 1, sta_radio))
    _base_id = 2
    test_params[2] = (dict(ip = "", vlan_id = "1", use_valid_id = False),
                      _tcid(_base_id, 1, sta_radio))
    _base_id = 3
    test_params[3] = (dict(ip = "20.0.2.252/255.255.255.0", vlan_id = "2", use_valid_id = True),
                      _tcid(_base_id, 1, sta_radio))
    _base_id = 4
    test_params[4] = (dict(ip = "20.15.254.252/255.255.255.0", vlan_id = "3677", use_valid_id = True),
                      _tcid(_base_id, 1, sta_radio))
    _base_id = 5
    test_params[5] = (dict(ip = "", vlan_id = "4095", use_valid_id = False),
                      _tcid(_base_id, 1, sta_radio))

    return test_params

def getCommonName(tcid, test_param):
    common_name = '%s - VLAN Configuration: %s'
    desc = ''
    if tcid[-1] == u'1':
        desc = 'Create VLAN and verify the client traffic'
    else:
        desc = 'test VLAN %s' if test_param['use_valid_id'] else 'test invalid VLAN %s'
        desc = desc % test_param['vlan_id']

    return common_name % (tcid, desc)

# Add test suite
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = "VLAN Configuration"
    )
    attrs.update(kwargs)

    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]    
    ts = testsuite.get_testsuite(ts_name,
                      'Verify different VLAN configuration on Zone Director.',
                      interactive_mode = attrs["interactive_mode"])

    test_cfgs = makeTestParameter(target_sta_radio)
    test_name = 'ZD_VLAN_Configuration'

    test_order = 1
    test_added = 0
    for test_params, test_id in test_cfgs.itervalues():
        test_order += 1
        testcase_id = test_id
        test_params['target_station'] = target_sta
        test_params['target_sta_radio'] = target_sta_radio
        common_name = getCommonName(testcase_id, test_params)
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

