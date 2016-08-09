# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Nov 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
      'sta_tag': 'Station tag',
      'ap_tag': 'AP tag',
      'radio_mode': 'Station radio mode',
      'wlan_cfg': 'Wlan configuration',
      'username': "Username for login, which is for webauth and hotspot wlan, if empty will use wlan_cfg['username']",
      'status': 'Station expected status, authorized and unauthorized',
      'check_status_timeout': 'Timeout to verify station information in ZD',
      'chk_empty':'Check empty information in ZD',
      'chk_radio':'Check radio mode of station in ZD',
      'use_guestpass_auth': 'It is for guest access wlan, whether use guest pass authentication',
      'guest_name': 'Guest name',
      'verify_sta_info_ap': 'Verify station information in AP',
      'verify_sta_tunnel_mode': 'Verify station tunnel mode or not',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Verify station information on ZD
        - [Optional] Verify station information on AP, default is True
        - [Optional] Verify station tunnel mode, default is True
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If station information is correct on ZD and AP, station tunnel mode is correct. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Verify_Station_Info_On_ZD_AP(Test):
    required_components = ['Station']
    parameters_description = {'sta_tag': 'Station tag',
                              'ap_tag': 'AP tag',
                              'radio_mode': 'Station radio mode',
                              'wlan_cfg': 'Wlan configuration',
                              'username': "Username for login, which is for webauth and hotspot wlan, if empty will use wlan_cfg['username']",
                              'status': 'Station expected status, authorized and unauthorized',
                              'check_status_timeout': 'Timeout to verify station information in ZD',
                              'chk_empty':'Check empty information in ZD',
                              'chk_radio':'Check radio mode of station in ZD',
                              'use_guestpass_auth': 'It is for guest access wlan, whether use guest pass authentication',
                              'guest_name': 'Guest name',
                              'vlan': 'Station vlan information on ZD',
                              'verify_sta_info_ap': 'Verify station information in AP',
                              'verify_sta_tunnel_mode': 'Verify station tunnel mode or not',
                              }    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self._verify_station_info_on_zd(self.conf['status'])
            if self.conf['verify_sta_info_ap'] and not self.errmsg: 
                self._verify_station_info_on_ap()
            if self.conf['verify_sta_tunnel_mode'] and not self.errmsg:
                self._verify_station_in_tunnel_mode()
                
        except Exception, ex:
            self.errmsg = "Exception: %s" % ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "The steps %s works correctly." % self.steps
            return  self.returnResult('PASS', self.passmsg)                     
    
    def cleanup(self):
        self._update_carribag()
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'sta_tag': 'sta_1',
                     'ap_tag': '',
                     'radio_mode': '',
                     'wlan_cfg': {},
                     'username': "", # ras.local.user
                     'status': 'authorized',
                     'check_status_timeout': 120,
                     'chk_empty':False,
                     'chk_radio':True,
                     'use_guestpass_auth': False,
                     'guest_name': '',
                     'vlan': '',
                     'verify_sta_info_ap': True,
                     'verify_sta_tunnel_mode': False,}
        
        self.conf.update(conf)
        
        #For radio mode is bg, need to set it is as g.
        self.radio_mode = self.conf['radio_mode']
        if self.radio_mode == 'bg':
            self.radio_mode = 'g'
        
        #Get ZD, AP and station components.
        self.zd = self.testbed.components["ZoneDirector"]
        
        self.errmsg = ''
        self.passmsg = ''
        self.steps = []        
    
    def _retrieve_carribag(self):        
        sta_dict = self.carrierbag.get(self.conf['sta_tag'])
        if sta_dict:
            self.target_station = sta_dict['sta_ins']
            self.sta_wifi_mac_addr = sta_dict['wifi_mac_addr']
            self.sta_wifi_ip_addr = sta_dict['wifi_ip_addr']
            self.sta_wifi_ipv6_addr_list = sta_dict.get('wifi_ipv6_addr_list')
        else:
            raise Exception("No station provided.")
        
        ap_dict = self.carrierbag.get(self.conf['ap_tag'])
        if ap_dict:
            self.active_ap = ap_dict['ap_ins']
            self.ap_mac_addr = self.active_ap.get_base_mac().lower()
        else:
            if self.conf.get('verify_sta_info_ap') == True:
                raise Exception("No active ap provided")
            else:
                self.active_ap = None
                self.ap_mac_addr = None
            
                
    def _update_carribag(self):
        pass
    
    #-----------------Main validation steps method -------------------
    def _verify_station_info_on_zd(self, status = 'Authorized'):
        '''
        Verify station information on ZD GUI.
        '''
        errmsg = None
        passmsg = None
        
        try:
            wlan_cfg = self.conf['wlan_cfg']
            
            if wlan_cfg['encryption'].upper() == 'AUTO':
                encryption = wlan_cfg['sta_encryption']
            else:
                encryption = wlan_cfg['encryption']
            
            if self.radio_mode == 'g' or encryption.upper() in ['TKIP', 'WEP-64', 'WEP-128', 'WEP64', 'WEP128']:
                expected_radio_mode = ['802.11b/g', '802.11a']
            else:
                expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
            
            #@author: Liang Aihua,@since: 2015-3-11,@change: to fix bug zf-12242  
            #*************
            expected_ip = [self.sta_wifi_ip_addr]
            if self.sta_wifi_ipv6_addr_list:
                for wifi_ipv6_addr in self.sta_wifi_ipv6_addr_list:
                    expected_ip.append('%s/%s' % (self.sta_wifi_ip_addr, wifi_ipv6_addr))
                    expected_ip.append('%s' % wifi_ipv6_addr)
            
            if self.conf['status'].lower() == 'authorized':
                if wlan_cfg.get('auth')== 'mac' or (wlan_cfg.get('type') == 'hotspot' and self.conf.get('username') == 'mac.bypass'):
                    import itertools
                    mac_addr = self.sta_wifi_mac_addr.split(':')
                    mac_address = "".join(itertools.chain(mac_addr))
                    if not wlan_cfg.get('mac_addr_format'):
                        username = mac_address.lower()
                    elif wlan_cfg.get('mac_addr_format') == 'aabbccddeeff':
                        username = mac_address.lower()
                    elif wlan_cfg.get('mac_addr_format') == 'AABBCCDDEEFF':
                        username = mac_address.upper()
                    elif self.wlan_cfg.get('mac_addr_format') == 'aa:bb:cc:dd:ee:ff':
                        username = self.sta_wifi_mac_addr.lower()
                    elif wlan_cfg.get('mac_addr_format') == 'AA:BB:CC:DD:EE:FF':
                        username = self.sta_wifi_mac_addr.upper()
                    elif wlan_cfg.get('mac_addr_format') == 'aa-bb-cc-dd-ee-ff':
                        username = self.sta_wifi_mac_addr.lower().replace(':', '-')
                    elif wlan_cfg.get('mac_addr_format') == 'AA-BB-CC-DD-EE-FF':
                        username = self.sta_wifi_mac_addr.upper().replace(':', '-')
                
                elif wlan_cfg.get('type') in ['guest', 'guest-access']:
                    if self.conf.get('use_guestpass_auth'):
                        username = self.conf['guest_name']
                    else:
                        username = 'guest'
                elif wlan_cfg.get('web_auth') or wlan_cfg.get('do_webauth'):
                    username = self.conf['username'] if self.conf['username'] else wlan_cfg['username']
                    
                elif wlan_cfg.get('auth') == 'EAP':
                    username = wlan_cfg['username']
                    
                else:
                    username = self.conf.get('username')
            
                if username:
                    for index,item in enumerate(expected_ip):
                        expected_ip[index] = username + '/' + item
                    expected_ip.append(username)
            #**********************************************

            exp_client_info = {"ip": expected_ip,
                               "status": status,
                               "wlan": wlan_cfg['ssid'],
                               "radio": expected_radio_mode,
                               "apmac": self.ap_mac_addr,}
            
            if self.conf.get('vlan'):
                exp_client_info['vlan'] = self.conf['vlan']
            
            #added by cwang, skip checking radio status.
            if not self.conf['chk_radio']:
                exp_client_info.pop('radio')
                
            errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd,
                                                                             self.sta_wifi_mac_addr,
                                                                             exp_client_info,
                                                                             self.conf['check_status_timeout'])
            
            logging.info('Client information in ZD is %s' % (self.client_info_on_zd))
            
            if self.conf['chk_empty']:
                if errmsg and errmsg.find("Zone Director didn't show any information") >= 0:
                    errmsg = ''
                else:
                    errmsg = 'The client info should not be shown in zd'
                    
            passmsg = "Client information is correct in ZD Web UI"
                
        except Exception,ex:
            errmsg = ex.message
            
        step_name = "Verify station info on ZD"
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)
            
    def _verify_station_info_on_ap(self):
        '''
        Verify station information on AP.
        '''
        errmsg = None
        passmsg = None
        
        try:
            if not self.conf['wlan_cfg'].has_key('name'):
                self.wlan_cfg_name = self.conf['wlan_cfg']['ssid']
            else:
                self.wlan_cfg_name = self.conf['wlan_cfg']['name']
            errmsg = tmethod.verify_station_info_on_ap(self.active_ap, 
                                                       self.sta_wifi_mac_addr, 
                                                       self.wlan_cfg_name, 
                                                       self.client_info_on_zd['channel'])
            
            passmsg = "Client information is correct in AP"
        except Exception, ex:
            errmsg = ex.message
        
        step_name = "Verify station info on AP"
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)
            
    def _verify_station_in_tunnel_mode(self):
        '''
        Verify station tunnel mode: if do_tunnel is True, station is in tunnel mode,
        else station is not in tunnel mode.
        '''
        errmsg = None
        passmsg =None
        step_name = None
        
        try:
            tunnel_mode = self.conf['wlan_cfg'].get('do_tunnel')
            if tunnel_mode == True:
                step_name = "Verify station in tunnel mode"
                passmsg = "Station is in tunnel mode"
            else:
                #Tunnel mode default value is False.
                step_name = "Verify station not in tunnel mode"
                passmsg = "Station is not in tunnel mode"
                
            errmsg = self.testbed.verify_station_mac_in_tunnel_mode(self.ap_mac_addr, self.sta_wifi_mac_addr, tunnel_mode)
        except Exception, e:
            errmsg = e.message
        
        if errmsg and step_name:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)