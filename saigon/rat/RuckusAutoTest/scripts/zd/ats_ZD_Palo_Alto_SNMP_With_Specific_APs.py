import sys
import random
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

pp = pprint.PrettyPrinter(indent=4)

def getDescription(id):
    description = dict()
    description["2"] = "Configuring SNMP function from WebUI"
    description["3"] = "Checking Ruckus MIB working fine with MIB-WALK"
    description["5"] = "Checking ruckusZDSystemMIB-1"
    description["6"] = "Checking ruckusZDSystemMIB-2"
    description["7"] = "Checking ruckusZDWLANMIB-1"
    description["8"] = "Checking ruckusZDWLANMIB-2"
    description["9"] = "Checking ruckusZDWLANMIB-3"
    description["10"] = "Checking APs list appears correctly with SNMP"
    description["11"] = "Checking Clients list apprears correctly with SNMP"
    description["12"] = "Checking Rouge APs list appears correctly with SNMP"
    description["13"] = "Checking traps sent out when APs join"
    description["14"] = "Checking traps sent out when client authentication failed/blocked"
    description["15"] = "Checking traps sent out when Rouge APs detected"
    description["16"] = "Checking traps sent out when APs lost detected"
    description["20"] = "Negative OIDs input"
    return description[id]

def tcidAPSpecificTest(base_id, radio, ap_model_id, ap_role_id, description, ap_type):
    return u'TCID:26.01.%02d.%02d.%s.%s - %s - %s' % (radio, base_id, ap_model_id, ap_role_id, description, ap_type)

def getRadioId(radio):
    if radio == 'g': return 1
    if radio == 'n': return 2
    if radio == 'a': return 3
    if radio == 'na': return 4
    if radio == 'ng': return 5

def get_wlan_cfg(wlan_params):
    wlan_cfg = dict(
        auth = 'PSK',
        encryption = 'TKIP',
        wpa_ver = 'WPA',
        key_string = utils.make_random_string(random.randint(8,63),"hex"),
        ssid = 'rat-snmp'
    )

    wlan_cfg.update(wlan_params)
    return wlan_cfg

def showNotice():
    msg = "Please select 1 AP for test"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)


def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs['interactive_mode']:
        while True:
            target_station = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
            if target_station: break
            print "Pick one station as your target"

        showNotice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
    test_order = 1
    ap_specific_test_order = 1
    test_added = 0
    test_name = ''
    ts_description = 'Test Zone Director\'s SNMP Functionality'
    if attrs['testsuite_name']: ts_name = attrs['testsuite_name']
    else: ts_name = 'ZD SNMP with specific APs'
    snmp_ap_specific_ts = testsuite.get_testsuite(ts_name, ts_description, interactive_mode = attrs["interactive_mode"])
    for active_ap in active_ap_list:
        test_params = {}
        active_ap_conf = ap_sym_dict[active_ap]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
        if attrs['interactive_mode']:
            radio = raw_input("Pick AP (%s) radio mode (g, n, a, na, ng) [enter = g]: " % active_ap)
            if radio.strip() == "":
                radio = "g"
        else: radio = "g"
        test_params['active_ap'] = active_ap
        test_name = 'ZD_SNMP_Trap'
        test_params.update({'snmp_trap_cfg': dict(enabled = True, server_ip = "192.168.0.252")})
        for i in [13, 16]:
            description = getDescription(str(i))
            # define test cases name and OID for each case
            if i == 13: test_params.update({'oid':'1.3.6.1.4.1.25053.2.2.2.2', 'test_case':'ap_join_trap'})
            if i == 16: test_params.update({'oid':'1.3.6.1.4.1.25053.2.2.2.2', 'test_case':'ap_lost_trap'})
            common_name = tcidAPSpecificTest(i, getRadioId(radio), ap_model_id, ap_role_id, description, ap_type)
            testsuite.addTestCase(snmp_ap_specific_ts, test_name, common_name, test_params, ap_specific_test_order)
            ap_specific_test_order = ap_specific_test_order + 1
            test_added = test_added + 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, snmp_ap_specific_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
