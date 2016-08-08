import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration(target_station, mesh_link_ap_list):
    wlan_cfg = defineWLANConf()
    test_cfgs = []

    test_name = 'CB_ZD_Init_Wired_Mesh_Network_Test_Environment'
    common_name = 'Initiate test environment'
    test_cfgs.append(({'expected_number_ap':5,
                       'auth_server_info':wlan_cfg['auth_ser'],
                       },
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create 2 EAP WLANs %s' % ([wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid']])
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg['eap-wpa-tkip'], wlan_cfg['eap-wpa2-eas']]},
                      test_name, common_name, 1, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing on two WLANs %s' % ([wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid']])
    test_cfgs.append(({'target_station': '192.168.1.11'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wired_Mesh_Network_Test'
    common_name = 'Form wired mesh network'
    test_cfgs.append(({'testcase': 'form_wired_mesh_network',
                       'mesh_link_aps_list': mesh_link_ap_list,
                       'expected_aps_role':{'root_ap':1, 'mesh_ap':1, 'link_ap':3}},
                      test_name, common_name, 1, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing on two WLANs %s after the wired mesh network is formed'
    common_name = common_name % ([wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid']])
    test_cfgs.append(({'target_station': target_station},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create 2 more EAP WLANs %s' % ([wlan_cfg['eap-wpa2-tkip']['ssid'], wlan_cfg['eap-wpa-eas']['ssid']])
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg['eap-wpa2-tkip'], wlan_cfg['eap-wpa-eas']]},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing on four WLANs %s'
    common_name = common_name % ([wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid'],
                                  wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid']])
    test_cfgs.append(({'target_station': target_station},
                      test_name, common_name, 3, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Tear down all WLANs'
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create 4 EAP WLANs %s' % ([wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid'],
                                              wlan_cfg['eap-wpa2-tkip']['ssid'], wlan_cfg['eap-wpa-eas']['ssid']])
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg['eap-wpa-tkip'], wlan_cfg['eap-wpa2-eas'],
                                        wlan_cfg['eap-wpa2-tkip'], wlan_cfg['eap-wpa-eas']]},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing on WLANs %s after creating'
    common_name = common_name % ([wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid'],
                                  wlan_cfg['eap-wpa-tkip']['ssid'], wlan_cfg['eap-wpa2-eas']['ssid']])
    test_cfgs.append(({'target_station': target_station},
                      test_name, common_name, 3, False))

    test_name = 'CB_ZD_Wired_Mesh_Network_Test'
    common_name = 'Reboot the Mesh AP, one of three Link AP become Mesh AP'
    test_cfgs.append(({'testcase': 'mesh_ap_temporary_out_of_service',
                       'mesh_link_aps_list': mesh_link_ap_list,
                       'expected_aps_role':{'root_ap':1, 'mesh_ap':1, 'link_ap':3}},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing after Mesh AP temporary out of service'
    test_cfgs.append(({'target_station': target_station},
                      test_name, common_name, 3, False))

    test_name = 'CB_ZD_Wired_Mesh_Network_Test'
    common_name = 'Reboot the Link AP, this AP will reconnect to Zone Director as Link AP'
    test_cfgs.append(({'testcase': 'link_ap_temporary_out_of_service',
                       'mesh_link_aps_list': mesh_link_ap_list,
                       'expected_aps_role':{'root_ap':1, 'mesh_ap':1, 'link_ap':3}},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing after Link AP temporary out of service'
    test_cfgs.append(({'target_station': target_station},
                      test_name, common_name, 3, False))

    test_name = 'CB_ZD_Wired_Mesh_Network_Test'
    common_name = 'Mesh AP become Root'
    test_cfgs.append(({'testcase': 'mesh_ap_become_root',
                       'mesh_link_aps_list': mesh_link_ap_list,
                       'expected_aps_role':{'root_ap':2, 'mesh_ap':1, 'link_ap':2}},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wired_Mesh_Network_Test'
    common_name = 'Link AP become Root'
    test_cfgs.append(({'testcase': 'link_ap_become_root',
                       'mesh_link_aps_list': mesh_link_ap_list,
                       'expected_aps_role':{'root_ap':3, 'mesh_ap':1, 'link_ap':1}},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing after the Mesh AP and one Link AP become Root'
    test_cfgs.append(({'target_station': target_station},
                      test_name, common_name, 3, False))

    test_name = 'CB_ZD_Wired_Mesh_Network_Test'
    common_name = 'Reboot Zone Director, the wired mesh network will form correctly after then'
    test_cfgs.append(({'testcase': 'CB_ZD_temporary_out_of_service',
                       'mesh_link_aps_list': mesh_link_ap_list,
                       'expected_aps_role':{'root_ap':1, 'mesh_ap':1, 'link_ap':3}},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing after the Zone Director is up'
    test_cfgs.append(({'target_station': target_station},
                      test_name, common_name, 3, False))

    test_name = 'CB_ZD_Wired_Mesh_Network_Test'
    common_name = 'All Mesh AP and Link APs become Root'
    test_cfgs.append(({'testcase': 'all_aps_become_root',
                       'mesh_link_aps_list': mesh_link_ap_list,
                       'expected_aps_role':{'root_ap':5, 'mesh_ap':0, 'link_ap':0}},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs'
    test_cfgs.append(({},
                      test_name, common_name, 2, False))

    return test_cfgs

def defineWLANConf():
    wlan_cfg = {'auth_ser': {'server_name': 'RADIUS',
                             'server_addr': '192.168.0.252',
                             'radius_auth_secret': '1234567890',
                             'server_port': '1812'},
                'eap-wpa-tkip': {'ssid':'EAP-WPA-TKIP', 'auth':'EAP', 'encryption':'TKIP',
                                 'wpa_ver':'WPA', 'auth_svr': 'RADIUS', 'type': None,
                                 'username':'ras.eap.user', 'password':'ras.eap.user',
                                 'use_radius': True, 'key_string': ''},
                'eap-wpa-eas': {'ssid':'EAP-WPA-AES', 'auth':'EAP', 'encryption':'AES',
                                'wpa_ver':'WPA', 'auth_svr': 'RADIUS', 'type': None,
                                'username':'ras.eap.user', 'password':'ras.eap.user',
                                'use_radius': True, 'key_string': ''},
                'eap-wpa2-tkip': {'ssid':'EAP-WPA2-TKIP', 'auth':'EAP', 'encryption':'TKIP',
                                  'wpa_ver':'WPA2', 'auth_svr': 'RADIUS', 'type': None,
                                  'username':'ras.eap.user', 'password':'ras.eap.user',
                                  'use_radius': True, 'key_string': ''},
                'eap-wpa2-eas': {'ssid':'EAP-WPA2-AES', 'auth':'EAP', 'encryption':'AES',
                                 'wpa_ver':'WPA2', 'auth_svr': 'RADIUS', 'type': None,
                                 'username':'ras.eap.user', 'password':'ras.eap.user',
                                 'use_radius': True, 'key_string': ''}}

    return wlan_cfg

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    target_station = testsuite.getTargetStation(sta_ip_list, 'Pick an wireless station: ')
    print 'Select 4 APs for Wired Mesh Network setting up'
    while True:
        mesh_link_ap_list = testsuite.getActiveAp(ap_sym_dict)
        if len(mesh_link_ap_list) == 4:
            break

    ts_name = 'ZD_CB_Test_Wired_Mesh_Network'
    ts = testsuite.get_testsuite(ts_name, 'Verify the wired mesh network functionality', combotest=True)
    test_cfgs = defineTestConfiguration(target_station, mesh_link_ap_list)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
