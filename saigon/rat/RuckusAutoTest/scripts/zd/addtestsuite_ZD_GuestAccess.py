import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(base_id,target_sta_radio, description):
    return u'TCID:03.02.01.%02d.%d - %s' % (base_id,const.get_radio_id(target_sta_radio), description)

def defineTestConfiguration(target_sta, target_sta_radio, zd_ip_addr='192.168.0.2', active_ap_list = None):
    restricted_ip_list=['172.21.0.252', '172.22.0.252', '172.23.0.252', '172.24.0.252', '172.25.0.252']
    dest_ip = '172.126.0.252'
    test_cfgs = []
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=True , use_tou=False, redirect_url = ''),
                      "ZD_GuestAccess",
                      _tcid(1,target_sta_radio, "Auth/No TOU/No Redirection"),))
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=True , use_tou=False, redirect_url = 'http://www.example.net/'),
                      "ZD_GuestAccess",
                      _tcid(2,target_sta_radio, "Auth/No TOU/Redirection"),))
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=True , use_tou=True , redirect_url = ''),
                      "ZD_GuestAccess",
                      _tcid(3,target_sta_radio, "Auth/TOU/No Redirection"),))
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=True , use_tou=True , redirect_url = 'http://www.example.net/'),
                      "ZD_GuestAccess",
                      _tcid(4,target_sta_radio, "Auth/TOU/Redirection"),))
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=False, use_tou=False, redirect_url = ''),
                      "ZD_GuestAccess",
                      _tcid(5,target_sta_radio, "No Auth/No TOU/No Redirection"),))
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=False, use_tou=False, redirect_url = 'http://www.example.net/'),
                      "ZD_GuestAccess",
                      _tcid(6,target_sta_radio, "No Auth/No TOU/Redirection"),))
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=False, use_tou=True , redirect_url = ''),
                      "ZD_GuestAccess",
                      _tcid(7,target_sta_radio, "No Auth/TOU/Redirection"),))
    test_cfgs.append((dict(ip=dest_ip, target_station=target_sta, use_guest_auth=False, use_tou=True , redirect_url = 'http://www.example.net/'),
                      "ZD_GuestAccess",
                      _tcid(8,target_sta_radio, "No Auth/TOU/Redirection"),))
    test_cfgs.append((dict(allowed_ip=dest_ip, target_station=target_sta, zd_ip=zd_ip_addr, restricted_ip_list=restricted_ip_list),
                      "ZD_RestrictedSubnetAccess",
                      _tcid(9,target_sta_radio, "Restricted Subnet Access"),))

    # Distribute active AP to all the test cases
    idx = 0
    total_ap = len(active_ap_list)
    for test_cfg in test_cfgs:
        test_cfg[0]['active_ap'] = sorted(active_ap_list)[idx]
        idx = (idx + 1) % total_ap

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name="WLAN Types - Guest Access"
    )
    attrs.update(kwargs)
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    zd_ip_addr = tbcfg['ZD']['ip_addr']
    ap_sym_dict = tbcfg["ap_sym_dict"]
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(tbcfg['sta_ip_list'])
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    test_cfgs = defineTestConfiguration(target_sta, target_sta_radio, zd_ip_addr, active_ap_list)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    ts = testsuite.get_testsuite(ts_name,
                      'Verify the ability of the ZD to handle guest access properly',
                      interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        test_params['target_sta_radio'] = target_sta_radio
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
