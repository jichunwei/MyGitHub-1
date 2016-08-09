'''
Description:
    This script is used to verify the client connectivity.

Procedure:
    +Renew WIFI address in client if needed.
    +Verify client information on ZD GUI -> Monitor -> Currently Active Clients page.
    +Verify client MAC in the MAC table of L3Switch if tunnel mode is enabled in WLAN.
    +Verify client is allowed to ping a target IP.
    
Created on Jan 7, 2012
@author: serena.tan@ruckuswireless.com
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Verify_Station_Connectivity(Test):
    required_components = ['ZoneDirector', 'AP']
    parameters_description = {}
    
    def config(self, conf):
        self._initTestParameters(conf)
        self._retrieve_carribag()

    def test(self):
        try:
            if not self.sta_wifi_ip_addr or not self.sta_wifi_mac_addr:
                res, var1, var2 = tmethod.renew_wifi_ip_address(
                    self.target_station, 
                    self.conf['check_status_timeout']
                    )
                if not res:
                    return self.returnResult('FAIL', var2)
            
                self.sta_wifi_ip_addr = var1
                self.sta_wifi_mac_addr = var2
            
            self._testVerifyStationInfoOnZD()
            if self.errmsg: 
                return self.returnResult('FAIL', self.errmsg)
            
            self.passmsg += 'Verify station info on ZD successfully.'
             
            if self.conf['wlan_cfg'].get('do_tunnel'):
                self.testbed.verify_station_mac_in_tunnel_mode(self.ap_mac,
                                                               self.sta_wifi_mac_addr.lower(),
                                                               True)
            
                self.passmsg += 'Verify client MAC address in tunnel mode successfully.'
            
            # An Nguyen, Mar 2013 - Added the option to verify the ping in duration of time
            
            import random
            time_padding = random.randint(5,15)
            
            if self.conf['wlan_cfg'].get('interim_update'):
                verify_ping_time = int(self.conf['wlan_cfg']['interim_update'])*60 + time_padding
            elif self.conf.get('interim_update'):
                verify_ping_time = int(self.conf['interim_update'])*60 + time_padding
            else:
                verify_ping_time = self.conf['ping_timeout_ms']/1000 + time_padding
            
            start_time = time.time()
            ping_time = time.time() - start_time
            while ping_time < verify_ping_time:
                ping_time = time.time() - start_time
                self.errmsg = tmethod.client_ping_dest_is_allowed(
                                  self.target_station,
                                  self.conf['target_ip'],
                                  ping_timeout_ms = self.conf['ping_timeout_ms']
                                  )
                time.sleep(10)
                
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            self.passmsg += "Client ping IP[%s] successfully." % self.conf['target_ip']
            
        except Exception, ex:
            return self.returnResult('FAIL', ex.message)
        
        self._updateCarrierBag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'sta_tag': '',
                     'ap_tag': '',
                     'wlan_cfg': {},
                     'status': 'Authorized',
                     'use_guestpass_auth': True,
                     'guest_name': '',
                     'username': '',
                     'radio_mode': None,
                     'target_ip': '172.16.10.252',
                     'check_status_timeout': 120,
                     'ping_timeout_ms': 20 * 1000,#@author: Jane.Guo @since: 2013-10 120s is too long.
                     'renew_wifi_ip_address': False,
                     'zd_tag':'',
                     }
        self.conf.update(conf)
        
        self.wlan_cfg = self.conf['wlan_cfg']
        self.radio_mode = self.conf['radio_mode']
        #For radio mode is 'bg', need to set it to 'g'.
        if self.radio_mode == 'bg':
            self.radio_mode = 'g'
            
        if self.conf['zd_tag']:
            self.zd = self.carrierbag[self.conf['zd_tag']]
        else: 
            self.zd = self.testbed.components['ZoneDirector']

        self.sta_wifi_mac_addr = '' 
        self.sta_wifi_ip_addr = ''
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        sta_dict = self.carrierbag.get(self.conf['sta_tag'])
        if not sta_dict:
            raise Exception("No station provided.")
        
        self.target_station = sta_dict['sta_ins']
        if not self.conf['renew_wifi_ip_address']:
            self.sta_wifi_mac_addr = sta_dict['wifi_mac_addr']
            self.sta_wifi_ip_addr = sta_dict['wifi_ip_addr']
        
        if self.conf['ap_tag']:
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
            #@author: Jane.Guo @since: 2013-10 fix bug zf-5773
            self.ap_mac = self.active_ap.base_mac_addr
        else:
            self.active_ap = None
            self.ap_mac = ""
        
    def _testVerifyStationInfoOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director")
        if self.radio_mode == 'g' or \
           str(self.wlan_cfg.get('encryption')).upper() in ['TKIP', 'WEP-64', 'WEP-128', 'WEP64', 'WEP128']:
            expected_radio_mode = ['802.11b/g', '802.11a']
        elif str(self.wlan_cfg.get('encryption')).upper() == 'AUTO' and \
             str(self.wlan_cfg.get('sta_encryption')).upper() in ['TKIP', 'WEP-64', 'WEP-128', 'WEP64', 'WEP128']:
            expected_radio_mode = ['802.11b/g', '802.11a']
        else:
            expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
        
        expected_ip = self.sta_wifi_ip_addr
        if self.wlan_cfg.get('auth') == 'EAP':
            expected_ip = self.wlan_cfg['username']

        elif self.wlan_cfg.get('web_auth') or self.wlan_cfg.get('do_webauth'):
            if self.conf['status'] == 'Authorized':
                expected_ip  = self.conf['username'] if self.conf['username'] else self.wlan_cfg['username']
                
        elif self.wlan_cfg.get('type') == 'guest' and self.conf['status'] == 'Authorized':
            if self.conf['use_guestpass_auth']:
                expected_ip = self.conf['guest_name']
                
            else:
                expected_ip = 'guest'
        
        elif self.wlan_cfg.get('type') == 'hotspot' and self.conf['status'] == 'Authorized':
            expected_ip = self.conf['username']
                
        exp_client_info = {"status": self.conf['status'], 
                           "wlan": self.wlan_cfg['ssid'],
                           "radio": expected_radio_mode,
                           "ip": expected_ip
                           }
        
        if self.wlan_cfg.get('vlan'):
            exp_client_info['vlan'] = self.wlan_cfg['vlan']
            
        if self.active_ap != None:
            exp_client_info['apmac'] = self.active_ap.base_mac_addr
            
        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, 
                                                                              self.sta_wifi_mac_addr, 
                                                                              exp_client_info, 
                                                                              self.conf['check_status_timeout'])
        
    def _updateCarrierBag(self):
        self.carrierbag['client_info_on_zd'] = self.client_info_on_zd
        self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.sta_wifi_mac_addr
        self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.sta_wifi_ip_addr