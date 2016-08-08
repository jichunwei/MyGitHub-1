import sys, time
import random
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(tcid, ap_model_id, ap_role_id):
    return "TCID:%s.%02d.%s.%s" % (14.02, tcid, ap_model_id, ap_role_id)

def defineTestConfiguration(target_station_1, target_station_2, ap_sym_dict, ap_conn_mode):
    test_cfgs = []
    target_ip = '172.126.0.253'
    wlan_profile_set = 'set_of_32_open_none_wlans'
    wlan_profile_set_for_guest = 'set_of_32_open_none_wlans'
    print '---------------------------------------------------'
    print 'Please pick up the Root APs to test: '
    active_root_ap_list = testsuite.getActiveAp(ap_sym_dict)
    print '---------------------------------------------------\n'
    print '---------------------------------------------------'
    print 'Please pick up the Mesh APs to test: '
    active_mesh_ap_list = testsuite.getActiveAp(ap_sym_dict)
    print '---------------------------------------------------'

    if ap_conn_mode =='l3':
        test_name = 'ZD_MultiWlans_ZeroIT_Integration'
        for rootAP in active_root_ap_list:
            active_ap_conf = ap_sym_dict[rootAP]
            ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
            ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
            ap_type = active_ap_conf['model']

            common_name = '%s + VLAN + ZeroIT + L3LWAPP + Root AP %s' % (wlan_profile_set, ap_type)
            test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':rootAP,
                               'vlan_id':'2', 'ip':'20.0.2.252/255.255.255.0'},
                              test_name, common_name, tcid(12, ap_model_id, ap_role_id)))

            common_name = '%s + Tunnel + ZeroIT + L3LWAPP + Root AP %s' % (wlan_profile_set, ap_type)
            test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':rootAP,
                               'do_tunnel': True, 'ip':'192.168.33.0'},
                              test_name, common_name, tcid(14, ap_model_id, ap_role_id)))

        for meshAP in active_root_ap_list:
            active_ap_conf = ap_sym_dict[meshAP]
            ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
            ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
            ap_type = active_ap_conf['model']

            common_name = '%s + VLAN + ZeroIT + L3LWAPP + Mesh AP %s' % (wlan_profile_set, ap_type)
            test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':meshAP,
                               'vlan_id':'2', 'ip':'20.0.2.252/255.255.255.0'},
                              test_name, common_name, tcid(13, ap_model_id, ap_role_id)))

            common_name = '%s + Tunnel + ZeroIT + L3LWAPP + Mesh AP %s' % (wlan_profile_set, ap_type)
            test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':meshAP,
                               'do_tunnel': True, 'ip':'192.168.33.0'},
                              test_name, common_name, tcid(15, ap_model_id, ap_role_id)))

        return test_cfgs

    for rootAP in active_root_ap_list:
        active_ap_conf = ap_sym_dict[rootAP]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = active_ap_conf['model']

        test_name = 'ZD_MultiWlans_Isolation_Integration'
        common_name = '%s + Isolation + Root AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station_1': target_station_1, 'target_station_2': target_station_2,
                           'wlan_config_set':wlan_profile_set, 'active_ap':rootAP},
                           test_name, common_name, tcid(2, ap_model_id, ap_role_id)))

        test_name = 'ZD_MultiWlans_ACL_Integration'
        common_name = '%s + ACL + Root AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':rootAP},
                          test_name, common_name, tcid(4, ap_model_id, ap_role_id)))

        test_name = 'ZD_MultiWlans_Rate_Limit_Integration'
        common_name = '%s + Rate Limit + Root AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':rootAP},
                          test_name, common_name, tcid(6, ap_model_id, ap_role_id)))

        test_name = 'ZD_MultiWlans_ZeroIT_Integration'
        common_name = '%s + VLAN + ZeroIT + L2LWAPP + Root AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':rootAP,
                           'vlan_id':'2', 'ip':'20.0.2.252/255.255.255.0'},
                           test_name, common_name, tcid(8, ap_model_id, ap_role_id)))

        common_name = '%s + Tunnel + ZeroIT + L2LWAPP + Root AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':rootAP,
                           'do_tunnel': True, 'ip':'192.168.0.0'},
                           test_name, common_name, tcid(10, ap_model_id, ap_role_id)))

    for meshAP in active_root_ap_list:
        active_ap_conf = ap_sym_dict[meshAP]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = active_ap_conf['model']

        test_name = 'ZD_MultiWlans_Isolation_Integration'
        common_name = '%s + Isolation + Mesh AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station_1': target_station_1, 'target_station_2': target_station_2,
                           'wlan_config_set':wlan_profile_set, 'active_ap':meshAP},
                           test_name, common_name, tcid(3, ap_model_id, ap_role_id)))

        test_name = 'ZD_MultiWlans_ACL_Integration'
        common_name = '%s + ACL + Mesh AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':meshAP},
                          test_name, common_name, tcid(5, ap_model_id, ap_role_id)))

        test_name = 'ZD_MultiWlans_Rate_Limit_Integration'
        common_name = '%s + Rate Limit + Mesh AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':meshAP},
                          test_name, common_name, tcid(7, ap_model_id, ap_role_id)))

        test_name = 'ZD_MultiWlans_ZeroIT_Integration'
        common_name = '%s + VLAN + ZeroIT + L2LWAPP + Mesh AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':meshAP,
                           'vlan_id':'2', 'ip':'20.0.2.252/255.255.255.0'},
                           test_name, common_name, tcid(9, ap_model_id, ap_role_id)))

        common_name = '%s + Tunnel + ZeroIT + L2LWAPP + Mesh AP %s' % (wlan_profile_set, ap_type)
        test_cfgs.append(({'target_station': target_station_1, 'wlan_config_set':wlan_profile_set, 'active_ap':meshAP,
                           'do_tunnel': True, 'ip':'192.168.0.0'},
                           test_name, common_name, tcid(11, ap_model_id, ap_role_id)))
    return test_cfgs

def make_test_suite(**kwargs):
    #tbi = getTestbed(**kwargs)
    #tb_cfg = testsuite.getTestbedConfig(tbi)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    target_sta_1 = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
    #print 'Pick up another station for Isolation testing'
    target_sta_2 = testsuite.getTargetStation(sta_ip_list, "Pick another wireless station for Isolation testing: ")
    
    tested_wlan_list = [0,31]
    for i in range(4):        
        index = random.randint(1,30)
        while index in tested_wlan_list: 
            index = random.randint(1,30)
            time.sleep(0.1)
        tested_wlan_list.append(index)
    tested_wlan_list.sort()
    ap_conn_mode = ''
    while ap_conn_mode not in ['l2', 'l3']:
        ap_conn_mode = raw_input('Please select the connection mode of APs in your testbed (l2/l3): ')

    ts_name = '32 WLANs - Integration'

    test_cfgs = defineTestConfiguration(target_sta_1, target_sta_2, ap_sym_dict, ap_conn_mode)
    ts = testsuite.get_testsuite(ts_name, 'Verify 32 WLANs Integration')

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        test_params['tested_wlan_list'] = tested_wlan_list
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, cname)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
