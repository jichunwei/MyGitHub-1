import sys
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

pp = pprint.PrettyPrinter(indent=4)

def getDescription(ap_mode, tunnel , vlan_override, diff_wgs = False, map_roam = False, client_roam = False):
    common_name = "%s Override VLAN %s Tunnel - %s"
    vlan_override = {True:"Enable", False:"Disable"}[vlan_override]
    tunnel = {True: "With", False:"Without"}[tunnel]
    map_roam = {True: "MAP Roam", False: ""}[map_roam]
    client_roam = {True: "Client Roam", False: ""}[client_roam]
    common_name = common_name % (vlan_override, tunnel, ap_mode)

    if diff_wgs and map_roam:
        map_roam = "%s Different WlanGroup" % map_roam
    if diff_wgs and client_roam:
        client_roam = "%s Different WlanGroup" % client_roam
    if map_roam:
        common_name = "%s %s" % (map_roam, common_name)
    if client_roam:
        common_name = "%s %s" % (client_roam, common_name)

    return common_name

def getCommonName(id, description):
    return "TCID:15.02.%02d - %s" % (id, description)

def showNotice():
    msg = "Please select 3 APs (RootAP, RootAP, Mesh AP) under test (separate by comma)"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def get_wlan_cfg(ssid, wlan_params):
    wlanCfg = dict( ssid=ssid,
                    auth="open",
                    wpa_ver="",
                    encryption="none",
                    sta_auth="open",
                    sta_wpa_ver="",
                    sta_encryption="none",
                    key_index="",
                    key_string="",
                    username="",
                    password="",
                    ras_addr="",
                    ras_secret="",
                    use_radius= False,
                    do_tunnel = False,
                    vlan_id = '2')
    wlanCfg.update(wlan_params)
    return wlanCfg

def getTestParams(params, diff_wgs = False):
    wgs_cfg_01 = dict(
        description = 'rat-wgs-integration-01',
        name = 'rat-wgs-integration-01',
        vlan_override = False,
        wlan_member = {'rat-wlangroups-integration':{'vlan_override':'No Change', 'original_vlan':'None'}},
        ap_list = []
    )
    wgs_cfg_02 = dict(
        description = 'rat-wgs-integration-02',
        name = 'rat-wgs-integration-02',
        vlan_override = False,
        wlan_member = {'rat-wlangroups-integration':{'vlan_override':'No Change', 'original_vlan':'None'}},
        ap_list = []
    )

    test_params = dict(
        tunnel = False,
        vlan_override = False,
        root_ap_01 = '',
        root_ap_02 = '',
        mesh_ap = '',
        wgs_cfg_list = [wgs_cfg_01],
        wlan_cfg = get_wlan_cfg('rat-wlangroups-integration', {}),
        target_ip = '192.168.0.252',
        target_station = '',
        client_roam = False,
        map_roam = False,
        expected_subnet = '20.0.2.0/255.255.255.0'
    )
    test_params.update(params)

    wgs_cfg_01['ap_list'].append(test_params['root_ap_01'])
    wgs_cfg_01['ap_list'].append(test_params['mesh_ap'])
    if diff_wgs:
        wgs_cfg_02['ap_list'].append(test_params['root_ap_02'])
        test_params['wgs_cfg_list'].append(wgs_cfg_02)
    else:
        wgs_cfg_01['ap_list'].append(test_params['root_ap_02'])

    if test_params['vlan_override']:
        test_params['expected_subnet'] = '20.14.83.0/255.255.255.0'

    if test_params['vlan_override'] and not test_params['tunnel']:
        for i in range(len(test_params['wgs_cfg_list'])):
                       test_params['wgs_cfg_list'][i]['wlan_member'] = {'rat-wlangroups-integration':{'vlan_override':'Tag', 'tag_override':'3677'}}


    return test_params

def getTestbedLogic():
    tb_logic_list = ['l2.mesh.fanout', 'l3.mesh.fanout', 'mesh.specific']
    tb_list = []
    for i in range(len(tb_logic_list)):
        tb_list.append("  %d - %s" % (i, tb_logic_list[i]))
    print "Station IP list:"
    print "\n".join(tb_list)
    message = "Pick an testbed logic for current testbed: "
    id = raw_input(message)
    try:
        tb_logic = tb_logic_list[int(id)]
    except:
        tb_logic = ""
    return tb_logic

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    while True:
        target_station = testsuite.getTargetStation(sta_ip_list, "Pick an Windows Vista wireless station: ")
        if target_station: break
        print "Pick at least one station as your target"

    ap_list = []
    while len(ap_list)<3:
        showNotice()
        ap_list = testsuite.getActiveAp(ap_sym_dict)
        print ap_list
    root_ap_01 = ap_list[0]
    root_ap_02 = ap_list[1]
    mesh_ap = ap_list[2]

    tb_logic = getTestbedLogic()

    connection_mode = "l2"
    while True:
        connection_mode = raw_input("Please enter connection mode [l2/l3]: ")
        if connection_mode.strip(): break
        print "Input l2/l3 as connection mode"
    connection_mode = {"L2": "L2LWAPP", "L3": "L3LWAPP" }[connection_mode.upper()]
    target_ip = raw_input("Target IP Address [enter = '192.168.0.252']")
    target_ip = target_ip.strip()
    if target_ip == "": target_ip = "192.168.0.252"

    default_test_params = {'root_ap_01': root_ap_01,
                           'root_ap_02': root_ap_02,
                           'mesh_ap': mesh_ap,
                           'target_station': target_station,
                           'target_ip': target_ip}

    test_name = 'ZD_WLAN_Groups_Integration'
    ts_description = 'Wlan Groups Integration test case with Vlan Override, Tunnel, Roaming'
    test_order = 1
    test_added = 0

    if tb_logic == 'mesh.specific':
        wlangroup_ts = testsuite.get_testsuite('ZD_WLAN_Groups_Integration_MAP_Roam_%s' % connection_mode, ts_description)
        for diff_wgs in [False, True]:
            for tunnel in [False, True]:
                    description = getDescription(connection_mode, vlan_override = True, tunnel = tunnel,
                                                 diff_wgs = diff_wgs, map_roam = True, client_roam = False)
                    common_name = getCommonName(test_order, description)
                    vlan_tunnel_setting = {'vlan_override': True, 'tunnel': tunnel, 'map_roam':True}
                    test_params = default_test_params.copy()
                    test_params.update(vlan_tunnel_setting)
                    test_params = getTestParams(test_params, diff_wgs = diff_wgs)
                    testsuite.addTestCase(wlangroup_ts, test_name, common_name, test_params, test_order)
                    test_added = test_added + 1
                    test_order = test_order + 1
    else:
        wlangroup_ts = testsuite.get_testsuite('ZD_WLAN_Groups_Integration_%s' % connection_mode, ts_description)
        for vlan_override in [False,True]:
            for tunnel in [False, True]:
                description = getDescription(connection_mode, vlan_override, tunnel)
                common_name = getCommonName(test_order, description)
                vlan_tunnel_setting = {'vlan_override': vlan_override, 'tunnel': tunnel}
                test_params = default_test_params.copy()
                test_params.update(vlan_tunnel_setting)
                test_params = getTestParams(test_params)
                testsuite.addTestCase(wlangroup_ts, test_name, common_name, test_params, test_order)
                test_added = test_added + 1
                test_order = test_order + 1

        for diff_wgs in [False, True]:
            for tunnel in [False, True]:
                    description = getDescription(connection_mode, vlan_override = True, tunnel = tunnel,
                                                 diff_wgs = diff_wgs, map_roam = False, client_roam = True)
                    common_name = getCommonName(test_order, description)
                    vlan_tunnel_setting = {'vlan_override': True, 'tunnel': tunnel, 'client_roam' : True}
                    test_params = default_test_params.copy()
                    test_params.update(vlan_tunnel_setting)
                    test_params = getTestParams(test_params, diff_wgs = diff_wgs)
                    testsuite.addTestCase(wlangroup_ts, test_name, common_name, test_params, test_order)
                    test_added = test_added + 1
                    test_order = test_order + 1


    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, wlangroup_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
