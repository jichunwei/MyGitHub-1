import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _tcid(mid, sid, description):
    return u'TCID:04.01.%02d.%02d - %s' % (mid, sid, description)

def defineTestConfiguration(tbcfg, attrs = {}):
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta_11g = testsuite.getTargetStation(sta_ip_list, "Pick an IP for 11g client: ")
        target_sta_11n = testsuite.getTargetStation(sta_ip_list, "Pick an IP for 11n client: ")
    else:
        if attrs["sta_11g"]:
            target_sta_11g = sta_ip_list[attrs["sta_11g"][0]]
        if attrs["sta_11n"]:
            target_sta_11n = sta_ip_list[attrs["sta_11n"][0]]

    ap_2925 = None
    ap_2942 = None
    ap_7942 = None
    ap_2741 = None
    for ap_sym, ap_info in ap_sym_dict.items():
        if ap_info['model'].lower() == 'zf2925':
            ap_2925 = ap_sym
        elif ap_info['model'].lower() == 'zf2942':
            ap_2942 = ap_sym
        elif ap_info['model'].lower() == 'zf7942':
            ap_7942 = ap_sym
        elif ap_info['model'].lower() == 'zf2741':
            ap_2741 = ap_sym
        else:
            print 'WARNING: Model %s is not defined in testsuite.' % ap_info['model']

    test_cfgs = []
    if target_sta_11g:
        test_cfgs.append(({'target_station':target_sta_11g},
                          _tcid(1, 0, "Wireless clients cannot talk to each other"),
                          "ZD_Wireless_Client_Isolation",))
        test_cfgs.append(({'target_station':target_sta_11g},
                          _tcid(2, 1, "Wireless clients cannot reach ZD's default subnet"),
                          "ZD_Wireless_Client_ZD_Default_Subnet_Isolation",))
        test_cfgs.append(({'target_station':target_sta_11g, 'ip':'172.21.0.252', 'restricted_ip_list':['172.21.0.0/16']},
                          _tcid(2, 2, "Wireless clients cannot reach non-default restricted subnets"),
                          "ZD_Wireless_Client_ZD_nonDefault_Subnet_Isolation",))
        if ap_2925:
            test_cfgs.append(({'target_station':target_sta_11g, 'ip_of_non_default_subnet':'172.21.0.252',
                               'active_ap':ap_2925, 'restricted_ip_list':['172.21.0.0/16'], 'radio_mode':''},
                              _tcid(3, 0, "Verify wireless client isolation on ZF2925"),
                              "ZD_Wireless_Client_Isolation_For_Specific_AP",))
        if ap_2942:
            test_cfgs.append(({'target_station':target_sta_11g, 'ip_of_non_default_subnet':'172.21.0.252',
                               'active_ap':ap_2942, 'restricted_ip_list':['172.21.0.0/16'], 'radio_mode':''},
                              _tcid(4, 0, "Verify wireless client isolation on ZF2942"),
                              "ZD_Wireless_Client_Isolation_For_Specific_AP",))
        if ap_2741:
            test_cfgs.append(({'target_station':target_sta_11g, 'ip_of_non_default_subnet':'172.21.0.252',
                               'active_ap':ap_2741, 'restricted_ip_list':['172.21.0.0/16'], 'radio_mode':''},
                              _tcid(4, 0, "Verify wireless client isolation on ZF2741"),
                              "ZD_Wireless_Client_Isolation_For_Specific_AP",))
        if ap_7942:
            test_cfgs.append(({'target_station':target_sta_11g, 'ip_of_non_default_subnet':'172.21.0.252',
                               'active_ap':ap_7942, 'restricted_ip_list':['172.21.0.0/16'], 'radio_mode':'g'},
                              _tcid(5, 0, "Verify wireless client isolation on ZF7942 and 11g client"),
                              "ZD_Wireless_Client_Isolation_For_Specific_AP",))
    if target_sta_11n and ap_7942:
        test_cfgs.append(({'target_station':target_sta_11n, 'ip_of_non_default_subnet':'172.21.0.252',
                           'active_ap':ap_7942, 'restricted_ip_list':['172.21.0.0/16'], 'radio_mode':'n'},
                          _tcid(6, 0, "Verify wireless client isolation on ZF7942 and 11n client"),
                          "ZD_Wireless_Client_Isolation_For_Specific_AP",))

    return test_cfgs

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_11g = "", # default value for station 0
        sta_11n = "", # default value for station 1        
        targetap = False,
        testsuite_name = "WLAN Options - Wireless Client Isolation"
    )
    attrs.update(kwargs)
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    test_cfgs = defineTestConfiguration(tbcfg, attrs)

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]    
    ts = testsuite.get_testsuite(ts_name, 'Verify the feature Wireless Client Isolation')

    test_order = 1
    test_added = 0
    
    for test_params, common_name, test_name in test_cfgs:        
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

