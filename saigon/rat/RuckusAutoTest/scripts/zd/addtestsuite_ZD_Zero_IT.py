import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(mid,sid):
    return u'TCID:06.01.%02d.%02d' % (mid, sid)

def makeWlanCfg():
    ssid = "rat-zero-it-%s" % time.strftime("%H%M%S")
    wlan_cfg = []

    # Open System
    wlan_cfg.append((dict(ssid=ssid, auth="open", wpa_ver="", encryption="none", sta_auth="open",
                          sta_wpa_ver="", sta_encryption="none", key_index="" , key_string="",
                          username="ras.local.user", password="ras.local.user", ras_addr="",
                          ras_port="", ras_secret="", use_radius=False, use_zero_it=True),
                     {'Windows XP':_tcid(1,1), 'Windows Vista':_tcid(2,1)},
                     'Zero-IT with Open WLAN'))

    # Open-WEP-64
    wlan_cfg.append((dict(ssid=ssid, auth="open", wpa_ver="", encryption="WEP-64",
                          sta_auth="open", sta_wpa_ver="", sta_encryption="WEP-64",
                          key_index="1" , key_string=utils.make_random_string(10,"hex"),
                          username="ras.local.user", password="ras.local.user",
                          ras_addr="", ras_port="", ras_secret="", use_radius=False, use_zero_it=True),
                     {'Windows XP':_tcid(1,2), 'Windows Vista':_tcid(2,2)},
                     'Zero-IT with Open/WEP/64 WLAN'))

    # Open-WEP-128
    wlan_cfg.append((dict(ssid=ssid, auth="open", wpa_ver="", encryption="WEP-128",
                          sta_auth="open", sta_wpa_ver="", sta_encryption="WEP-128",
                          key_index="1" , key_string=utils.make_random_string(26,"hex"),
                          username="ras.local.user", password="ras.local.user",
                          ras_addr="", ras_port="", ras_secret="", use_radius=False, use_zero_it=True),
                     {'Windows XP':_tcid(1,3), 'Windows Vista':_tcid(2,3)},
                     'Zero-IT with Open/WEP/128 WLAN'))

    # Shared-WEP-64
#    wlan_cfg.append((dict(ssid=ssid, auth="shared", wpa_ver="", encryption="WEP-64",
#                          sta_auth="shared", sta_wpa_ver="", sta_encryption="WEP-64",
#                          key_index="1" , key_string=utils.make_random_string(10,"hex"),
#                          username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="", ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,4), 'Windows Vista':_tcid(2,4)},
#                     'Zero-IT with Shared/WEP/64 WLAN'))
#
#    # Shared-WEP-128
#    wlan_cfg.append((dict(ssid=ssid, auth="shared", wpa_ver="", encryption="WEP-128",
#                          sta_auth="shared", sta_wpa_ver="",sta_encryption="WEP-128",
#                          key_index="1" , key_string=utils.make_random_string(26,"hex"),
#                          username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="", ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,5), 'Windows Vista':_tcid(2,5)},
#                     'Zero-IT with Shared/WEP/128 WLAN'))
#
#    # WPA-PSK-TKIP
#    wlan_cfg.append((dict(ssid=ssid, auth="PSK", wpa_ver="WPA", encryption="TKIP",
#                          sta_auth="PSK", sta_wpa_ver="WPA", sta_encryption="TKIP",
#                          key_index="" , key_string=utils.make_random_string(random.randint(8,63),"hex"),
#                          username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="", ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,6), 'Windows Vista':_tcid(2,6)},
#                     'Zero-IT with PSK/WPA/TKIP WLAN'))
#
#    # WPA-PSK-AES
#    wlan_cfg.append((dict(ssid=ssid, auth="PSK", wpa_ver="WPA", encryption="AES",
#                          sta_auth="PSK", sta_wpa_ver="WPA", sta_encryption="AES",
#                          key_index="" , key_string=utils.make_random_string(random.randint(8,63),"hex"),
#                          username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="",ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,7), 'Windows Vista':_tcid(2,7)},
#                     'Zero-IT with PSK/WPA/AES WLAN'))
#
#    # WPA2-PSK-TKIP
#    wlan_cfg.append((dict(ssid=ssid, auth="PSK", wpa_ver="WPA2", encryption="TKIP",
#                          sta_auth="PSK", sta_wpa_ver="WPA2", sta_encryption="TKIP",
#                          key_index="" , key_string=utils.make_random_string(random.randint(8,63),"hex"),
#                          username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="",ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,8), 'Windows Vista':_tcid(2,8)},
#                     'Zero-IT with PSK/WPA2/TKIP WLAN'))

    # WPA2-PSK-AES
    wlan_cfg.append((dict(ssid=ssid, auth="PSK", wpa_ver="WPA2", encryption="AES",
                          sta_auth="PSK", sta_wpa_ver="WPA2", sta_encryption="AES",
                          key_index="" , key_string=utils.make_random_string(random.randint(8,63),"hex"),
                          username="ras.local.user", password="ras.local.user",
                          ras_addr="", ras_port="",ras_secret="", use_radius=False, use_zero_it=True),
                     {'Windows XP':_tcid(1,9), 'Windows Vista':_tcid(2,9)},
                     'Zero-IT with PSK/WPA2/AES WLAN'))

#    # EAP-WPA-TKIP
#    wlan_cfg.append((dict(ssid=ssid, auth="EAP", wpa_ver="WPA", encryption="TKIP",
#                          sta_auth="EAP", sta_wpa_ver="WPA", sta_encryption="TKIP",
#                          key_index="" , key_string="",username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="",ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,10), 'Windows Vista':_tcid(2,10)},
#                     'Zero-IT with EAP/WPA/TKIP WLAN'))
#
#    # EAP-WPA-AES
#    wlan_cfg.append((dict(ssid=ssid, auth="EAP", wpa_ver="WPA", encryption="AES",
#                          sta_auth="EAP", sta_wpa_ver="WPA", sta_encryption="AES",
#                          key_index="" , key_string="",username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="",ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,11), 'Windows Vista':_tcid(2,11)},
#                     'Zero-IT with EAP/WPA/AES WLAN'))
#
    # EAP-WPA2-TKIP
#    wlan_cfg.append((dict(ssid=ssid, auth="EAP", wpa_ver="WPA2", encryption="TKIP",
#                          sta_auth="EAP", sta_wpa_ver="WPA2", sta_encryption="TKIP",
#                          key_index="" , key_string="",username="ras.local.user", password="ras.local.user",
#                          ras_addr="", ras_port="",ras_secret="", use_radius=False, use_zero_it=True),
#                     {'Windows XP':_tcid(1,12), 'Windows Vista':_tcid(2,12)},
#                     'Zero-IT with EAP/WPA2/TKIP WLAN'))

    # EAP-WPA2-AES
    wlan_cfg.append((dict(ssid=ssid, auth="EAP", wpa_ver="WPA2", encryption="AES",
                          sta_auth="EAP", sta_wpa_ver="WPA2", sta_encryption="AES",
                          key_index="" , key_string="",username="ras.local.user", password="ras.local.user",
                          ras_addr="", ras_port="",ras_secret="", use_radius=False, use_zero_it=True),
                     {'Windows XP':_tcid(1,13), 'Windows Vista':_tcid(2,13)},
                     'Zero-IT with EAP/WPA2/AES WLAN'))

    return wlan_cfg

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_xp = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    serv_ip = testsuite.getTestbedServerIp(tbcfg)
    test_stas = {}
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        test_stas['Windows XP'] = \
            testsuite.getTargetStation(tbcfg['sta_ip_list'],
                             "Pick an XP client from the list above, press ENTER to skip: ")
        sta_xp_radio = testsuite.get_target_sta_radio()
    else:
        test_stas['Windows XP'] = sta_ip_list[attrs["sta_xp"][0]]
        sta_xp_radio = attrs["sta_xp"][1]
        
    test_name = 'ZD_EncryptionTypes_ZeroIT'
    test_params = {'ip': serv_ip}
    wlan_cfgs = makeWlanCfg()

    test_order = 1
    test_added = 0
    for os_name, target_sta in test_stas.items():
        if attrs["interactive_mode"]:
            if not target_sta: continue
        elif target_sta==None: continue
        testsuite_name = 'Zero-IT Activation - %s' % os_name
        testsuite_desc = 'Verify the execution of Zero-IT tool on %s wireless client' % os_name
        ts = testsuite.get_testsuite(testsuite_name, testsuite_desc)
        
        for wlan_cfg, test_id, common_name in wlan_cfgs:
            test_params['wlan_cfg'] = wlan_cfg
            test_params['target_station'] = target_sta
            test_params['use_winxp_sta'] = True if os_name == 'Windows XP' else False
            test_params['target_sta_radio'] = sta_xp_radio if os_name == 'Windows XP' else sta_vista_radio
            test_id[os_name] = "%s.%d" % (test_id[os_name],const.get_radio_id(test_params['target_sta_radio']))
            common_name = "%s - %s" % (test_id[os_name], common_name)
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
