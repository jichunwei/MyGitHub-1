import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(id, radio_id, description, ap_model, ap_type_role, ap_tag):
    aptcid = const.get_ap_model_id(ap_model)
    rband = "2.4G" if radio_id in [1, 2] else "5G"
    xdescription = description + ' - ' + ap_tag + ' -  ' + rband
    aprtid = getApTypeRoleId(ap_type_role)
    return "TCID:34.03.%02d.%02d.%02d.%02d - %s" % (id, radio_id , aptcid, aprtid, xdescription)
    
def getRadioId(radio):
    if radio == 'g': return 1
    if radio == 'n': return 2
    if radio == 'a': return 3
    if radio == 'na': return 4

def apSupport11n(ap_model):
    if re.search("(7942|7962|7762)", ap_model, re.I):
        return True
    return False

def apSupportdualband(ap_model):
    if re.search("(7962|7762)", ap_model, re.I):
        return True
    return False

def getApTypeRoleId(ap_type_role):
    if re.search("(root)", ap_type_role, re.I):
        return 1
    if re.search("(mesh)", ap_type_role, re.I):
        return 2
    if re.search("(ap)", ap_type_role, re.I):
        return 3

def getRadioModeByAPModel(ap_model):
    rlist = []
    if re.search("(2925|2942|2741)", ap_model, re.I):
        rlist.append('g')
    if re.search("(7942)", ap_model, re.I):
        rlist.append('n')
    if re.search("(7962|7762)", ap_model, re.I):
        rlist.append('n')
        rlist.append('na')
    return rlist
    
def getWgsTypeByRadioAndAPModel(radio_mode, ap_model):
    if radio_mode == 'g':
        wgscfg = 'bg'
    elif radio_mode == 'n':
        if re.search("(7962|7762)", ap_model):
            wgscfg = 'ng_na'
        else:
            wgscfg = 'ng'
    elif radio_mode == 'na':
        wgscfg = 'na_ng'
    return wgscfg

def getTestCfg(ssid, auth_server_cfg):
    TestCfg={}
    TestCfg['wlan_cfg'] = {'auth': 'EAP',
                           'encryption': 'AES',
                           'key_index': '',
                           'key_string': '',
                           'ssid': ssid,
                           'sta_auth': 'EAP',
                           'sta_encryption': 'AES',
                           'sta_wpa_ver': 'WPA2',
                           'wpa_ver': 'WPA2'}
    TestCfg['auth_srv'] = {'ras_addr': '192.168.0.250',
                           'ras_port': '18120',
                           'ras_secret': '1234567890'}
    TestCfg['eap_user'] = {'user1': {'dest_ip': '192.168.10.252',
                                     'expected_subnet' : '192.168.10.0/255.255.255.0',
                                     'expected_vlan': '10',
                                     'password': 'finance.user',
                                     'username': 'finance.user'},
                           'user2': {'dest_ip': '192.168.20.252',
                                     'expected_subnet' : '192.168.20.0/255.255.255.0',
                                     'expected_vlan': '20',
                                     'password': 'marketing.user',
                                     'username': 'marketing.user'}}
    TestCfg['auth_srv'].update(auth_server_cfg)
    return TestCfg 

# return list of tuple(wlan_cfg, common_name)
def defineTestCfgByAPModel(ssid, radio_mode, ap_model, ap_type_role, ap_tag):
    if ap_model:
        ap_model = ap_model.upper()
    radio = getRadioId(radio_mode)
    test_cfg_list = \
    [  (  getTestCfg(  ssid, dict(ras_addr='192.168.0.250',
                                  ras_port='18120',
                                  ras_secret='1234567890')),
          tcid(1, radio, "IOP - IAS", ap_model, ap_type_role, ap_tag)),
       (  getTestCfg(  ssid, dict(ras_addr='192.168.0.252',
                                  ras_port='1812',
                                  ras_secret='1234567890')),
          tcid(2, radio, "IOP - FreeRADIUS", ap_model, ap_type_role, ap_tag)),
       #(  getTestCfg(  ssid, dict(ras_addr='192.168.0.250',
       #                           ras_port='1645',
       #                           ras_secret='1234567890')),
       #   tcid(3, radio, "IOP - Cisco ACS", ap_model, ap_type_role, ap_tag)),
    ]
    return test_cfg_list

#if wgscfg=='bg':wgs_cfg={'ap_rp':{'bg': {'wlangroups': 'wlan-wg-bg'}}, 'name': 'wlan-wg-bg','description': 'utest-wg-22bg'}
#if wgscfg=='ng':wgs_cfg={'ap_rp':{'ng':{'wlangroups': 'wlan_wg-ng'}},'name':'wlan-wg-ng','description': 'utest-wg-22ng'}
#if wgscfg=='ng_na':wgs_cfg={'ap_rp':{'ng':{wlangroups':  'wlan_wg-ng'},'na':{'default':True}}, 'name':'wlan-wg-7962ng','description': 'utest-wg-22ng'}
#if wgscfg=='na_ng';wgs_cfg={'ap_rp':{'na':{wlangroups':  'wlan_wg-na'},'ng':{'default':True}}, 'name':'wlan-wg-7962na','description': 'utest-wg-22na'}

def getWgsCfg(mode):
    if mode =='bg':
        wgs_cfg = {'name': 'wlan-wg-bg', 'description': 'utest-wg-22bg', 'ap_rp': {}}
        wgs_cfg['ap_rp']['bg'] = {'wlangroups': wgs_cfg['name']}
    elif mode == 'ng':
        wgs_cfg = {'name': 'wlan-wg-ng', 'description': 'utest-wg-22ng', 'ap_rp': {}}
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
    elif mode == 'ng_na':
        wgs_cfg = {'name': 'wlan-wg-ng-na', 'description': 'utest-wg-22ng-na', 'ap_rp': {}}
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
        wgs_cfg['ap_rp']['na'] = {'default': True}
    else:
        wgs_cfg = {'name': 'wlan-wg-na-ng', 'description': 'utest-wg-22na-ng', 'ap_rp': {}}
        wgs_cfg['ap_rp']['na'] = {'wlangroups': wgs_cfg['name'],'channel':'Auto'}
        wgs_cfg['ap_rp']['ng'] = {'default': True}	
    return wgs_cfg

def getTestParams(test_cfg, wgs_cfg, active_ap, target_station, radio_mode):
    test_params = { 'wgs_cfg': wgs_cfg,
                    'active_ap': active_ap,
                    'target_station': target_station,
                    'radio_mode': radio_mode}
    test_params.update(test_cfg)
    return test_params

def showNotice():
    msg = "Please select the APs under test."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    while True:
        target_sta_11ng = testsuite.getTargetStation(sta_ip_list, "Pick an 11n 2.4G wireless station: ")
        target_sta_11na = testsuite.getTargetStation(sta_ip_list, "Pick an 11n 5.0G wireless station: ")
        if (target_sta_11ng or target_sta_11na): break
        print "Pick at least one station as your target"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    ts = testsuite.get_testsuite( "Mesh - Dynamic VLAN - IOP - WlanGroups"
       , "Verify dynamic function with different Authentication Server in mesh environment.")

    ssid = "rat-dvlanWGS-mesh"

    test_order = 1
    test_added = 0
    test_name="ZD_DynamicVLAN_WlanGroups"

    for active_ap in sorted(active_ap_list):       
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg)
        radio_mode_list = getRadioModeByAPModel(apcfg['model'])
        for radio_mode in radio_mode_list:
            test_cfg_list = defineTestCfgByAPModel(ssid, radio_mode, apcfg['model'], ap_type_role, active_ap)
            wgscfg = getWgsTypeByRadioAndAPModel(radio_mode, apcfg['model'])
            target_sta = target_sta_11na if radio_mode == 'na' else target_sta_11ng
            if target_sta:
                for test_cfg, common_name in test_cfg_list:
                    test_params = getTestParams( test_cfg,
                                                 getWgsCfg(wgscfg),
                                                 active_ap,
                                                 target_sta,
                                                 radio_mode)
                    if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                        test_added += 1
                    test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
