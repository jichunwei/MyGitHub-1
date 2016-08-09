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

class ZD_EncryptionTypes_WlanGroups(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip':'IP address to ping',
                           'target_station':'ip address of target station',
                           'active_ap':'mac address (NN:NN:NN:NN:NN:NN)of target ap which client will associate to',
                           'wlan_cfg':'dictionary of association parameters',
                           'wgs_cfg':'dictionary of wlan groups parameters',
                           'radio_mode':'wireless mode on client. Valid values are: ng, na'}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgGetTargetStation()
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._findActiveAP()

    def test(self):
        self._cfg_wlanForAP()
        self._isolateAPWithWlanGroups()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testWlanIsUp()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._configClientToAssocWlan()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._get_clientWifiAddress()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testIfVlanCheckClientAndDestAtSameSubnet()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testClientCanReachGateway()
        if self.errmsg: return ("FAIL", self.errmsg)
        #self._getActiveClient()
        #self._getWlanGroupsStatus()
        self._testClientRadioMatchZD()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testVerifyStationInfoOnZD()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testVerifyStationInfoOnAP()
        if self.errmsg: return ("FAIL", self.errmsg)

        msg = "ActiveAP[%s %s %s %s] can support Auth[%s] Encryption[%s]" \
            % (self.conf['active_ap'], self.ap_xstatus['model'],
                self.active_ap.get_base_mac(), self.active_ap.ip_addr,
                self.wlan_cfg['auth'], self.wlan_cfg['encryption'])
        return ('PASS', msg)

    def cleanup(self):
        #self._cfgRemoveZDWlanGroupsAndWlan()
        pass

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3,
                          radio_mode = '')
        self.conf.update(conf)
        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg(self.conf['vlan_id'])
        if not self.conf.has_key('wgs_cfg'):
            self.conf['wgs_cfg'] = tmethod8.get_default_wlan_groups_cfg(self.conf['radio_mode'])
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid(self.conf['wlan_cfg']['ssid']) 
        self.wlan_cfg = self.conf['wlan_cfg']
        self.wgs_cfg = self.conf['wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.gateway_ip = self.conf['dest_ip']
        self.radio = {'defined': self.conf['radio_mode']}
        tmp_list = self.conf['dest_ip'].split("/")
        self.test_ip_addr = tmp_list[0]
        if len(tmp_list) == 2:
            self.expected_subnet_mask = tmp_list[1]
        else:
            self.expected_subnet_mask = ""

        if self.conf.has_key('vlan_id'):
            self.wlan_cfg['vlan_id'] = self.conf['vlan_id']

        if self.conf.has_key('connection_mode'):
            self.connection_mode = self.conf['connection_mode']
        else:
            self.connection_mode = ""

        if self.conf.has_key('enable_tunnel'):
            self.wlan_cfg['do_tunnel'] = self.conf['enable_tunnel']
        else:
            self.wlan_cfg['do_tunnel'] = False

        if self.conf.has_key('expected_subnet'):
            l = self.conf['expected_subnet'].split("/")
            self.expected_subnet = l[0]
            if len(l) == 2:
                self.expected_subnet_mask = l[1]
            else:
                self.expected_subnet_mask = ""
        else:
            self.expected_subnet = ""
            self.expected_subnet_mask = ""

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
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)
        #self.zd.remove_all_cfg()

    def _findActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = None
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in testbed." % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.base_mac_addr.lower()

#
# test()
#
    def _cfg_wlanForAP(self):
        if self.wlan_cfg['auth'] == "EAP":
            logging.info("Create an authentication server on the ZoneDirector")
            if self.wlan_cfg['use_radius']:
                self.zd.create_radius_server(self.wlan_cfg['ras_addr'],
                                          self.wlan_cfg['ras_port'],
                                          self.wlan_cfg['ras_secret'])
            else:
                logging.info("Create a user on the ZoneDirector")
                self.zd.create_user(self.wlan_cfg['username'],
                                    self.wlan_cfg['password'])

        self.zd.cfg_wlan(self.wlan_cfg)
        #tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
        # make sure wlan_cfg['ssid'] is not belong to default wlanGroups
        # so we can isolate an AP to wlan_cfg['ssid'] -- to make 1Wlan 1AP possible
        lib.zd.wgs.uncheck_default_wlan_member(self.zd,
                                           self.wlan_cfg['ssid'])

    def _testWlanIsUp(self):
        self.errmsg = tmethod8.check_wlan_on_ap_is_up(self.active_ap,
                                                  self.wlan_cfg['ssid'],
                                                  self.conf['check_wlan_timeout'])

    def _isolateAPWithWlanGroups(self):
        (self.wgs_info, self.wgs_apinfo, self.ap_xstatus) = \
            tmethod8.assign_1ap_to_1wlan_with_wlan_groups(self.zd,
                                                         self.active_ap_mac,
                                                         self.wlan_cfg,
                                                         self.wgs_cfg)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')


    # client is connected if not self.errmsg 
    def _configClientToAssocWlan(self):
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station,
                                                    self.wlan_cfg,
                                                    self.conf['check_status_timeout'])

    def _get_clientWifiAddress(self):
        (isOK, ip_addr, mac_addr) = tmethod.renew_wifi_ip_address(self.target_station,
                                                                self.conf['check_status_timeout'])
        if not isOK:
            self.errmsg = mac_addr
        else:
            self.wifi = dict(ip_addr = ip_addr, mac_addr = mac_addr)
 
    def _testIfVlanCheckClientAndDestAtSameSubnet(self):
        # Check if the wireless IP address of the station belongs to the subnet of the parameter 'ip'.
        self.errmsg = ""
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
 
    def _testClientCanReachGateway(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                           self.gateway_ip,
                                                           ping_timeout_ms = self.conf['ping_timeout'] * 1000) 

    def _testClientRadioMatchZD(self):
        self._getActiveClient()
        self._getWlanGroupsStatus()
        if int(self.actclient['channel']) > 20:
            ptn_channel = r'%s\s+\(([0-9an/-]+)\)' % self.actclient['channel']
        else:
            ptn_channel = r'%s\s+\(([0-9bgn/-]+)\)' % self.actclient['channel']
        m = re.search(ptn_channel, self.ap_xstatus['channel'])
        if not m:
            self.errmsg = "Client:[%s %s] channel[%s] not match ZD[%s]" \
                        % (self.wifi['ip_addr'], self.wifi['mac_addr'],
                            self.actclient['channel'], self.ap_xstatus['channel'])
            #Updated by cwang@20130607 return direct while error happen
            return

        msg = "Client[%s %s] channel[%s] match ZD[%s]" \
            % (self.wifi['ip_addr'], self.wifi['mac_addr'],
                self.actclient['channel'], self.ap_xstatus['channel'])
        logging.info(msg)
        self.radio['zd_radio'] = zd_radio = m.group(1)
        if self.radio['defined'].find('a') >= 0:
            if re.search(r'11a/n', zd_radio) and re.search(r'a(|/n)', self.radio['client_mode']):
                pass
            else:
                self.errmsg = "Client[%s %s] radio[%s] not match ZD[%s]" \
                            % (self.wifi['ip_addr'], self.wifi['mac_addr'],
                                self.radio['client'], zd_radio)
        elif self.radio['defined'] == 'n':
            if re.search(r'11b/g/n', zd_radio) != None and re.search(r'[bg]/[gn]', self.radio['client_mode']) != None:
                pass
            else:
                self.errmsg = "Client[%s %s] radio[%s] not match ZD[%s]" \
                            % (self.wifi['ip_addr'], self.wifi['mac_addr'],
                                self.radio['client'], zd_radio)
        else: 
            if re.search(r'11b/g', zd_radio) and re.search(r'b/g', self.radio['client_mode']):
                pass
            else:
                self.errmsg = "Client[%s %s] radio[%s] not match ZD[%s]" \
                            % (self.wifi['ip_addr'], self.wifi['mac_addr'],
                                self.radio['client'], zd_radio)
                
    def _getActiveClient(self):
        tmethod8.pause_test_for(3, 'Wait for ZD to update the client info')
        self.actclient = lib.zd.cac.get_status_by_mac(self.zd, self.wifi['mac_addr'].lower())
        self.radio['client'] = self.actclient['radio']
        m = re.search(r'802.11([^\s]+)', self.actclient['radio'])
        if m:
            self.radio['client_mode'] = m.group(1)

    def _getWlanGroupsStatus(self):
        self.ap_xstatus = lib.zd.wgs.get_status_ex_by_ap_mac_addr(self.zd,
                                                           self.wgs_cfg['name'],
                                                           self.active_ap.base_mac_addr.lower())
        
    def _testVerifyStationInfoOnAP(self):
        self.errmsg = tmethod.verify_station_info_on_ap(self.active_ap, self.wifi['mac_addr'], self.wlan_cfg['ssid'],
                                            self.client_info_on_zd['channel'])
        
    def _testVerifyStationInfoOnZD(self):
        logging.info("Verify information of the target station shown on the ZoneDirector")
        # Define the expected radio mode
        if self.conf['radio_mode'] == 'g':
            expected_radio_mode = r'802.11b/g'
        elif self.conf['radio_mode'] == 'n':
            if self.wlan_cfg['encryption'] in ['TKIP', 'WEP-64', 'WEP-128']:# TKIP,WEP-64, WEP-128 encryption doesn't support HT rate
                expected_radio_mode = r'802.11b/g'
            else:
                expected_radio_mode = r'802.11g/n'
        elif self.conf['radio_mode'] == 'a':
            expected_radio_mode = r'802.11a'
        elif self.conf['radio_mode'] == 'na':
            if self.wlan_cfg['encryption'] in ['TKIP', 'WEP-64', 'WEP-128']:# TKIP,WEP-64, WEP-128 encryption doesn't support HT rate
                expected_radio_mode = r'802.11a'
            else:
                expected_radio_mode = r'802.11a/n'
        else:
            expected_radio_mode = None
            
        if self.wlan_cfg['auth'] == 'EAP':
            expected_ip = self.wlan_cfg['username']
        else:
            expected_ip = self.wifi['ip_addr']
        #@An Nguyen (29 Sep, 09): define the expected_ap_info to fix the issue about the AP info in the Active Client table
        if self.wgs_cfg.get('description'):
            expeceted_ap_info = self.wgs_cfg['description']
        else:
            expeceted_ap_info = self.active_ap.base_mac_addr

        exp_client_info = {"ip": expected_ip, "status": "Authorized", "wlan": self.wlan_cfg['ssid'],
                           "radio": expected_radio_mode, "apmac": expeceted_ap_info}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.testbed.components["ZoneDirector"],
                                                                   self.wifi['mac_addr'], exp_client_info,
                                                                   self.conf['check_status_timeout'])



#
# cleanup()
#

