'''
Description: This script is used to verify the information of the station shown on the ZD.
Created on Jul 11, 2011
@author: jluh@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Verify_Active_Client_Info(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):                        
        self._testVerifyStationInfoOnZD()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self._updateCarrierBag()
        self.passmsg = 'Verify station information [%s] on zd successfully' % self.client_info_on_zd      
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_status_timeout':120, 'username':'', 'chk_empty':False, 'radio_mode':None}
        self.exp_client_info = {"status": "Authorized"}
        self.conf.update(conf)
        self.wlan_cfg = conf['wlan_cfg']
        self.radio_mode = self.conf['radio_mode']
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.zd = self.testbed.components["ZoneDirector"]
        
        self.exp_client_info = {"ip": None, 
                                "status": "Authorized", 
                                "wlan": self.wlan_cfg['ssid'], 
                                "radio": None, 
                                "apmac": self.active_ap.base_mac_addr, 
                                }
        
        self.exp_client_info['status'] = self.conf['status']
        
        logging.info("Verify information of the target station shown on the Zone Director")
        if self.radio_mode == 'g' or self.wlan_cfg['encryption'].upper() in ['TKIP', 'WEP-64', 'WEP-128','WEP64','WEP128']:
            self.expected_radio_mode = ['802.11b/g', '802.11a']
        else:
            self.expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
        
        if self.wlan_cfg['encryption'].upper() in ['AUTO'] and self.wlan_cfg['sta_encryption'].upper() in ['TKIP']:
            self.expected_radio_mode = ['802.11b/g', '802.11a']
            
        if self.wlan_cfg['auth'] == 'EAP':
            self.expected_ip = self.wlan_cfg['username']

        if self.wlan_cfg.has_key('do_webauth') and self.wlan_cfg['do_webauth']:
            if self.exp_client_info['status'] == 'Authorized':
                self.expected_ip  = self.conf['username']
            elif self.exp_client_info['status'] == 'Unauthorized':
                self.expected_ip  = self.sta_wifi_ip_addr
            else:
                pass
            
        if self.wlan_cfg.has_key('type') and self.wlan_cfg['type'] == 'guest':
            if self.conf.has_key('use_guestpass_auth') and self.conf['use_guestpass_auth']:
                if self.conf.has_key('guest_name') and self.conf['guest_name']:
                    self.expected_ip = self.conf['guest_name']
            elif self.conf.has_key('use_guestpass_auth') and not self.conf['use_guestpass_auth']:
                self.expected_ip = 'guest'
            else:
                self.expected_ip = self.sta_wifi_ip_addr
        
        self.exp_client_info['radio'] = self.expected_radio_mode      
        self.exp_client_info['ip'] = self.expected_ip
              
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyStationInfoOnZD(self):
        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, 
                                                                              self.sta_wifi_mac_addr, 
                                                                              self.exp_client_info, 
                                                                              self.conf['check_status_timeout'])
        if 'chk_empty' in self.conf:
            if self.conf['chk_empty']:
                if self.errmsg and self.errmsg.find("Zone Director didn't show any information") >= 0:
                    self.errmsg = ''
                else:
                    self.errmsg = 'The client info should not be shown in zd'
        
    def _updateCarrierBag(self):
        self.carrierbag['client_info_on_zd'] = self.client_info_on_zd

