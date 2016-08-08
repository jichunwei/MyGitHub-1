'''
Description:

   Check if station info exists in active AP CLI info by station mac address

Create on 2013-4-10
@author: kevin.tan@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_AP_CLI_Check_Station(Test):
    required_components = ['RuckusAP']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'ssid':'',
                     'check_status_timeout': 120,
                     'break_time': 10,
                     'restart_cnt': 6,
                     'is_negative':False}
        self.conf.update(conf)
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']        
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        if not self.conf['is_negative']:
            self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']

    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        wlan_if = self.active_ap.ssid_to_wlan_if(self.conf['ssid'])
        
        if self.conf['is_negative']:
            if self.conf.get('wlan_cfg'):
                wlan_cfg = self.conf['wlan_cfg']

                if wlan_cfg.has_key("wpa_ver") and wlan_cfg.get("wpa_ver").lower() == "wpa_mixed":
                    wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
        
                if wlan_cfg.has_key("encryption") and wlan_cfg.get("encryption").lower() == "auto":
                    wlan_cfg['encryption'] = wlan_cfg['sta_encryption']

                tmethod.assoc_station_with_ssid(self.target_station, wlan_cfg, 
                                                self.conf['check_status_timeout'],self.conf['break_time'], self.conf['restart_cnt'])

            info = self.active_ap.get_station_info(wlan_if)
            if len(info) == 0:
                return self.returnResult('PASS', 'Check station information should not exist in WLAN[%s] by AP CLI' % self.conf['ssid'])
        else:
            info = self.active_ap.get_station_info(wlan_if)
            if info.has_key(self.sta_wifi_mac_addr):
                return self.returnResult('PASS', 'Check station information in AP CLI successfully')
                            
        return self.returnResult('FAIL', 'Check station information in AP CLI failed')
    
    def cleanup(self):
        self._update_carribag()
