import sys
import random
import re
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common.lib_Constant import *
from libZD_TestSuite import *

def get_support_dual_band(ap_model):
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

def get_wgs_type_by_radio_and_ap_model(radio_mode, ap_model):
    if radio_mode == 'g':
        wgs_type = 'bg'
    elif radio_mode == 'n':
        if re.search("(7962|7762)", ap_model):
            wgs_type = 'ng_na'
        else:
            wgs_type = 'ng'
    elif radio_mode == 'na':
        wgs_type = 'na_ng'
    return wgs_type

def define_Wlan_cfg(ssid, ras_ip_addr):
    wlan_cfgs = []
    '''
    wlan_cfgs.append(dict(ssid = ssid + "-openNONE", auth = "open", wpa_ver = "", encryption = "none",
                          key_index = "" , key_string = "",
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-openWEP64", auth = "open", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-openWEP128", auth = "open", wpa_ver = "", encryption = "WEP-128",
                          key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-WpaPskTkip", auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-WpaPskAes", auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-Wpa2PskTkip", auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-Wpa2PskAes", auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-shareWEP64", auth = "shared", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = ""))

    wlan_cfgs.append(dict(ssid = ssid + "-shareWEP128", auth = "shared", wpa_ver = "", encryption = "WEP-128",
                          key_index = "2" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = ""))
    '''

    wlan_cfgs.append(dict(ssid = ssid + "-EapWpaTkip", auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    wlan_cfgs.append(dict(ssid = ssid + "-EapWpaAes", auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    wlan_cfgs.append(dict(ssid = ssid + "-EapWpa2Tkip", auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    wlan_cfgs.append(dict(ssid = ssid + "-EapWpa2Aes", auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    return wlan_cfgs

def get_wgs_cfg(wgs_type):
    wgs_cfg = {'name': 'Encryption_Group', 'description': '', 'ap_rp': {}}
    if wgs_type =='bg':
        wgs_cfg['ap_rp']['bg'] = {'wlangroups': wgs_cfg['name']}
    elif wgs_type == 'ng':
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
    elif wgs_type == 'ng_na':
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
        wgs_cfg['ap_rp']['na'] = {'default': 'EmptyWlanGroup'}
    else:
        wgs_cfg['ap_rp']['na'] = {'wlangroups': wgs_cfg['name'], 'channel':'157'}
        wgs_cfg['ap_rp']['ng'] = {'default': 'EmptyWlanGroup'}
    return wgs_cfg

def define_test_cfg(**kwargs):
    fcfg = dict( ap_tag = 'dut_ap',
                 sta_tag = 'bg_sta',
		 wlan_cfg_list = [],
		 ssid = 'ssid',
		 radio_mode = 'radio_mode',
                 ras_cfg = dict(server_addr = '192.168.0.252',
                                server_port = '1812',
                                server_name = '',
                                radius_auth_secret = '1234567890'),
                 )

    fcfg.update(kwargs)
    wgs_cfg = get_wgs_cfg(fcfg['wgs_type'])
    test_cfg = list()
    if fcfg['wgs_type'] in ['bg', 'ng', 'ng_na', 'na_ng']:
        test_cfg.extend(
        [
         ( dict(active_ap = fcfg['active_ap']),
           "CB_ZD_Find_Active_AP",
           "get the active AP",0, False),

         ( dict(target_station = fcfg['target_station']),
           "CB_ZD_Find_Station",
           "get the station",0, False),

         ( dict({}),
           "CB_ZD_Remove_All_Config",
           "remove all configuration from ZD",0, False),

         ( dict(auth_ser_cfg_list = [fcfg['ras_cfg']]),
           "CB_ZD_Create_Authentication_Server",
           "create the authentication server",0, False),

         ( dict(wgs_cfg=dict(name='EmptyWlanGroup', description='EmptyWlanGroup')),
           "CB_ZD_Create_Empty_Wlan_Group",
           "create a wlan group [EmptyWlanGroup]",0, False),

         ( dict({}),
           "CB_ZD_Assign_All_APs_To_Empty_Wlan_Group",
           "assign all APs to empty wlan group",0, False),

         ( dict(wgs_cfg=wgs_cfg),
           "CB_ZD_Create_Wlan_Group",
           "create a wlan group on ZD",0, False),

	 ( dict(active_ap=fcfg['active_ap'], ap_tag=fcfg['ap_tag']),
           "CB_ZD_Create_Active_AP",
           "Verify active AP exists on ZD",0, False),

         ( dict(ap_tag=fcfg['ap_tag'], wgs_cfg=wgs_cfg),
           "CB_ZD_Config_Wlan_Group_On_AP",
           "assign wlan group on active AP",0, False),

        ])
        test_cfg.extend(define_test_cfg_1(**fcfg))
        test_cfg.extend(
	[
	  ( dict({}),
	    "CB_ZD_Remove_All_Config",
	    "remove all configuration from ZD after test",0, False),		
        ])

    return test_cfg

def define_test_cfg_1(**kwargs):
    fcfg = dict( ap_tag = 'dut_ap',
                 sta_tag = 'bg_sta',
                 wlan_cfg_list = [],
                 ssid = 'ssid',
                 radio_mode = 'radio_mode',
		 wlan_cfg = 'wlan_cfg',
                 ras_cfg = dict(server_addr = '192.168.0.252',
                                server_port = '1812',
                                server_name = '',
                                radius_auth_secret = '1234567890'),
                 )
    fcfg.update(kwargs)
    wgs_cfg = get_wgs_cfg(fcfg['wgs_type'])
    test_cfg_1 = list()
    for wlan_cfg in fcfg['wlan_cfg_list']:
	short_ssid = wlan_cfg['ssid'][10:]    
        test_cfg_1.extend(
            [
            ( wlan_cfg,
              "CB_ZD_Create_Single_Wlan",
	      "create a wlan [%s] on ZD" % short_ssid,1, False),

            ( dict(wlan_list=[wlan_cfg['ssid']], wgs_cfg=wgs_cfg),
              "CB_ZD_Config_Wlan_On_Wlan_Group",
              "Configure wlan [%s] on wlan group" % short_ssid,2, False),

            ( dict(ssid=wlan_cfg['ssid']),
              "CB_ZD_Verify_Wlan_On_APs",
              "wlan [%s]: verify the wlan on the active AP" % short_ssid,2, False),

            ( dict(wlan_cfg=wlan_cfg),
              "CB_ZD_Associate_Station",
              "wlan [%s]: associate the station" % short_ssid,2, False),

            ( dict({}),
              "CB_ZD_Get_Station_Wifi_Addr",
              "wlan [%s]: get wifi address of the station"% short_ssid,2, False),

            ( dict(target_ip=fcfg['ras_cfg']['server_addr']),
              "CB_ZD_Client_Ping_Dest_Is_Allowed",
              "wlan [%s]: the station ping a target ip"% short_ssid,2, False),

            ( dict(radio_mode=fcfg['wgs_type'], wlan_cfg=wlan_cfg),
              "CB_ZD_Verify_Station_Info",
              "wlan [%s]: verify the station information on ZD"% short_ssid,2, False),

            ( dict(ssid=wlan_cfg['ssid']),
              "CB_ZD_Verify_Station_Info_On_AP",
              "wlan [%s]: verify the station information on the active AP"% short_ssid,2, False),

            ( dict(wlan_list=[wlan_cfg['ssid']], wgs_cfg=wgs_cfg),
              "CB_ZD_Remove_Wlan_On_Wlan_Group",
              "wlan [%s]: remove wlans on active wlan group"% short_ssid,2, True),
        ])
    return test_cfg_1

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_11ng = 0,
        sta_11na = 0,
	radio_type = "",
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)


    if attrs['interactive_mode']:

        print "Please pick up one AP for testing"
        active_ap_list = getActiveAp(ap_sym_dict)
        print "Active AP : %s" % active_ap_list
        active_ap = active_ap_list.pop()
        target_sta = getTargetStation(tbcfg['sta_ip_list'])
	#sta_ip_addr = getTargetStation(tbcfg['sta_ip_list'])
    else:
        active_ap = attrs['active_ap']
        sta_ip_addr = attrs['sta_ip_addr']
    apcfg = ap_sym_dict[active_ap]
    ap_model_id = get_ap_model_id(apcfg['model'])
    ap_role_id = get_ap_role_by_status(apcfg['status'])
    
    if apcfg['model'].find('2942') != -1: wgs_type = 'bg'
    if apcfg['model'].find('7942') != -1: wgs_type = 'ng'
    
    if get_support_dual_band(apcfg['model']):
            if attrs['interactive_mode']:
                bandopt = {'0':'ng_na', '1':'na_ng'}
                while 1:
                    dut_band = raw_input("Please select 2.4G or 5G band you want to test[1/0] (0:2.4G, 1:5G):")
                    if dut_band not in ['0', '1']:
                        print "Input Error"
                        continue
                    else:
                        wgs_type = bandopt[dut_band]
                        break
            else:
                 wgs_type = 'na_ng' if attrs['radio_type'].lower() == '5G'.lower() else 'ng_na'

    ssid = "rat-ETWGS"
    wlan_cfg_list = define_Wlan_cfg(ssid, ras_ip_addr)


    radio_id = 2 if wgs_type == 'na_ng' else 1
    TCID = "TCID:00.01.%02d.%02d.%02d" % (ap_model_id, ap_role_id, radio_id)
    ts_name = "%s Mesh-EncryptionTypesEap-WGS-Combo" % TCID
    ts_name += "-%s" % apcfg['model'].upper()
    if wgs_type == 'na_ng':
        ts_name += "-5G"
    test_cfgs = define_test_cfg(**dict(active_ap=active_ap, wgs_type=wgs_type, target_station=target_sta, wlan_cfg_list=wlan_cfg_list))
    ts = testsuite.get_testsuite(ts_name,
                                     "Verify different encryption types in mesh environment",
                                     interactive_mode = attrs["interactive_mode"],
                                     combotest=True)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)


if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    #import pdb; pdb.set_trace()
    createTestSuite(**_dict)
