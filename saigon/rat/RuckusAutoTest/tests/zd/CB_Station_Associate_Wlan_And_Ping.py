#encoding:utf-8
'''
Created on 2013-05-15

@author: ye.songnan@odc-ruckuswireless.com

Description:

Let Station associate the 27 wlans one by one, and ping.

'''

import logging
import copy
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_Station_Associate_Wlan_And_Ping(Test):
    
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        for wlan_cfg in self.wlan_list:
            #Restart adapter
            if self.conf['is_restart_adapter']:
                tmethod.restart_station_adapter(self.target_station)
            #Associate to wlan and verify it
            time.sleep(20)    
            self._test_assoc_station_with_ssid(wlan_cfg)
            logging.info("Associate to wlan : %s"  %wlan_cfg['ssid'])
            #Ping 
            time.sleep(10)
            for ip in self.target_list:
                logging.info("Ping destination : %s"  %ip)
                self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, ip,
                                                                      ping_timeout_ms = self.conf['ping_timeout_ms'])
                
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = '[ZDCLI] Station associate wlans and ping one by one successfully.' 
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {
            'wlan_list':[], 
            'check_status_timeout': 120,
            'break_time': 10,
            'restart_cnt': 6,
            'is_restart_adapter': False,
            'sta_tag': "sta1",
            'ping_timeout_ms': 15 * 1000,
            'target_ip_list': ['192.168.0.252'],
            }            
        
        self.conf.update(conf)
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.target_list = self.conf['target_ip_list']  
        self.wlan_list = self.conf['wlan_list'] 
            
    def _test_assoc_station_with_ssid(self,wlan_cfg):
        wlan_cfg = copy.deepcopy(wlan_cfg)

        if wlan_cfg.has_key("wpa_ver") and wlan_cfg.get("wpa_ver").lower() == "wpa_mixed":
            wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']

        if wlan_cfg.has_key("encryption") and wlan_cfg.get("encryption").lower() == "auto":
            wlan_cfg['encryption'] = wlan_cfg['sta_encryption']

        self.errmsg = tmethod.assoc_station_with_ssid(
            self.target_station, wlan_cfg, self.conf['check_status_timeout'],
            self.conf['break_time'], self.conf['restart_cnt'])

        self.errmsg = tmethod.verify_wlan_in_the_air(
            self.target_station, wlan_cfg['ssid'])
