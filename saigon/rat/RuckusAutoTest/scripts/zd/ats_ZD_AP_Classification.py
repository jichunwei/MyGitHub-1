import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(base_id, description, ap_model):
    aptcid = const.get_ap_model_id(ap_model)
    ap_model = ap_model.upper()
    return u'TCID:06.02.%02d.%02d - %s - %s' % (base_id, aptcid, description, ap_model)

# Example:
#
#   tcfgs = get_test_cfgByApModel('192.168.1.11', 'AP_01', 'zf2741')
#
# return list of tuple(test_param, common_name, test_name)
def get_test_cfgByApModel(target_sta, active_ap, ap_model):
    test_cfgs = [
        (   {   'target_station':target_sta,
                'active_ap':active_ap,
                'num_of_pkts':1000,
                'len_of_pkt':300,
                'pkt_gap':20000,
                'expect_queue':'voice'},
            tcid(1, "Heuristics voice classification based on IPG+packet length", ap_model),
            "ZD_AP_Heuristic_Classification"),
        (   {   'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'len_of_pkt':1500,
                'pkt_gap':20000,
                'expect_queue':'video'},
            tcid(2, "Heuristics video classification based on IPG+packet length", ap_model),
            "ZD_AP_Heuristic_Classification"),
        (   {   'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'len_of_pkt':500,
                'pkt_gap':2000,
                'expect_queue':'data'},
            tcid(3, "Other UDP traffics should go data queue", ap_model),
            "ZD_AP_Heuristic_Classification"),
        (   {   'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'tos':'0xc0',
                'expect_queue':'voice'},
            tcid(9, "TOS voice classification", ap_model),
            "ZD_AP_TOS_Classification"),
        (   {   'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'tos':'0xa0',
                'expect_queue':'video'},
            tcid(10, "TOS video classification", ap_model),
            "ZD_AP_TOS_Classification"),
    ]
    return test_cfgs

def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = None,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        showNotice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "QOS - Smartcast"
    ts = testsuite.get_testsuite(ts_name,
                      'Verify the ability of the APs to classify traffic properly using different methods',
                      interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for active_ap in sorted(active_ap_list):
        ap_cfg = ap_sym_dict[active_ap]
        test_cfgs = get_test_cfgByApModel(target_sta, active_ap, ap_cfg['model'])
        for test_params, common_name, test_name in test_cfgs:
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

