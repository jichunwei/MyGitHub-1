import sys
import random
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.SNMP import SNMP as snmp_obj

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

def tcidAPSpecificTest(base_id, radio, description, ap_model=None):
    aptcid = const.get_ap_model_id(ap_model)
    return u'TCID:26.01.%02d.%02d.%02d - %s - %s' % (radio, base_id, aptcid, description, ap_model)

def getRadioId(radio):
    if radio == 'g': return 1
    if radio == 'n': return 2
    if radio == 'a': return 3
    if radio == 'na': return 4
    if radio == 'ng': return 5

def tcidNoneAPSpecificTest(base_id, description):
    return "TCID:26.01.%02d - %s" % (base_id, description)

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
    if attrs['interactive_mode']:
        while True:
            target_station = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
            if target_station: break
            print "Pick one station as your target"
    else:
        target_station = attrs['sta_id']
    default_test_params = dict(
        wlan_cfg = get_wlan_cfg({}),
        target_station = target_station
    )

    test_order = 1
    ap_specific_test_order = 1
    test_added = 0
    test_name = ''
    ts_description = 'Test Zone Director\'s SNMP Functionality'
    ts_name = "ZD SNMP"
    if attrs['testsuite_name']: ts_name = attrs['testsuite_name']
    snmp_ts = testsuite.get_testsuite('ZD_SNMP', ts_description)
    for i in [2,3,5,6,7,8,9,10,11,12,14,20]:
        description = getDescription(str(i))
        test_params = {}
        if i == 2:
            test_name = 'ZD_SNMP_WebUI'
            test_params['max_len'] = 32
        if i in [7,8,9,11,14]:
            test_params = default_test_params.copy()
        if i in [3,5,6,7,8,9,10,11,12,20]:
            test_name = 'ZD_SNMP'
        if i in [14]:
            test_name = 'ZD_SNMP_Trap'
            test_params.update({'snmp_trap_cfg' : dict(enabled = True, server_ip = "192.168.0.252")})
        # define test cases name and OID for each case
        if i == 3: test_params.update({'test_case' : 'mib-walk'})
        #Fix the issue about OID will be changed in different MIB files. Need to install net-snmp.
        tc_id_name_mapping = {5: {'tc_name':'ruckusZDSystemInfo', 
                                  'mib_obj_name':'RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName'},
                              6: {'tc_name':'ruckusZDSystemStats', 
                                  'mib_obj_name':'RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemStatsNumAP'},
                              7: {'tc_name':'ruckusZDWlANInfo', 
                                  'mib_obj_name':'RUCKUS-ZD-WLAN-MIB::ruckusZDWLANTable'},
                              8: {'tc_name':'ruckusZDWLANAPInfo', 
                                  'mib_obj_name':'RUCKUS-ZD-WLAN-MIB::ruckusZDWLANAPTable'},
                              9: {'tc_name':'ruckusZDWLANStaInfo', 
                                  'mib_obj_name':'RUCKUS-ZD-WLAN-MIB::ruckusZDWLANStaTable'},
                              10: {'tc_name':'checkAPList', 
                                   'mib_obj_name':'RUCKUS-ZD-WLAN-MIB::ruckusZDWLANAPEntry'},
                              11: {'tc_name':'checkSta_list', 
                                   'mib_obj_name':'RUCKUS-ZD-WLAN-MIB::ruckusZDWLANStaEntry'},
                              12: {'tc_name':'checkRougeAPList', 
                                   'mib_obj_name':'RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemStatsNumRogue'},
                              14: {'tc_name':'sta_fail_auth_trap', 
                                   'mib_obj_name':'RUCKUS-ZD-EVENT-MIB::ruckusZDEventClientMacAddr'},
                              }
        snmp = snmp_obj({})
        
        if tc_id_name_mapping.has_key(i):
            tc_info_d = tc_id_name_mapping[i]
            tc_name = tc_info_d['tc_name']
            obj_name = tc_info_d['mib_obj_name']
            oid = snmp.translate(obj_name)[0].strip()
            if oid.find('.25053.') < 0:
                raise Exception("Don't get OID correctly. Response is %s" % oid)
            else:
                #Response of translate will add one dot at the beginning, remove dot in the first and last.
                oid = oid[1:] if oid[0] == '.' else oid
                oid = oid[:-1] if oid[-1] == '.' else oid
                test_params.update({'oid':oid, 'test_case':tc_name})
       
        if i == 20: test_params.update({'oid':'192.168.0.2', 'test_case':'negativeOID'})

        common_name = tcidNoneAPSpecificTest(i, description)
        testsuite.addTestCase(snmp_ts, test_name, common_name, test_params, test_order)
        test_order = test_order + 1

        test_added = test_added + 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, snmp_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
