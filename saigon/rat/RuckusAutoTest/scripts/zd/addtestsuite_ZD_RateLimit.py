import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(mid, sid, target_sta_radio):
    return u"TCID:04.03.%02d.%02d.%d" % (mid, sid, const.get_radio_id(target_sta_radio))

def getCommonName(tcid, test_desc):
    return u"%s-%s" % (tcid, test_desc)

def makeTestParams(target_sta, target_sta_radio, traffic_svr_addr = '192.168.0.252'):
    test_params = {}
    #test_params[1] = (dict(uplink_rate_limit = "100 kbps", downlink_rate_limit = "100 kbps", margin_of_error = 0.04,
    #                target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1),
    #                "ZD_RateLimiting", tcid(1, 1, target_sta_radio), "Apply 100k Up/Down RL to wlan")
    test_params[2] = (dict(uplink_rate_limit = "250 kbps", downlink_rate_limit = "250 kbps", margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1), 
                    "ZD_RateLimiting", tcid(1, 2, target_sta_radio), "Apply 250k Up/Down RL to wlan")
    test_params[3] = (dict(uplink_rate_limit = "500 kbps", downlink_rate_limit = "500 kbps", margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1), 
                    "ZD_RateLimiting", tcid(1, 3, target_sta_radio), "Apply 500k Up/Down RL to wlan")
    test_params[4] = (dict(uplink_rate_limit = "1 mbps"  , downlink_rate_limit = "1 mbps"  , margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1), 
                    "ZD_RateLimiting", tcid(1, 4, target_sta_radio), " Apply 1M Up/Down RL to wlan")
    test_params[5] = (dict(uplink_rate_limit = "2 mbps"  , downlink_rate_limit = "2 mbps"  , margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1), 
                    "ZD_RateLimiting", tcid(1, 5, target_sta_radio), "Apply 2M Up/Down RL to wlan")
    test_params[6] = (dict(uplink_rate_limit = "5 mbps"  , downlink_rate_limit = "5 mbps"  , margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1), 
                    "ZD_RateLimiting", tcid(1, 6, target_sta_radio), "Apply 5M Up/Down RL to wlan")
    test_params[7] = (dict(uplink_rate_limit = "10 mbps" , downlink_rate_limit = "10 mbps" , margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1),
                    "ZD_RateLimiting", tcid(1, 7, target_sta_radio), "Apply 10M Up/Down RL to wlan")
    test_params[8] = (dict(uplink_rate_limit = "20 mbps" , downlink_rate_limit = "20 mbps" , margin_of_error = 0.04,
                    target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1),
                    "ZD_RateLimiting", tcid(1, 8, target_sta_radio), "Apply 20M Up/Down RL to wlan")
    #test_params[9] = (dict(uplink_rate_limit = "50 mbps" , downlink_rate_limit = "50 mbps" , margin_of_error = 0.04,
    #                target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1),
    #                "ZD_RateLimiting", tcid(1, 9, target_sta_radio) , "Apply 50M Up/Down RL to wlan")
    #test_params[10] = (dict(uplink_rate_limit = "100 kbps", downlink_rate_limit = "2 mbps"  , margin_of_error = 0.04,
    #                 target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 1), 
    #                 "ZD_RateLimiting", tcid(2, 0, target_sta_radio), "Apply 100k Up/2M Down RL to wlan")
    test_params[11] = (dict(uplink_rate_limit = "10 mbps" , downlink_rate_limit = "10 mbps" , margin_of_error = 0.04,
                     target_station = target_sta, traffic_srv_addr = traffic_svr_addr, number_of_ssid = 8), 
                     "ZD_RateLimiting", tcid(3, 0, target_sta_radio), "Apply same RL rule to 8 wlans")
    return test_params

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = "WLAN Options - Rate Limiting"        
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    traffic_serv_ip = testsuite.getTestbedServerIp(tbcfg)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "WLAN Options - Rate Limiting"
    ts = testsuite.get_testsuite(ts_name,
                      "Verify the ability of the ZD to control rate limits properly",
                      interactive_mode = attrs["interactive_mode"])

    if attrs["interactive_mode"]:        
        print "Please select a wireless station supporting %s radio" % expected_radio_mode
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:        
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]

    test_cfgs = makeTestParams(target_sta, target_sta_radio, traffic_serv_ip)
    test_order = 1
    test_added = 0
    for test_params, test_name, tcid, test_desc in test_cfgs.itervalues():
        common_name = getCommonName(tcid, test_desc)
        test_params['target_sta_radio'] = target_sta_radio
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

