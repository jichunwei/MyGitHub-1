import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(baseId, offId):
    return u'TCID:10.02.%02d' % (baseId + offId)

def defineTestID(base_id):
    test_id_list = dict()
    for model, model_id in const._ap_model_id.items():
        test_id_list[model] = _tcid(model_id, base_id)

    return  test_id_list

# each test_params is a tuple with 2 elemens: (<test_params dict>, <TCID dict>)
def getTestCfg():
    test_params = {}
    _baseId = 0
    test_params[1] = (dict(expected_process='provisioning'), defineTestID(_baseId))
    _baseId = 6
    test_params[2] = (dict(expected_process='become root'), defineTestID(_baseId))
    _baseId = 9
    test_params[3] = (dict(expected_process='become mesh'), defineTestID(_baseId))

    return test_params

def getCommonName(tcid, model, process):
    msg = 'through ethernet' if process == 'provisioning' else 'after provisioning'
    common_name = 'Mesh %s - AP[%s] %s %s' % (tcid, model.upper(), process, msg)
    return common_name

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)

    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'Mesh Provisioning'
    ts = testsuite.get_testsuite(ts_name, 'Verify Mesh provisioning process', interactive_mode = attrs["interactive_mode"])

    test_cfgs = getTestCfg()
    test_order = 1
    test_added = 0
    test_name = 'ZD_Mesh_Provisioning'
    test_ap_model_list = testsuite.get_ap_modelList(ap_sym_dict.itervalues())

    for model in test_ap_model_list:
        for test_params, test_id in test_cfgs.itervalues():
            test_order += 1
            test_params['test_ap_model'] = model
            #test_params['target_sta_radio'] = target_sta_radio
            testcase_id = test_id[model]
            common_name = getCommonName(testcase_id, model, test_params['expected_process'])
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)

