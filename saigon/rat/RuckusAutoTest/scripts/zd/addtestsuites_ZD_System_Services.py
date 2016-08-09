import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const
import RuckusAutoTest.common.lib_Debug as bugme

def tcid(base_id, ap_model_id = None, ap_role_id = None):
    if ap_model_id:
        return u"TCID:01.01.03.%02d.%s.%s" % (base_id, ap_model_id, ap_role_id)
    else:
        return u"TCID:01.01.03.%02d" % (base_id)
   
def getCommonName(tcid, test_desc, ap_tag=None):
    if ap_tag:  
        return u"%s - %s -%s" % (tcid, test_desc,ap_tag) 
    else:
        return u"%s -%s" % (tcid, test_desc)   


#@author: Tanshixiong @since: 20150312 ZF-12345
def makeTestParams(target_ap = None, ap_model_id = None, ap_role_id = None):    
    test_params = []

    if target_ap:
        test_params.append(({'target_ap': target_ap},
                            "ZD_System_NTP",
                            tcid(2, ap_model_id, ap_role_id),
                            "NTP - AP side"))
        #@author: Tanshixiong @since: 20150312 ZF-12345
#        test_params.append(({'target_ap': target_ap},
#                            "ZD_System_Syslog",
#                            tcid(4, ap_model_id, ap_role_id),
#                            "Syslog - AP side"))
    else:
        test_params.append(({},
                            "ZD_System_NTP",
                            tcid(1),
                            "NTP - ZD side"))
        test_params.append(({},
                            "ZD_System_Syslog",
                            tcid(3),
                            "Syslog - ZD side"))
        #@author: Tanshixiong @since: 20150312 ZF-12345 
#        test_params.append(({'email_to':'rattest@example.net', 'timeout':300},
#                            "ZD_System_Alarm_Mail",
#                            tcid(5),
#                            "Generation Arlam Email"))

    return test_params

def showNotice(msg = "Please select the APs under test. Only RootAP if your testbed is meshed."):
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "System - Services"
    ts = testsuite.get_testsuite(ts_name,
                      "Verify the functionality of the basic services in the ZD",
                      interactive_mode = attrs["interactive_mode"])

    if attrs["interactive_mode"]:
        showNotice("Please select the APs under test")
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    test_cfgs = []
    test_cfgs= test_cfgs + makeTestParams()
    # Generate Test Params for TC require target AP
    for target_ap in active_ap_list:
        target_ap_conf = ap_sym_dict[target_ap]
        ap_model_id = const.get_ap_model_id(target_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(target_ap_conf['status'])
        #@autor: Tanshixiong @since: 20150312 zf-12345
        test_cfgs = test_cfgs + makeTestParams(target_ap, ap_model_id, ap_role_id)

    test_order = 1
    test_added = 0
    for test_params, test_name, tcid, test_desc in test_cfgs:
        if test_params.has_key('target_ap'):
            target_ap = test_params['target_ap']
            target_ap_conf = ap_sym_dict[target_ap]
            #autor: Tanshixiong @since: 20150312 zf-12345
            common_name=getCommonName(tcid, test_desc,target_ap)
        else:            
            common_name=getCommonName(tcid, test_desc)
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
