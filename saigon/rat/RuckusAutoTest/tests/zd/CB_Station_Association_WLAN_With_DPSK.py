"""
Description: This script is used to configure a WLAN with DPSK on the target station and check association status of the target station.
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
@since: April 2012
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from copy import deepcopy


class CB_Station_Association_WLAN_With_DPSK(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._test_associate_station_with_ssid()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = 'Associate station [%s] successfully' % self.target_station.ip_addr
        self._update_carrier_bag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'check_status_timeout': 120,
                     'expect_result': 'pass'}
        
        self.conf.update(conf)
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        
        wlan_cfg = {}
        if self.conf.get('wlan_ssid'):
            wlan_cfg = self.carrierbag[self.conf['wlan_ssid']]
        else:
            raise Exception('WLAN configuration parameter is not exist. Please check!')
        
        self.wlan_cfg = deepcopy(wlan_cfg)
        if self.wlan_cfg.get('wpa_ver') == "WPA_Mixed":
            self.wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
            self.wlan_cfg['encryption'] = wlan_cfg['sta_encryption']
        
        if self.conf.get('dpsk_info'):
            self.dpsk = self.conf['dpsk_info']
        elif self.carrierbag.get('last_generated_dpsks'):
            self.dpsk = self.carrierbag['last_generated_dpsks'][self.carrierbag['last_generated_dpsks'].keys()[0]]
        else:
            raise Exception('DPSK configuration parameter is not exist. Please check!')
        
        self.wlan_cfg['key_string'] = self.dpsk['Passphrase']
        
        self.errmsg = ''
        self.passmsg = ''

    def _test_associate_station_with_ssid(self):
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.conf['check_status_timeout'])
        if self.errmsg:
            self.errmsg = tmethod.verify_wlan_in_the_air(self.target_station, self.wlan_cfg['ssid'])
            return
        
        if self.conf.has_key("auth_deny"):
            logging.info("Get Mac address of the wireless adapter on the target station")
            res, self.var1, self.var2 = tmethod.renew_wifi_ip_address(self.target_station, 
                                                                      self.conf['check_status_timeout'],
                                                                      2,
                                                                      self.conf['auth_deny'])
            if not res:
                self.errmsg = self.var2            
            else:
                passmsg = 'Station[%s] associate wlan[%s] and get Mac address[%s] successfully'
                self.passmsg = passmsg % (self.target_station.get_ip_addr(), self.wlan_cfg['ssid'], self.var2)
        
        else:
            logging.info("Renew IP address and Mac of the wireless adapter on the target station")
            res, self.var1, self.var2 = tmethod.renew_wifi_ip_address(self.target_station, 
                                                                      self.conf['check_status_timeout']
                                                                      )
            if not res:
                self.errmsg = self.var2            
            else:
                passmsg = 'Station[%s] associate wlan[%s] and get wifi ip address[%s] successfully'
                self.passmsg = passmsg % (self.target_station.get_ip_addr(), self.wlan_cfg['ssid'], self.var1)
        
    def _update_carrier_bag(self):
        if self.conf.has_key("auth_deny"):
            self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.var2
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = ""
        else:
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.var1
            self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.var2
                
        self.carrierbag[self.conf['sta_tag']]['expected_station_info'] = {}
        self.carrierbag[self.conf['sta_tag']]['expected_station_info'].update({'wlan': self.wlan_cfg['ssid'],
                                                                               'status': 'Authorized',
                                                                               'ip': self.dpsk['User Name']})
        if self.dpsk['Vlan ID'] and int(self.dpsk['Vlan ID']) in range (2, 4094):
            self.carrierbag[self.conf['sta_tag']]['expected_station_info']['vlan'] = self.dpsk['Vlan ID']