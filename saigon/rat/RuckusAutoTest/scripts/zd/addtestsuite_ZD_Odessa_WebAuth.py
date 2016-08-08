import sys
import time
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def getApTargetType(active_ap, apcfg, default_ap_type=False):
    mfmt = '\nactive_ap (%s): model: %s; mac: %s; status: %s; is (root | mesh | mesh2)? '
    msg = mfmt % (active_ap, apcfg['model'], apcfg['mac'], apcfg['status'])
    ap_model = apcfg['model'].lower()
    ap_status = apcfg['status']
    if default_ap_type:
        if re.search(r'root', ap_status, re.I):
            return '%s ROOT' % ap_model
        if re.search(r'mesh ap, 1 hop', ap_status, re.I):
            return '%s MESH' % ap_model
        if re.search(r'mesh ap, 2 hops', ap_status, re.I):
            return '%s MESH2' % ap_model
    else:
        while True:
            what = raw_input(msg).lower()
            if what == "root":
                return '%s ROOT' % ap_model
            elif what == "mesh":
                return '%s MESH' % ap_model
            elif what == "mesh2":
                return '%s MESH2' % ap_model
            elif re.match(r'^(q|x)', what):
                raise 'User abort adding test case'
            elif len(what) == 0:
                if re.search(r'root', ap_status, re.I):
                    return '%s ROOT' % ap_model
                if re.search(r'mesh ap, 1 hop', ap_status, re.I):
                    return '%s MESH' % ap_model
                if re.search(r'mesh ap, 2 hops', ap_status, re.I):
                    return '%s MESH2' % ap_model

def defineWlanConfigs():
    wlan_cfgs = []
    ssid = "RAT-WEBAUTHENTICATION-%s" % time.strftime("%H%M%S")

    # Open System
    wlan_cfgs.append((dict(ssid=ssid, auth="open", wpa_ver="", encryption="none",
                           sta_auth="open", sta_wpa_ver="", sta_encryption="none",
                           key_index="" , key_string="",
                           username="", password="", ras_addr="", ras_port="",
                           ras_secret="", use_radius=False),
                      "Open System", 4))
    # Open - WEP64
    wlan_cfgs.append((dict(ssid=ssid, auth="open", wpa_ver="", encryption="WEP-64",
                           sta_auth="open", sta_wpa_ver="", sta_encryption="WEP-64",
                           key_index="1" , key_string=utils.make_random_string(10,"hex"),
                           username="", password="", ras_addr="", ras_port="",
                           ras_secret="", use_radius=False),
                      "Open WEP64 KEY1", 5))
    # WPA PSK TKIP
    wlan_cfgs.append((dict(ssid=ssid, auth="PSK", wpa_ver="WPA", encryption="TKIP",
                           sta_auth="PSK", sta_wpa_ver="WPA", sta_encryption="TKIP",
                           key_index="" , key_string=utils.make_random_string(63,"alnum"),
                           username="", password="", ras_addr="", ras_port="",
                           ras_secret="", use_radius=False),
                      "WPA PSK TKIP", 6))
    # WPA2 PSK AES
    wlan_cfgs.append((dict(ssid=ssid, auth="PSK", wpa_ver="WPA2", encryption="AES",
                           sta_auth="PSK", sta_wpa_ver="WPA2", sta_encryption="AES",
                           key_index="" , key_string=utils.make_random_string(63,"alnum"),
                           username="", password="", ras_addr="", ras_port="",
                           ras_secret="", use_radius=False),
                      "WPA2 PSK AES", 7))

    return wlan_cfgs

def defineAuthConfig():
    auth_cfgs = []
    auth_cfgs.append(("Local Account", {"username":"odessa.test.user", "password":"odessa.test.user",
                                        "ras_addr":"", "ras_port":"", "ras_secret":"",
                                        "ad_addr":"", "ad_port":"", "ad_domain":""}))
    auth_cfgs.append(("Active Directory", {"username":"rat.test.user", "password":"rat.test.user",
                                           "ras_addr":"", "ras_port":"", "ras_secret":"",
                                           "ad_addr":"192.168.0.250", "ad_port":"389", "ad_domain":"rat.ruckuswireless.com"}))
    auth_cfgs.append(("Radius Server", {"username":"ras.local.user", "password":"ras.local.user",
                                        "ras_addr":"192.168.0.252", "ras_port":"1812", "ras_secret":"1234567890",
                                        "ad_addr":"", "ad_port":"", "ad_domain":""}))
    return auth_cfgs

def tcid(tsid, tcid, target_sta_radio):
    return "TCID:%s.%02d.%d" % (tsid, tcid, const.get_radio_id(target_sta_radio))

def tcid_ex(tsid, base_id, auth_type, ap_type, target_sta_radio):
    _ap_type = ap_type.lower()
    _auth_type = auth_type.lower()
    ofs = {"local account": 0, "active directory": 4, "radius server": 8}[_auth_type]
    apid = const.get_ap_model_id(_ap_type.split()[0].upper())
    return "TCID:%s.%02d.%d.%d" % (tsid, base_id+ofs, apid, const.get_radio_id(target_sta_radio))

def defineTestConfiguration(target_sta, target_sta_radio, conn_mode, enable_tunnel, enable_vlan, active_ap_list, ap_sym_dict, default_ap_type=False):
    test_cfgs = []
    target_ip = '172.126.0.252'
    if conn_mode.lower() == "l2":
        if enable_tunnel:
            if not enable_vlan:
                tsid = "11.03"
                expected_subnet = "192.168.0.0"
                vlan_id = ""
            else:
                tsid = "11.04"
                expected_subnet = "20.0.2.0/255.255.255.0"
                vlan_id = "2"

            # Define 3 test cases
            test_policy = 'web authentication'
            active_ap = active_ap_list[0]
            test_cfgs.append((dict(ip=target_ip, expected_subnet=expected_subnet, connection_mode=conn_mode,
                                   target_station=target_sta, active_ap=active_ap, enable_tunnel=enable_tunnel,
                                   vlan_id=vlan_id, test_option='delete', test_policy=test_policy),
                              'ZD_Client_Management', 'Open System - Local Account - Client Deleted', tcid(tsid, 1, target_sta_radio)))
            test_cfgs.append((dict(ip=target_ip, expected_subnet=expected_subnet, connection_mode=conn_mode,
                                   target_station=target_sta, active_ap=active_ap, enable_tunnel=enable_tunnel,
                                   vlan_id=vlan_id, test_option='block', test_policy=test_policy),
                              'ZD_Client_Management', 'Open System - Local Account - Client Blocked', tcid(tsid, 2, target_sta_radio)))
            test_cfgs.append((dict(ip=target_ip, expected_subnet=expected_subnet, connection_mode=conn_mode,
                                   target_station=target_sta, active_ap=active_ap, enable_tunnel=enable_tunnel,
                                   vlan_id=vlan_id, test_option='unblock', test_policy=test_policy),
                              'ZD_Client_Management', 'Open System - Local Account - Client Unblocked', tcid(tsid, 3,target_sta_radio)))
    elif conn_mode.lower() == "l3":
        if enable_tunnel:
            if not enable_vlan:
                tsid = "12.03"
                expected_subnet = "192.168.0.0"
                vlan_id = ""
            else:
                tsid = "12.04"
                expected_subnet = "20.0.2.0/255.255.255.0"
                vlan_id = "2"
        else:
            if not enable_vlan:
                tsid = "12.07"
                expected_subnet = "192.168.33.0"
                vlan_id = ""
            else:
                tsid = "12.08"
                expected_subnet = "20.0.2.0/255.255.255.0"
                vlan_id = "2"

    test_name = "ZD_EncryptionTypesWebAuth"
    wlan_cfgs = defineWlanConfigs()
    auth_cfgs = defineAuthConfig()
    auth_cfg_idx = 0
    for active_ap in sorted(active_ap_list):
        ap_cfg = ap_sym_dict[active_ap]
        ap_type = testsuite.getApTargetType(active_ap, ap_cfg, default_ap_type)
        auth_cfg_name, auth_cfg = auth_cfgs[auth_cfg_idx]
        for cfg in wlan_cfgs:
            wlan_cfg, wlan_cfg_name, wlan_cfg_base_id = cfg
            # Merge with authentication server configuration
            wlan_cfg.update(auth_cfg)
            # Define basic test configuration
            test_cfg = dict(ip=target_ip, expected_subnet=expected_subnet, connection_mode=conn_mode,
                            target_station=target_sta, active_ap=active_ap, enable_tunnel=enable_tunnel,
                            use_guest_auth=True, use_tou=True, redirect_url = 'http://www.example.net/', wlan_cfg=wlan_cfg.copy())
            # Define common name and test ID
            common_name = "%s - %s - %s" % (wlan_cfg_name, auth_cfg_name, ap_type.upper())
            id = tcid_ex(tsid, wlan_cfg_base_id, auth_cfg_name, ap_type, target_sta_radio)
            # Add to the list
            test_cfgs.append((test_cfg, test_name, common_name, id))
        # Choose the authentication server in a round-robin fashion
        auth_cfg_idx = (auth_cfg_idx + 1)%len(auth_cfgs)

    if enable_vlan:
        for test_cfg in test_cfgs:
            test_cfg[0]['vlan_id'] = vlan_id

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        mode = "l2",
        tunnel = False,
        vlan = False,
        testsuite_name=""
    )
    attrs.update(kwargs)

    tbi = testsuite.getTestbed2(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    ap_sym_dict = tb_cfg["ap_sym_dict"]
    sta_ip_list = tb_cfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(tb_cfg["sta_ip_list"])
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        print "Active AP list: %s" % active_ap_list

        conn_mode = raw_input("Please enter connection mode [l2/l3]: ")
        enable_tunnel = raw_input("Is tunnel mode enabled? [y/n]: ").lower() == "y"
        enable_vlan = raw_input("Is VLAN tagging enabled? [y/n]: ").lower() == "y"
        default_ap_type = True
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
        conn_mode = kwargs["mode"]
        enable_tunnel = kwargs["tunnel"]
        enable_vlan = kwargs["vlan"]
        default_ap_type = False

    ts_name = "%s %s - WebAuth" % (conn_mode.upper(), "Tunnel" if enable_tunnel else "Without Tunnel")
    if enable_vlan:
        ts_name += " with VLAN"

    test_cfgs = defineTestConfiguration(target_sta, target_sta_radio, conn_mode, enable_tunnel, enable_vlan, active_ap_list, ap_sym_dict,
                                        default_ap_type)

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    ts = testsuite.get_testsuite(ts_name, "")

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        test_params['target_sta_radio'] = target_sta_radio
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
