import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _tcid(base_id, description):
    return u"Mesh TCID:10.04.%02d -%s" % (base_id, description)

def defineTestConfiguration():
    test_cfgs = list()

    test_cfgs.append(({'rap_model':'zf2925', 'map_model':'zf2925', 'topology':'root-mesh', 'channelization':''},
                      _tcid(1, "Verify mesh forming using ZF2925 ROOT-MAP"),))
    test_cfgs.append(({'rap_model':'zf2942', 'map_model':'zf2942', 'topology':'root-mesh', 'channelization':''},
                      _tcid(4, "Verify mesh forming using ZF2942 ROOT-MAP"),))
    test_cfgs.append(({'rap_model':'zf7942', 'map_model':'zf7942', 'topology':'root-mesh', 'channelization':'20'},
                      _tcid(7, "Verify mesh forming using ZF7942 20Mhz ROOT-MAP"),))
    test_cfgs.append(({'rap_model':'zf7942', 'map_model':'zf7942', 'topology':'root-mesh', 'channelization':'40'},
                      _tcid(10, "Verify mesh forming using ZF7942 40Mhz ROOT-MAP"),))
    test_cfgs.append(({'rap_model':'zf7942', 'map_model':'zf2925', 'topology':'root-mesh', 'channelization':''},
                      _tcid(16, "Verify mesh cannot form using ZF2925 with ZF7942 ROOT"),))
    test_cfgs.append(({'rap_model':'zf7942', 'map_model':'zf2942', 'topology':'root-mesh', 'channelization':''},
                      _tcid(18, "Verify mesh cannot form using ZF2942 with ZF7942 ROOT"),))
    test_cfgs.append(({'rap_model':'zf2925', 'map_model':'zf7942', 'topology':'root-mesh', 'channelization':''},
                      _tcid(20, "Verify mesh cannot form using ZF7942 with ZF2925 ROOT"),))
    test_cfgs.append(({'rap_model':'zf2942', 'map_model':'zf7942', 'topology':'root-mesh', 'channelization':''},
                      _tcid(22, "Verify mesh cannot form using ZF7942 with ZF2942 ROOT"),))
    test_cfgs.append(({'rap_model':'zf2741', 'map_model':'zf2741', 'topology':'root-mesh', 'channelization':''},
                      _tcid(24, "Verify mesh forming using ZF2741 ROOT-MAP"),))
    test_cfgs.append(({'rap_model':'zf7942', 'map_model':'zf2741', 'topology':'root-mesh', 'channelization':''},
                      _tcid(27, "Verify mesh cannot form using ZF2741 with ZF7942 ROOT"),))
    test_cfgs.append(({'rap_model':'zf2741', 'map_model':'zf7942', 'topology':'root-mesh', 'channelization':''},
                      _tcid(29, "Verify mesh cannot form using ZF7942 with ZF2942 ROOT"),))

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name = ""
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
    _dict['zf2741'] = True if 'zf2741' in test_ap_model_list else False

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'Mesh Forming'
    ts = testsuite.get_testsuite(ts_name,
                      "Verify the ability of the ZD to instruct the APs to form mesh",
                      interactive_mode = attrs["interactive_mode"])
    test_order = 1
    test_added = 0
    test_name = "ZD_Mesh_Forming"
    for test_params, common_name in defineTestConfiguration():
        if test_params['map_model'] in test_ap_model_list and test_params['rap_model'] in test_ap_model_list:
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

