import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
   
#@autor: Tanshixiong @since 20150312 zf-12345
def tcid(base_id, description, ap_model=None ,ap_tag=None):
    if ap_model:
        aptcid = const.get_ap_model_id(ap_model)    
        return u"TCID:01.01.02.%02d.%02d - %s -%s" % (base_id, aptcid, description, str(ap_tag))
    else:
        return u"TCID:01.01.02.%02d.%02d - %s " % (base_id, 0, description)

def get_test_cfg1():
    test_cfgs = [
        (   {'auto_approval':'True'},
            "ZD_AP_Approval",
             tcid(1, "Automatic AP Approval")),
        (   {'auto_approval':'False'},
            "ZD_AP_Approval",
            tcid(2, "Manual AP Approval"))
    ]
    return test_cfgs

def get_test_cfg2( ap_model, ap_pair):
    ap_sym_name = ap_pair[0]
    test_cfgs = [
        (   {'auto_approval':'True', 'active_ap':ap_sym_name},
            "ZD_AP_Join",
            #@autor: Tanshixiong @since 20150312 zf-12345
            tcid(3, "AP joins", ap_model, str(ap_sym_name)))
    ]
    if len(ap_pair) == 2:
        test_cfgs.extend( [
            (   {   'is_ap_join_after_change':False,
                    'locked_ap': ap_pair[0],
                    'nonlocked_ap': ap_pair[1]},
                "ZD_AP_Country_Code",
                #@autor: Tanshixiong @since 20150312 zf-12345
                tcid(6, "Change country code before AP join", ap_model, str(ap_pair[1]))),
            (   {   'is_ap_join_after_change':True,
                    'locked_ap': ap_pair[1],
                    'nonlocked_ap': ap_pair[0]},
                "ZD_AP_Country_Code",
                #@autor: Tanshixiong @since 20150312 zf-12345
                tcid(7, "Change country code after AP join", ap_model, str(ap_pair[1])))
        ] )
    return test_cfgs

def showNotice():
    msg = "Enter list of APs in pair. Example: AP_01 AP_02 AP_05 AP_06"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    ts = testsuite.get_testsuite("System - AP Control",
                      "Verify the ability of the ZD to control the joinings of different AP types")

    test_cfgs = get_test_cfg1()

    showNotice()
    active_ap_pair_list = testsuite.getActiveApByModel(ap_sym_dict)
    for (ap1, ap2) in active_ap_pair_list:
        ap_model = ap_sym_dict[ap1]['model']
        test_cfgs.extend( get_test_cfg2(ap_model, (ap1, ap2)) )
    
    test_order = 0
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        test_order += 1
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)


if __name__ == '__main__':
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)

