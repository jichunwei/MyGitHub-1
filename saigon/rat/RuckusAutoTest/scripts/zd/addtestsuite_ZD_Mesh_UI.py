import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _tcid(base_id, description):
    return u"TCID:10.01.%02d - %s" % (base_id, description)

def defineTestConfiguration():
    test_cfgs = list()

    test_cfgs.append((dict(), "ZD_Mesh_WebUI_Enable", _tcid(3,"Enable Mesh on WebUI")))
    test_cfgs.append((dict(model="", topology="", verify_ssid=True, verify_passphrase=False),
                     "ZD_Mesh_WebUI_Configuration", _tcid(5,"Verify mesh SSID configuration over webUI")))

    test_cfgs.append((dict(model="", topology="", verify_ssid=False, verify_passphrase=True),
                     "ZD_Mesh_WebUI_Configuration", _tcid(6, "Verify mesh pass-phrase configuration over webUI")))

    makeWebUiModelTestConfig(test_cfgs, 'zf2925', [7, 8, 11,12,31,34,35,58,59,64,65])
    makeWebUiModelTestConfig(test_cfgs, 'zf2942', [15,16,19,20,32,38,39,60,61,66,67])
    makeWebUiModelTestConfig(test_cfgs, 'zf7942', [23,24,27,28,33,42,43,62,63,68,69])
    makeWebUiModelTestConfig(test_cfgs, 'zf2741', [81,82,85,86,87,88,89,90,91,92,93])

    test_cfgs.append((dict(), "ZD_Mesh_WebUI_Setup_Wizard", _tcid(73, "Run Setup Wizard Configuration to enable Mesh")))

    return test_cfgs

# makeWebUiModelTestConfig(test_cfgs, 'zf2741', [81,82,85,86,87,88,89,90,91,92,93])
def makeWebUiModelTestConfig(test_cfgs, model, tcidlist=[81,82,85,86,87,88,89,90,91,92,93]):
    _Model = model.upper()

    test_cfgs.append((dict(model=model, topology="root", verify_ssid=True, verify_passphrase=False),
                    "ZD_Mesh_WebUI_Configuration",
                    _tcid(tcidlist[0], "Verify mesh SSID configuration on %s ROOT" % _Model)))
    test_cfgs.append((dict(model=model, topology="root-mesh", verify_ssid=True, verify_passphrase=False),
                    "ZD_Mesh_WebUI_Configuration",
                    _tcid(tcidlist[1], "Verify mesh SSID configuration on %s MESH1" % _Model)))
    test_cfgs.append((dict(model=model, topology="root", verify_ssid=False, verify_passphrase=True),
                    "ZD_Mesh_WebUI_Configuration",
                    _tcid(tcidlist[2], "Verify mesh pass-phrase configuration on %s ROOT" % _Model)))
    test_cfgs.append((dict(model=model, topology="root-mesh", verify_ssid=False, verify_passphrase=True),
                    "ZD_Mesh_WebUI_Configuration",
                    _tcid(tcidlist[3], "Verify mesh pass-phrase configuration on %s MESH1" % _Model)))
    test_cfgs.append((dict(model=model), "ZD_Mesh_WebUI_Self_Status",
                    _tcid(tcidlist[4], "Verify self status of AP %s" % _Model)))
    test_cfgs.append((dict(model=model, topology="root"), "ZD_Mesh_WebUI_Neighbor_Status",
                      _tcid(tcidlist[5], "Verify neighbor status of AP %s ROOT" % _Model)))
    test_cfgs.append((dict(model=model, topology="root-mesh"), "ZD_Mesh_WebUI_Neighbor_Status",
                      _tcid(tcidlist[6], "Verify neighbor status of AP %s MESH1" % _Model)))
    test_cfgs.append((dict(model=model, topology="root"), "ZD_Mesh_WebUI_Change_Channel",
                      _tcid(tcidlist[7], "Change channel of AP %s ROOT" % _Model)))
    test_cfgs.append((dict(model=model, topology="root-mesh"), "ZD_Mesh_WebUI_Change_Channel",
                      _tcid(tcidlist[8] ,"Change channel of AP %s MESH1" % _Model)))
    test_cfgs.append((dict(model=model, topology="root"), "ZD_Mesh_WebUI_Change_TxPower",
                      _tcid(tcidlist[9], "Change TxPower of AP %s ROOT" % _Model)))
    test_cfgs.append((dict(model=model, topology="root-mesh"), "ZD_Mesh_WebUI_Change_TxPower",
                      _tcid(tcidlist[10], "Change TxPower of AP %s MESH1" % _Model)))

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)

    # TAK/JLEE@20081125
    #      Using tesbed's ap_sym_dict to generate zf2741 testcases if it exists
    _dict = {}
    _dict.update(**kwargs)
    mtb = testsuite.getMeshTestbed(**_dict)
    tbcfg = testsuite.getTestbedConfig(mtb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    test_ap_model_list = testsuite.get_ap_modelList(ap_sym_dict.itervalues())

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'Mesh WebUI'
    ts = testsuite.get_testsuite(ts_name, "Verify Mesh WebUI Configuration", interactive_mode = attrs["interactive_mode"])

    test_cfgs = defineTestConfiguration()

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        if test_params.has_key('model') and test_params['model'] and (not test_params['model'] in test_ap_model_list):
            # print "Skip model %s" % test_params['model']
            continue
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
    
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
