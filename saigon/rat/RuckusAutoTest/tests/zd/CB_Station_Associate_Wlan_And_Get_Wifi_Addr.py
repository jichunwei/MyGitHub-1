'''
Procedure: 
    1.Remove all wlans from target station.
    2.Associate the target station.
    2.Get station wifi ip address.

Create on 2011-9-26
@author: serena.tan@ruckuswireless.com
'''


import logging
import time
from copy import deepcopy

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_Station_Associate_Wlan_And_Get_Wifi_Addr(Test):
    required_components = ['Station']
    parameters_description = {'check_status_timeout': '',
                              'wlan_cfg': 'The wlan configuration',
                              'sta_tag': 'The station tag in carrierbag'}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            tconfig.remove_all_wlan_from_station(
                self.station,
                check_status_timeout = self.conf['check_status_timeout']
            )
            
            wlan_cfg = deepcopy(self.conf['wlan_cfg'])
            if (wlan_cfg.has_key("wpa_ver") and wlan_cfg['wpa_ver'] == "WPA_Mixed") or \
               (wlan_cfg.has_key("encryption") and wlan_cfg['encryption'] == "Auto"):
                wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
                wlan_cfg['encryption'] = wlan_cfg['sta_encryption']
            if self.conf.has_key('config_wlan_ap') and self.conf.get('config_wlan_ap'):
                if wlan_cfg.get('key_string') == '':
                    wlan_cfg['key_string'] = self.carrierbag[self.conf['config_wlan_ap']]['config_wlan_psk']
            
            time.sleep(self.conf['wait_before_associate'])
            self.errmsg = tmethod.assoc_station_with_ssid(
                self.station,
                wlan_cfg,
                self.conf['check_status_timeout']
            )
            time.sleep(5)
            if self.errmsg:
                self.errmsg = tmethod.verify_wlan_in_the_air(self.station, wlan_cfg['ssid'])
                logging.info(self.errmsg)
                if self.is_negative:
                    if "couldn't associate" in self.errmsg:
                        self.errmsg = ""
                        self.passmsg = "The station was not allowed to associate due to ACL."
                    else:
                        if self.check_wlan_exist:
                            if "didn't see" in self.errmsg:
                                self.errmsg = ""
                                self.passmsg = "The station didn't see the wlan in the air due to ACL."
                            else:
                                return self.returnResult('FAIL', self.errmsg)

            if not self.check_wlan_exist:
                res, self.var1, self.var2 = tmethod.renew_wifi_ip_address(
                                                self.station, 
                                                self.conf['check_status_timeout'],
                                                2,
                                                self.conf['auth_deny']
                                            )
                if not res:
                    self.errmsg = self.var2
            
                else:
                    passmsg = 'Station[%s] associate wlan[%s] and get wifi ip address[%s] successfully'
                    self.passmsg = passmsg % (self.station.get_ip_addr(), wlan_cfg['ssid'], self.var1)
            
        except Exception, e:
            self.errmsg = 'Verify guest pass expired time on ZD WebUI failed: %s' % e.message
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'check_status_timeout': 120,
                     'wlan_cfg': {},
                     'sta_tag': '',
                     'wlan_ssid': '',
                     'check_wlan_exist':False,
                     'auth_deny':False,
                     'is_negative': False,
                     'wait_before_associate':0,
                     'config_wlan_ap' : ''
                     }
        self.conf.update(conf)
        if self.conf['config_wlan_ap']:
            ap_mac = self.carrierbag[self.conf.get('config_wlan_ap')]['ap_ins'].base_mac_addr
            self.conf['wlan_ssid'] = "island-%s" % ap_mac.replace('-','').replace(':','')[6:].upper()
            self.conf['wlan_cfg']['name'] = self.conf['wlan_ssid']
            self.conf['wlan_cfg']['ssid'] = self.conf['wlan_ssid']
    
        if self.conf['wlan_cfg']:
            pass
        elif self.conf.get('wlan_ssid'):
            self.conf['wlan_cfg'] = self.carrierbag[self.conf['wlan_ssid']]
        else:
            raise Exception('WLAN configuration parameter is not exist. Please check!')
        self.is_negative = self.conf['is_negative']
        self.check_wlan_exist = self.conf['check_wlan_exist']
        self.station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        pass
            
    def _update_carribag(self):
        if not self.check_wlan_exist:
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.var1
            self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.var2.lower()
