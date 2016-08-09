import time
import logging

import csvUtil
import WGconfig_cfgLib_ref6 as BCLIB
import defaultWlanConfigParams_ref4 as DWCFG

from RuckusAutoTest.components.RemoteStationWinPC import RemoteStationWinPC as RPC
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector

###
### Testbed data base
###
# provide 1st name of wlan-group
mytb = {'wgs_name': 'MultiWgsHelpQaWorkOnRuckus'}
# provide Guest & Hotspot Wlan names
#mytb['wlans'] = ['guest-1','guest-2','guest-3','hotspot-2','hotspot-3']
mytb['wlans'] = ['DPSK']
# 6 wlans and encryption modes; please refer to defaultWlanConfigParams for details
#mytb['wlans'] = ['psk-wpa2-tkip-zeroIT-Dpsk-T','psk-wpa2-tkip-zeroIT-T','psk-wpa2-aes', 'psk-wpa2-tkip', 'share-wep128','open-wep128']
acl_conf = {'acl_name':'TestForFunL2ACL', 'description':'L2AccessControl', 'allowed_access': True, 'mac_list':['00:00:00:00:11:00', '00:22:43:13:39:30', '00:21:6A:2B:34:E2', '00:22:43:13:4B:2B']}
L3acl_conf = {'name':'TestForFunL3ACL', 'description':'L3L4AcessControl', 'default_mode':'allow-all', 'rules':[]}
L3acl_conf['rules'] = [{'description':'SNMP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SNMP'},
             {'description':'HTTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'HTTP'},
             {'description':'HTTPS-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'HTTPS'},
             {'description':'FTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'FTP'},
             {'description':'SSH-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SSH'},
             {'description':'TELNET-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'TELNET'},
             {'description':'SMTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SMTP'},
             {'description':'DHCP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'DHCP'},
             {'description':'DNS-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'DNS'},
             {'description':'Any-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':''},
             {'description':'protocol-ACLRuleNTP', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'protocol':'17', 'dst_port':'123'},
             {'description':'protocol-ACLRuleTFTP', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'protocol':'17', 'dst_port':'69'},
             {'description':'SNMP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SNMP'},
             {'description':'HTTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'HTTP'},
             {'description':'HTTPS-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'HTTPS'},
             {'description':'FTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'FTP'},
             {'description':'SSH-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SSH'},
             {'description':'TELNET-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'TELNET'},
             {'description':'SMTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SMTP'},
             {'description':'DHCP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'DHCP'},
             {'description':'DNS-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'DNS'},
             {'description':'Any-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':''},
             {'description':'protocol-ACLRuleNTP', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'protocol':'17', 'dst_port':'123'},
             {'description':'protocol-ACLRuleTFTP', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'protocol':'17', 'dst_port':'69'},
             {'description':'SNMP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SNMP'},
             {'description':'HTTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'HTTP'},
             {'description':'HTTPS-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'HTTPS'},
             {'description':'FTP-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'FTP'},
             {'description':'SSH-ACLRule', 'action':'Deny', 'dst_addr':'192.168.0.2/24', 'application':'SSH'}, ]

wispr_params = {'username':'jchu', 'password':'happy', 'redirect_url':'http://192.168.0.202', 'original_url':'http://192.168.0.210'}
guest_params = {'guest_pass':'', 'use_tou':True, 'redirect_url':'http://192.168.0.202'}
zeroit_params = {'eth_if_ip_addr':'192.168.1.12', 'ip_addr':'192.168.0.112',
                 'net_mask':'255.255.255.0', 'auth_method':'', 'use_radius':'', 'activate_url':'http://192.168.0.2/activate',
                 'username':'TestingisFunJob', 'password':'TestingisFunJob', 'ssid':'DPSK'}

def create_zd(conf):
    cfg = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    cfg.update(conf)

    logging.info("Starting up ZoneDirector [%s]" % cfg['ip_addr'])

    zd = ZoneDirector(cfg)
    zd.start()

    return zd

#Test client association w/ ZD in round robin fashion w/ different wlans detected by remote Clients
#This method can test whatever wlans are configured on ZD
def do_station1_test(**kwargs):
    fcfg = dict(sta_ip_addr = '192.168.1.10', sleep = 10, repeat = 1, debug = False)
    fcfg.update(kwargs)
    halt(fcfg['debug'])
    sta = RPC(dict(sta_ip_addr = fcfg['sta_ip_addr']))
    sta.do_cmd('get_current_status')
    sta.do_cmd('remove_all_wlan')
    for r in range(1, int(fcfg['repeat']) + 1):
        for wlan_id in mytb['wlans']:
            sta.do_cmd('check_ssid', {'ssid': wlan_id})
            wlan_conf = DWCFG.get_cfg(wlan_id)
            time.sleep(fcfg['sleep'])
            sta.get_current_status()

        for i in range(10):
            sta.cfg_wlan(wlan_conf)
            wlan_ip = sta.get_wifi_addresses()
            if wlan_ip[0] not in ['0.0.0.0', '']: break
            time.sleep(10)

            if wlan_id in ['guest-1', 'guest-2', 'guest-3']:
                for c in range(1, 10):
                    try:
                        sta.do_cmd("perform_guest_auth", str(guest_params))
                        time.sleep(5)
                    except:
                        pass

            if wlan_id in ['hotspot-1', 'hotspot-2', 'hotspot-3']:
                for c in range(1, 10):
                    try:
                        sta.do_cmd("perform_hotspot_auth", str(wispr_params))
                        time.sleep(5)
                    except:
                        pass

            #sta.ping(client_ip, timeout_ms=3000)
            sta.do_cmd('remove_all_wlan')

    return 0

# Test multiple users w/ ZeroIT configurations
def do_sta1_zeroit_test(zd, **kwargs):
    fcfg = dict(sta_ip_addr = '192.168.1.10', sleep = 10, repeat = 1, debug = False)
    fcfg.update(kwargs)
    halt(fcfg['debug'])
    sta = RPC(dict(sta_ip_addr = fcfg['sta_ip_addr']))
    zd_user = BCLIB.get_zd_user(zd)
    for r in range(1, int(fcfg['repeat']) + 1):
        for wlan_id in mytb['wlans']:
            sta.do_cmd('check_ssid', {'ssid': wlan_id})
            for user in zd_user:
                zeroit_params['username'] = user
                zeroit_params['password'] = user
                sta.do_cmd('get_current_status')
                sta.do_cmd('remove_all_wlan')
                sta.do_cmd("cfg_wlan_with_zero_it", str(zeroit_params))
                time.sleep(fcfg['sleep'])
                sta.get_current_status()
                for i in range(10):
                    wlan_ip = sta.get_wifi_addresses()
                if wlan_ip[0] not in ['0.0.0.0', '']:
                    break
                time.sleep(10)
                client_ip = wlan_ip[0]
                sta.ping(client_ip, timeout_ms = 3000)
                logging.info("ZeroIT User Name %s" % (zeroit_params['username']))
                sta.do_cmd('remove_all_wlan')

    return 0

# Convert batch_dpsk.csv file into dictionary and then send each dpsk to Client for association process
def do_sta1_batch_psk_test(**kwargs):
    fcfg = dict(sta_ip_addr = '192.168.1.12', sleep = 10, repeat = 1, debug = False)
    fcfg.update(kwargs)
    halt(fcfg['debug'])
    sta = RPC(dict(sta_ip_addr = fcfg['sta_ip_addr']))
    sta.do_cmd('get_current_status')
    sta.do_cmd('remove_all_wlan')

    for r in range(1, int(fcfg['repeat']) + 1):
        for wlan_id in mytb['wlans']:
            sta.do_cmd('check_ssid', {'ssid': wlan_id})
            csvid = csvUtil.csv_as_list_dict("batch_dpsk_102409_16_06.csv")

        for raw in csvid:
            logging.info("User Name %s" % (raw['User Name']))
            wlan_conf = DWCFG.get_cfg(wlan_id)
            wlan_conf['key_string'] = raw['Passphrase']
            sta.cfg_wlan(wlan_conf)
            time.sleep(fcfg['sleep'])
            sta.get_current_status()
            for i in range(10):
                wlan_ip = sta.get_wifi_addresses()
            if wlan_ip[0] not in ['0.0.0.0', '']:
                break
            time.sleep(10)
            wlan_ip = sta.get_wifi_addresses()
            clientIp = wlan_ip[0]
            sta.ping(clientIp, timeout_ms = 3000)
        sta.do_cmd('remove_all_wlan')

    return 0

def do_station2_test(**kwargs):
    fcfg = dict(sta_ip_addr = '192.168.2.12', sleep = 10, repeat = 1, debug = False)
    fcfg.update(kwargs)
    halt(fcfg['debug'])
    sta = RPC(dict(sta_ip_addr = fcfg['sta_ip_addr']))
    sta.do_cmd('get_current_status')
    sta.do_cmd('remove_all_wlan')
    for r in range(1, int(fcfg['repeat']) + 1):
        for wlan_id in mytb['wlans']:
            sta.do_cmd('check_ssid', {'ssid': wlan_id})
            wlan_conf = DWCFG.get_cfg(wlan_id)
            sta.cfg_wlan(wlan_conf)
            time.sleep(fcfg['sleep'])
            sta.get_current_status()
            wlan_ip = sta.get_wifi_addresses()
            client_ip = wlan_ip[0]
            sta.ping(client_ip, timeout_ms = 3000)
            sta.do_cmd('remove_all_wlan')

    return 0

def halt(debug = False):
    if debug:
        import pdb
        pdb.set_trace()

def do_cfg(**kwargs):
    fcfg = dict(debug = False, do_config = True, username = 'admin', password = 'admin')
    fcfg.update(kwargs)
    halt(fcfg['debug'])

    zd = create_zd(fcfg)
    if not fcfg['do_config']:
        return zd

    #try:
    #    BCLIB.remove_wlan_config(zd)
    #except:
    #    pass
    #BCLIB.create_l2_acl_policy(zd, acl_conf, num_of_acl=1)
# Add ACL Clone function to speed up Max. ACL configurations
    #BCLIB.create_l2_acl_clone(zd, acl_conf, num_of_acl=30)
    #BCLIB.create_l3_acl_policy(zd, L3acl_conf, num_of_acl=3)
    #BCLIB.create_l3_acl_clone(zd, L3acl_conf, num_of_acl=31)
    #BCLIB.create_users(zd, username='TestingisFunJob', password='TestingisFunJob', fullname='TestingisFunJob', number_of_users=10)
    #BCLIB.create_wlans(zd, mytb)
    #BCLIB.create_wlan_group(zd, mytb)
    #BCLIB.create_multi_wlan_groups(zd, mytb)
    #BCLIB.align_wlan_group_sn_wlan(zd, mytb)

    return zd


# configure every AP on ZD w/ different WlanGroup
def do_test(zd, **kwargs):
    fcfg = dict(debug = False, sleep = 3, repeat = 1)
    fcfg.update(kwargs)
    halt(fcfg['debug'])
    wgs_list = BCLIB.get_wlan_groups_list(zd)

    ap_xs_list = BCLIB.get_ap_xs_info(zd)

    for p in range(1, int(fcfg['repeat']) + 1):
        for wgs_name in wgs_list:
            desc = "Update %03d wgs=%s" % (p, wgs_name)
            for ap_xs0 in ap_xs_list:
                ap_xs1 = BCLIB.update_ap_xs_info_ch(zd, ap_xs0, desc, wgs_name)
                time.sleep(fcfg['sleep'])
        #wgs_name = 'Default'
        #desc = "Update %03d wgs=%s" % (p, wgs_name)
        #for ap_xs0 in ap_xs_list:
        #    ap_xs1 = BCLIB.update_ap_xs_info(zd, ap_xs0, desc, wgs_name)
        #    time.sleep(fcfg['sleep'])
    return 0

def do_cleanup(zd, debug = False):
    halt(debug)
    BCLIB.remove_wlan_config(zd)

# Usage:
#
#   tea.py contrib.wlandemo.WGconfig_ref repeat = 1 do_cleanup = False
#   tea.pgetL3AclRuleList(zd, L3acl_conf)y bugs.bug6099 repeat=50 debug=True
#   tea.py bugs.bug6099 ip_addr=192.168.2.2
#
def main(**kwargs):
    fcfg = dict(debug = False, repeat = 1, sleep = 5, do_config = True, do_cleanup = False)
    fcfg.update(kwargs)

    sm = SeleniumManager()
    fcfg.update({'selenium_mgr': sm})

    zd = do_cfg(**fcfg)
    try:
        #do_test(zd,**kwargs)
    #while True:
        #do_station1_test(**kwargs)
        #do_station2_test(**kwargs)
        #do_sta1_batch_psk_test(**kwargs)
        do_sta1_zeroit_test(zd, **kwargs)
        if fcfg['do_cleanup']:
            do_cleanup(zd, debug = fcfg['debug'])

    except Exception, ex:
        sm.shutdown()
        return ('FAIL', mytb, {'error': ex.message})

    sm.shutdown()
    return ('PASS', mytb)

