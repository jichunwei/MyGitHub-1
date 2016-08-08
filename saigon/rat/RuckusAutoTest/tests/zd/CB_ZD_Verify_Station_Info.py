"""
Description: This script is used to verify the information of the station shown on the ZD.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Verify_Station_Info(Test):
    required_components = ['ZoneDirector', 'AP']
    parameters_description = {}
    
    def config(self, conf):
        self._init_test_parameters(conf)
        self._retrieve_carribag()

    def test(self):                        
        self._test_verify_station_info_on_zd()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        self.passmsg = 'Verify station information [%s] on zd successfully' % self.client_info_on_zd      
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        #add by cwang#20110421, chk_empty parameter which is used for checking target station isn't shown.
        self.conf = {'check_status_timeout': 120,
                     'username': '', 
                     'chk_empty': False, 
                     'radio_mode': None,
                     'status': 'Authorized',
                     'wlan_cfg': {},
                     'wlan_ssid': '',
                     'sta_tag': '',
                     'ap_tag': '',
                     'use_guestpass_auth': True,
                     'guest_name': '',
                     'expected_station_info': '',
                     'expected_network': ''
                     }
        self.conf.update(conf)
        
        if self.conf['wlan_cfg']:
            self.wlan_cfg = self.conf['wlan_cfg']
        elif self.conf['wlan_ssid']: # An Nguyen, Apr 2012, updated to get wlan configuration from carrierbag
            self.wlan_cfg = self.carrierbag[self.conf['wlan_ssid']]
            
        self.radio_mode = self.conf['radio_mode']
        
        self.zd = self.testbed.components["ZoneDirector"]   
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        if self.conf['sta_tag']:
            self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
            self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        
        else:
            self.sta_wifi_mac_addr = self.carrierbag['sta_wifi_mac_addr']
            self.sta_wifi_ip_addr = self.carrierbag['sta_wifi_ip_addr']
        
        if self.conf['ap_tag']:
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        
        elif self.carrierbag.has_key('active_ap'):
            self.active_ap = self.carrierbag['active_ap']['AP1']
        
        else:
            #Don't check the mac address of AP
            self.active_ap = None
    
    def _get_expected_client_info_base_on_wlan_cfg(self):
        """
        """
        if self.carrierbag.get(self.conf['sta_tag']) and self.carrierbag[self.conf['sta_tag']].get('expected_station_info'):
            exp_client_info = self.carrierbag[self.conf['sta_tag']]['expected_station_info']
            return exp_client_info
        
        if self.radio_mode == 'g' or self.radio_mode == 'bg' or self.wlan_cfg['encryption'].upper() in ['TKIP', 'WEP-64', 'WEP-128','WEP64','WEP128']:
            expected_radio_mode = ['802.11b/g', '802.11a']
            
        else:
            expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
        
        expected_ip = self.sta_wifi_ip_addr
        if self.wlan_cfg.get('auth') == 'EAP':
            expected_ip = self.wlan_cfg['username']
            expected_ip = [expected_ip, expected_ip+'/'+self.sta_wifi_ip_addr]
        # Modified by Liang Aihua on 2014-5-27 need to be optimized for different mac pattern
        elif self.wlan_cfg.get('auth') == 'mac':
            station_mac = self.sta_wifi_mac_addr.split(":")
            expected_ip = [self.sta_wifi_mac_addr,
                           self.sta_wifi_mac_addr.upper(),
                           '-'.join(station_mac),
                           ''.join(station_mac),
                           '-'.join(station_mac).upper(),
                           ''.join(station_mac).upper(),
                           self.sta_wifi_mac_addr+'/'+self.sta_wifi_ip_addr,
                           self.sta_wifi_mac_addr.upper()+'/'+self.sta_wifi_ip_addr,
                           '-'.join(station_mac)+'/'+self.sta_wifi_ip_addr,
                           ''.join(station_mac)+'/'+self.sta_wifi_ip_addr,
                           '-'.join(station_mac).upper()+'/'+self.sta_wifi_ip_addr,
                           ''.join(station_mac).upper()+'/'+self.sta_wifi_ip_addr]

        elif self.wlan_cfg.get('web_auth') or self.wlan_cfg.get('do_webauth'):
            if self.conf['status'] == 'Authorized':
                expected_ip = self.conf['username'] if self.conf['username'] else self.wlan_cfg['username']
                expected_ip = [expected_ip, expected_ip+'/'+self.sta_wifi_ip_addr]
        elif self.wlan_cfg.get('type') == 'guest' and self.conf['status'] == 'Authorized':
            if self.conf['use_guestpass_auth']:
                expected_ip = self.conf['guest_name']                
            else:
                expected_ip = 'guest'
            expected_ip = [expected_ip, expected_ip+'/'+self.sta_wifi_ip_addr]
        elif self.wlan_cfg.get('type') == 'hotspot' and self.conf['status'] == 'Authorized':
            expected_ip = self.conf['username']           
            expected_ip = [expected_ip, expected_ip+'/'+self.sta_wifi_ip_addr]

        exp_client_info = {"status": self.conf['status'], 
                           "wlan": self.wlan_cfg['ssid'],
                           "radio": expected_radio_mode,
                           "ip": expected_ip
                           }
        #@author:yuyanan @since:2014-8-6 zf-8842 add ap description process when ap description exist
        if self.active_ap != None:
            ap_info = self.zd._get_ap_info(self.active_ap.base_mac_addr)
            ap_description = ap_info.get('description')
            if ap_description: 
                exp_client_info['apmac'] = ap_description
            else:
                exp_client_info['apmac'] = self.active_ap.base_mac_addr
        
        return exp_client_info
    
    def _test_verify_station_info_on_zd(self):
        """
        """
        logging.info("Verify information of the target station shown on the Zone Director")
        # An Nguyen@Apr2012 added step to support to verify the expected info from test case configuration
        if self.conf.get('expected_station_info'):
            exp_client_info = self.conf['expected_station_info']
        else:
            exp_client_info = self._get_expected_client_info_base_on_wlan_cfg()
            
        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, 
                                                                              self.sta_wifi_mac_addr, 
                                                                              exp_client_info, 
                                                                              self.conf['check_status_timeout'])
        if 'chk_empty' in self.conf:
            if self.conf['chk_empty']:
                if self.errmsg and self.errmsg.find("Zone Director didn't show any information") >= 0:
                    self.errmsg = ''
                else:
                    self.errmsg = 'The client info should not be shown in zd'
        
        if self.conf.get('expected_network'):
            self._verify_station_wifi_ip_network()
        
    def _update_carrier_bag(self):
        self.carrierbag['client_info_on_zd'] = self.client_info_on_zd
    
    def _verify_station_wifi_ip_network(self):
        """
        Verify if the station got the IP address from expected network. Use for tunnel, vlan testing.
        Added by An Nguyen, an.nguyen@ruckuswireless.com
        @since: Mar 2012
        """
        ip_list = self.conf['expected_network'].split("/")
        expected_ip_addr = ip_list[0]
        if len(ip_list) == 2:
            expected_mask = ip_list[1]
        else:
            expected_mask = ""
                
        logging.info("Make sure that the client has got an IP address assigned to the network %s" 
                     % self.conf['expected_network'])
        if utils.get_network_address(self.sta_wifi_ip_addr, expected_mask) \
        != utils.get_network_address(expected_ip_addr, expected_mask):
            msg = "The IP address %s was not in the same subnet as %s." % (self.sta_wifi_ip_addr, expected_ip_addr)
            msg += " Traffic sent from the wireless station was not tagged properly"
            self.errmsg = msg