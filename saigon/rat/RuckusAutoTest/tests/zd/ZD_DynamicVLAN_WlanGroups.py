import os
import re
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils

class ZD_DynamicVLAN_WlanGroups(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station':'ip address of target station',
                           'active_ap':'mac address (NN:NN:NN:NN:NN:NN)of target ap which client will associate to',
                           'wlan_cfg':'dictionary of association parameters',
                           'wgs_cfg':'dictionary of wlan groups parameters',
                           'radio_mode':'wireless mode on client. Valid values are: n, na',
                           'eap_user':'dictionary of eap user parameters',
                           'auth_srv':'dictionary of authentication server parameters',
                           'test_case':'indicate eap user connect to some wlan or different wlan'}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgGetTargetStation()
        self._findActiveAP()
        self._assign_Default_Wlangroup_to_AP()
        self._cfgRemoveZDWlanGroupsAndWlan()
        

    def test(self):
        self._cfg_wlanForAP()
 
        self._isolateAPWithWlanGroups()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testWlanIsUp()
        if self.errmsg: return ("FAIL", self.errmsg)
        for eap_user in self.eap_user:
            self._configClientToAssocWlanWithUser(eap_user)
            if self.errmsg: return ("FAIL", self.errmsg)
            self._get_clientWifiAddress()
            if self.errmsg: return ("FAIL", self.errmsg)
            self._testIfVlanCheckClientAndDestAtSameSubnet(eap_user)
            if self.errmsg: return ("FAIL", self.errmsg)
            self._testClientCanReachGateway(eap_user)
            if self.errmsg: return ("FAIL", self.errmsg)
            self._testVerifyStationInfoOnZD(eap_user)
            if self.errmsg: return ("FAIL", self.errmsg)
            self._cfgGetTargetStation()    

        msg = "ActiveAP[%s %s %s %s] can support Dynamic VLAN with %s %s" \
            % (self.conf['active_ap'], self.ap_xstatus['model'],
                self.active_ap.base_mac_addr, self.active_ap.ip_addr,
                self.wlan_cfg1['wpa_ver'], self.wlan_cfg1['encryption'])
        return ('PASS', msg)

    def cleanup(self):
        self._assign_Default_Wlangroup_to_AP()
        self.zd.remove_all_wlan_group()
        self.zd.remove_all_wlan()
        
#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3,
                          radio_mode = '',
                          test_case = 'same wlan')
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        if not self.conf.has_key('wlan_cfg'):
            self.wlan_cfg = tmethod8.get_default_wlan_cfg(self.conf['vlan_id'])
        if not self.conf.has_key('wgs_cfg'):
            self.conf['wgs_cfg'] = tmethod8.get_default_wlan_groups_cfg(self.conf['radio_mode'])

        if self.conf.has_key('vlan_id'):
            self.wlan_cfg['vlan_id'] = self.conf['vlan_id']
        if self.conf.has_key('enable_tunnel'):
            self.wlan_cfg['do_tunnel'] = self.conf['enable_tunnel']
        else:
            self.wlan_cfg['do_tunnel'] = False
        self.ssid = self.wlan_cfg['ssid']
        self.wlan_cfg['dvlan'] = True if not self.wlan_cfg.has_key('dvlan') else self.wlan_cfg['dvlan']
        self.wlan_cfg1 = self.wlan_cfg.copy()
        self.wlan_cfg2 = self.wlan_cfg.copy()
        self.wlan_cfg1['username'] = self.wlan_cfg1['password'] = self.conf['eap_user']['user1']['username']
        self.wlan_cfg2['username'] = self.wlan_cfg2['password'] = self.conf['eap_user']['user2']['username']
        self.gateway_ip1 = self.conf['eap_user']['user1']['dest_ip']
        self.gateway_ip2 = self.conf['eap_user']['user2']['dest_ip']
        if self.conf['test_case'] == 'same wlan':
            self.wlan_cfg1['ssid'] = self.wlan_cfg2['ssid'] = tmethod.touch_ssid(self.ssid)
            self.wlan_list = [ self.wlan_cfg1]
        else:
            self.wlan_cfg1['ssid'] = tmethod.touch_ssid(self.ssid)
            self.wlan_cfg2['ssid'] = tmethod.touch_ssid(self.ssid)
            self.wlan_list = [ self.wlan_cfg1, self.wlan_cfg2 ]
        self.user1 = self.conf['eap_user']['user1']
        self.user2 = self.conf['eap_user']['user2']
        self.eap_user = [ self.user1, self.user2 ]
        self.auth_srv = self.conf['auth_srv']
        self.wgs_cfg = self.conf['wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.radio = {'defined': self.conf['radio_mode']}

        if self.conf.has_key('connection_mode'):
            self.connection_mode = self.conf['connection_mode']
        else:
            self.connection_mode = ""

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.conf['check_status_timeout']
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])
        

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        #logging.info("Remove all Wlan Groups on the Zone Director.")
        #lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        #logging.info("Remove all WLAN on the Zone Director.")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _findActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = None
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in testbed." % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.base_mac_addr.lower()
            
    def _assign_Default_Wlangroup_to_AP(self):
        # assign default wlangroup to active ap.
        lib.zd.ap.assign_to_default_wlan_group(self.zd, self.active_ap_mac)

#
# test()
#
    def _cfg_wlanForAP(self):
        if self.auth_srv:
            logging.info("Create an authentication server on the ZoneDirector")
            self.zd.create_radius_server(self.auth_srv['ras_addr'],
                                      self.auth_srv['ras_port'],
                                      self.auth_srv['ras_secret'])

        for wlan_cfg in self.wlan_list:
            lib.zd.wlan.create_wlan(self.zd, wlan_cfg)
            lib.zd.wgs.uncheck_default_wlan_member(self.zd,
                                               wlan_cfg['ssid'])

    def _testWlanIsUp(self):
        for wlan_cfg in self.wlan_list:
            self.errmsg = tmethod8.check_wlan_on_ap_is_up(self.active_ap,
                                                      wlan_cfg['ssid'],
                                                      self.conf['check_wlan_timeout'])

    def _isolateAPWithWlanGroups(self):
        (self.wgs_apinfo, self.ap_xstatus) = \
            tmethod8.assign_1ap_to_exist_wlan_with_wlan_groups(self.zd,
                                                         self.active_ap_mac,
                                                         self.wgs_cfg)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')

    # client is connected if not self.errmsg 
    def _configClientToAssocWlanWithUser(self, eap_user):
        wlan_cfg = self.wlan_cfg1 if eap_user == self.user1 else self.wlan_cfg2
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station,
                                                    wlan_cfg,
                                                    self.conf['check_status_timeout'])

    def _get_clientWifiAddress(self):
        (isOK, ip_addr, mac_addr) = tmethod.renew_wifi_ip_address(self.target_station,
                                                                self.conf['check_status_timeout'])
        if not isOK:
            self.errmsg = mac_addr
        else:
            self.wifi = dict(ip_addr = ip_addr, mac_addr = mac_addr)
 
    def _testIfVlanCheckClientAndDestAtSameSubnet(self, eap_user):
        # Check if the wireless IP address of the station belongs to the subnet of the parameter 'ip'.
        self.errmsg = ""
        if eap_user == self.user1:
            self.expected_subnet = self.user1['expected_subnet'].split("/")[0]
            self.expected_subnet_mask = self.user1['expected_subnet'].split("/")[1]
        else:
            self.expected_subnet = self.user2['expected_subnet'].split("/")[0]
            self.expected_subnet_mask = self.user2['expected_subnet'].split("/")[1]
        if self.expected_subnet:
            sta_wifi_subnet = utils.get_network_address(self.wifi['ip_addr'], self.expected_subnet_mask)
            if sta_wifi_subnet != self.expected_subnet:
                self.errmsg = "The wireless IP address '%s' of the target station was not as expected '%s'" % \
                              (self.wifi['ip_addr'], self.expected_subnet)
        elif self.conf.has_key('vlan_id'):
            sta_wifi_subnet = utils.get_network_address(self.wifi['ip_addr'], self.expected_subnet_mask)
            expected_subnet = utils.get_network_address(self.dest_ip, self.expected_subnet_mask)
            if sta_wifi_subnet != expected_subnet:
                self.errmsg = "The wireless IP address '%s' of target station %s has different subnet with '%s'" % \
                              (self.wifi['ip_addr'], self.target_station.get_ip_addr(), self.dest_ip)
 
    def _testClientCanReachGateway(self, eap_user):
        gateway_ip = self.gateway_ip1 if eap_user == self.user1 else self.gateway_ip2
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                           gateway_ip,
                                                           ping_timeout_ms = self.conf['ping_timeout'] * 1000) 
                
    def _getActiveClient(self):
        tmethod8.pause_test_for(3, 'Wait for ZD to update the client info')
        self.actclient = lib.zd.cac.get_status_by_mac(self.zd, self.wifi['mac_addr'].lower())
        self.radio['client'] = self.actclient['radio']
        m = re.search(r'802.11([^\s]+)', self.actclient['radio'])
        if m:
            self.radio['client_mode'] = m.group(1)
        
    def _testVerifyStationInfoOnZD(self, eap_user):
        logging.info("Verify information of the target station shown on the ZoneDirector")
        if eap_user == self.user1:
            wlan_cfg = self.wlan_cfg1 
            expected_ip = self.user1['username']
            expected_vlan = self.user1['expected_vlan']
            expected_wlan = self.wlan_cfg1['ssid']
        else:
            wlan_cfg = self.wlan_cfg2
            expected_ip = self.user2['username']
            expected_vlan = self.user2['expected_vlan']
            expected_wlan = self.wlan_cfg2['ssid']
        # Define the expected radio mode
        if self.conf['radio_mode'] == 'g':
            expected_radio_mode = r'802.11b/g'
        elif self.conf['radio_mode'] == 'n':
            if wlan_cfg['encryption'] in ['TKIP', 'WEP-64', 'WEP-128']:# TKIP,WEP-64, WEP-128 encryption doesn't support HT rate
                expected_radio_mode = r'802.11b/g'
            #Chico, 2015-7-14, station TKIP can't be high speed
            elif wlan_cfg['encryption'].lower() == 'auto':
                if wlan_cfg['sta_encryption'].lower() == 'tkip':
                    expected_radio_mode = r'802.11b/g'
                else:
                    expected_radio_mode = r'802.11g/n'
            #Chico, 2015-7-14, station TKIP can't be high speed
            else:
                expected_radio_mode = r'802.11g/n'
        elif self.conf['radio_mode'] == 'a':
            expected_radio_mode = r'802.11a'
        elif self.conf['radio_mode'] == 'na':
            if wlan_cfg['encryption'] in ['TKIP', 'WEP-64', 'WEP-128']:# TKIP,WEP-64, WEP-128 encryption doesn't support HT rate
                expected_radio_mode = r'802.11a'
            #Chico, 2015-7-14, station TKIP can't be high speed
            elif wlan_cfg['encryption'].lower() == 'auto':
                if wlan_cfg['sta_encryption'].lower() == 'tkip':
                    expected_radio_mode = r'802.11a'
                else:
                    expected_radio_mode = r'802.11a/n'
            #Chico, 2015-7-14, station TKIP can't be high speed
            else:
                expected_radio_mode = r'802.11a/n'
        else:
            expected_radio_mode = None
        
        #@An Nguyen (29 Sep, 09): define the expected_ap_info to fix the issue about the AP info in the Active Client table
        if self.wgs_cfg.get('description'):
            expeceted_ap_info = self.wgs_cfg['description']
        else:
            expeceted_ap_info = self.active_ap.base_mac_addr

        exp_client_info = {"ip": expected_ip,
                           "status": "Authorized",
                           "wlan": expected_wlan,
                           "vlan": expected_vlan,
                           "radio": expected_radio_mode,
                           "apmac": expeceted_ap_info}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd,
                                                                           self.wifi['mac_addr'], exp_client_info,
                                                                           self.conf['check_status_timeout'])



#
# cleanup()
#

