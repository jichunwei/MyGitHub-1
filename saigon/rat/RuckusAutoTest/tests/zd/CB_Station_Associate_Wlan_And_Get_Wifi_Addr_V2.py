'''
This test API base on the CB_Station_Associate_Wlan_And_Get_Wifi_Addr procedure.
Added enhancement by support negative test.

Procedure: 
    1.Remove all wlans from target station.
    2.Associate the target station.
    2.Get station wifi ip address.

Modified by An Nguyen, an.nguyen@ruckuswireless.com
@since: Dec 2012
'''


import logging
from copy import deepcopy

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2(Test):
    required_components = ['Station']
    parameters_description = {'check_status_timeout': '',
                              'wlan_cfg': 'The wlan configuration',
                              'sta_tag': 'The station tag in carrierbag'}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carrierbag()
  
    def test(self):
        res, msg = self._verify_station_association()
        
        return self.returnResult(res, msg)        
  
    def cleanup(self):
        pass
    
    
    def _init_params(self, conf):
        self.conf = {'check_status_timeout': 120,
                     'wlan_cfg': {},
                     'sta_tag': '',
                     'wlan_ssid': '',
                     'negative_test': False,
                     }
        self.conf.update(conf)        
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _verify_station_association(self):
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
            
            self.errmsg = tmethod.assoc_station_with_ssid(
                self.station,
                wlan_cfg,
                self.conf['check_status_timeout']
            )
            if self.errmsg:
                self.errmsg = tmethod.verify_wlan_in_the_air(self.station, wlan_cfg['ssid'])
                logging.info(self.errmsg)                
            else:
                self.errmsg = ''
                
            res, self.var1, self.var2 = tmethod.renew_wifi_ip_address(
                                            self.station, 
                                            self.conf['check_status_timeout']
                                        )
            #@author: Jane.Guo add get ip config info include subnet,mask,gateway
            self.ip_cfg = self.station.get_ip_config()
            logging.info("Get ip config from station: %s" % self.ip_cfg)
            
            if not res:
                self.errmsg = self.errmsg + '. ' + self.var2
            
            else:
                passmsg = 'Station[%s] associate WLAN[%s] and get wifi ip address[%s] successfully'
                self.passmsg = passmsg % (self.station.get_ip_addr(), wlan_cfg['ssid'], self.var1)
            
        except Exception, e:
            self.errmsg = self.errmsg + '. ' + 'Station[%s] failed to associate to WLAN %s: %s' % (self.station.get_ip_addr(), self.conf['wlan_cfg']['ssid'], e.message)
        
        # Return the result base on the negative test option
        if self.errmsg:
            if self.conf['negative_test']:
                passmsg = '[Correct behavior]: %s' % self.errmsg
                logging.info(passmsg)
                return ('PASS', passmsg)
            else:
                logging.info(self.errmsg)
                return ('FAIL', self.errmsg)
        else:
            if self.conf['negative_test']:
                errmsg = '[Incorrect behavior]: %s' % self.passmsg
                logging.info(errmsg)
                return ('FAIL', errmsg)
            else:
                logging.info(self.passmsg)
                self._update_carrierbag()
                return ('PASS', self.passmsg)
        
    def _retrieve_carrierbag(self):
        if self.conf['wlan_cfg']:
            pass
        elif self.conf.get('wlan_ssid'):
            self.conf['wlan_cfg'] = self.carrierbag[self.conf['wlan_ssid']]
        else:
            raise Exception('WLAN configuration parameter is not exist. Please check!')
        
        self.station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
            
    def _update_carrierbag(self):
        self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.var1
        self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.var2.lower()
        self._update_wifi_ip_cfg()
    
    def _update_wifi_ip_cfg(self):
        """
         @author: Jane.Guo add get ip config info include subnet,mask,gateway
        """
        self.update_ip_cfg = {}
        #Fixed by cwang, bugID#ZF-5449, KeyError: 'dhcp_enabled'
        if self.ip_cfg.get('dhcp_enabled') == 'Yes':
            self.update_ip_cfg['source'] = 'DHCP'
        else:
            self.update_ip_cfg['source'] = 'Static'           
        self.update_ip_cfg['addr'] = self.ip_cfg['ip_addr']
        self.update_ip_cfg['mask'] = self.ip_cfg['subnet_mask']
        self.update_ip_cfg['gateway'] = self.ip_cfg['gateway']
        self.carrierbag[self.conf['sta_tag']]['wifi_ip_cfg'] = self.update_ip_cfg
