import sys
import logging

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.scripts.fm.libFM_TestSuite import input_with_default
from RuckusAutoTest.common import Ratutils as utils

#@author:yuyanan @since:2014-8-6 zf-9438 optimize:ap_tag substitute for ap_model in case name
def tcid(base_id, description, ap_model,ap_tag):
    aptcid = const.get_ap_model_id(ap_model)
    ap_model = ap_model.upper()
    return u'TCID:14.02.%02d.%02d - %s - %s' % (base_id, aptcid, description, ap_tag)


def get_test_cfgByApModel(target_sta, active_ap, ap_model, server_ip, server_mac_addr, rate_limiting):
    test_cfgs = [
        (    # 14.1.2
            {   'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'tos':'0xe0',
                'expect_queue':'voice',
                'do_tunnel':True,
                'vlan_id':2},
            tcid(1, "TOS tagged voice classification", ap_model,active_ap),
            "ZD_AP_Qos_Tunnel"),
        (    # 14.1.3
            {   'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'tos':'0xa0',
                'expect_queue':'video',
                'do_tunnel':True,
                'vlan_id':2},
            tcid(2, "TOS tagged video classification", ap_model,active_ap),
            "ZD_AP_Qos_Tunnel"),

        ( # the combination: Qos 14.2.1
           {
                'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'tos':'0xe0',
                'expect_queue':'voice',
                'do_tunnel':True,
                'dvlan': True,
            },
            tcid(3, "TOS voice classification with dvlan", ap_model,active_ap),
            "ZD_AP_Qos_Tunnel"),

        ( # the combination: Qos 14.2.1
           {
                'target_station': target_sta,
                'active_ap': active_ap,
                'num_of_pkts':1000,
                'tos':'0xe0',
                'expect_queue':'voice',
                'do_tunnel':True,
                'dvlan': True,
                'set_mgmt': dict(enabled = True, vlan_id = str(2))
            },
            tcid(4, "TOS voice classification with dvlan, enable mgmt", ap_model,active_ap),
            "ZD_AP_Qos_Tunnel"),
    ]

    return test_cfgs

def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)


def input_ratelimiting(target_sta, traffic_svr_addr):
    rate_cfg = dict(uplink_rate_limit = "100 kbps", downlink_rate_limit = "100 kbps", margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1)

    logging.info("***** Input value for rate limiting test case *****")
    for rate_k, rate_v in rate_cfg.iteritems():
        rate_cfg[rate_k] = input_with_default("Input %s " % rate_k, rate_v)

    return rate_cfg

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

    server_mac_addr = raw_input("Server MAC address : ").lower()


    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        showNotice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    rate_limiting = input_ratelimiting(target_sta, tbcfg['server']['ip_addr'])

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "QOS - Smartcast Mesh"
    ts = testsuite.get_testsuite(ts_name,
                      'Verify the ability of the APs to classify traffic properly using different methods',
                      interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for active_ap in sorted(active_ap_list):
        ap_cfg = ap_sym_dict[active_ap]
        test_cfgs = get_test_cfgByApModel(target_sta, active_ap, ap_cfg['model'], tbcfg['server']['ip_addr'],
                                          server_mac_addr, rate_limiting)
        for test_params, common_name, test_name in test_cfgs:
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

