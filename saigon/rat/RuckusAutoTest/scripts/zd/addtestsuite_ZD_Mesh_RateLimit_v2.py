import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import lib_Debug as bugme

def makeTestCfg(sta_radio):
    test_cfg = dict()
    ts_base_id = "TCID:10.05.03"
    #_wcid = 0
    #test_cfg[1] = (dict(uplink_rate_limit = "100 kbps", downlink_rate_limit = "100 kbps", margin_of_error = 0.2, number_of_ssid = 1)
    #              , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 1
    test_cfg[2] = (dict(uplink_rate_limit = "250 kbps", downlink_rate_limit = "250 kbps", margin_of_error = 0.2, number_of_ssid = 1)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 2
    test_cfg[3] = (dict(uplink_rate_limit = "500 kbps", downlink_rate_limit = "500 kbps", margin_of_error = 0.2, number_of_ssid = 1)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 3
    test_cfg[4] = (dict(uplink_rate_limit = "1 mbps"  , downlink_rate_limit = "1 mbps"  , margin_of_error = 0.2, number_of_ssid = 1)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 4
    test_cfg[5] = (dict(uplink_rate_limit = "2 mbps"  , downlink_rate_limit = "2 mbps"  , margin_of_error = 0.2, number_of_ssid = 1)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 5
    test_cfg[6] = (dict(uplink_rate_limit = "5 mbps"  , downlink_rate_limit = "5 mbps"  , margin_of_error = 0.2, number_of_ssid = 1)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 6
    test_cfg[7] = (dict(uplink_rate_limit = "10 mbps" , downlink_rate_limit = "10 mbps" , margin_of_error = 0.2, number_of_ssid = 1)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 7
    test_cfg[8] = (dict(uplink_rate_limit = "20 mbps" , downlink_rate_limit = "20 mbps" , margin_of_error = 0.2, number_of_ssid = 1)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    #_wcid = 8
    #test_cfg[9] = (dict(uplink_rate_limit = "50 mbps" , downlink_rate_limit = "50 mbps" , margin_of_error = 0.2, number_of_ssid = 1)
    #              , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    #_wcid = 9
    #test_cfg[10] = (dict(uplink_rate_limit = "100 kbps", downlink_rate_limit = "2 mbps"  , margin_of_error = 0.2, number_of_ssid = 1)
    #              , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 10
    #JLIN@20090113 changed number_of_ssid from 8 to 6, because ZD80 only support 6 WLANs with mesh
    test_cfg[11] = (dict(uplink_rate_limit = "10 mbps" , downlink_rate_limit = "10 mbps" , margin_of_error = 0.2, number_of_ssid = 6)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))

    return test_cfg

def getCommonNameWithTcid(active_ap_type_role, apcfg, test_cfg):
    tcid = test_cfg[1][active_ap_type_role] if test_cfg[1].has_key(active_ap_type_role) else 'tcid:0.0.0.0'
    cname = getCommonName(test_cfg[0])
    return tcid + " - " + cname + " - " + active_ap_type_role

def getCommonName(tcfg):
    cname = "Up[%s]/Down[%s] RL on %d WLAN(s)" % (tcfg['uplink_rate_limit'], tcfg['downlink_rate_limit'], tcfg['number_of_ssid'])
    return cname

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = "Mesh - Integration - Rate Limiting - v2"
    )
    attrs.update(kwargs)    
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]    
    ts = testsuite.get_testsuite(ts_name,
                      'Verify the ability of the ZD to control rate limit rules on mesh network properly',
                      interactive_mode = attrs["interactive_mode"])

    test_cfg = makeTestCfg(target_sta_radio)
    test_order = 1
    test_added = 0
    test_name = 'ZD_RateLimiting_v2'

    for active_ap in sorted(active_ap_list):
        test_params = {}
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg)
        for idx, tcfg in test_cfg.iteritems():
            test_params = tcfg[0]
            test_params['target_station'] = target_sta
            test_params['target_sta_radio'] = target_sta_radio
            test_params['active_ap'] = active_ap
            test_params['traffic_srv_addr'] = '192.168.0.252'  #getServerIp

            common_name = "Mesh %s" % getCommonNameWithTcid(ap_type_role, apcfg, tcfg)
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1
    
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

