'''
Created on Nov 7, 2014

@author: Yin.wenling
'''

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import radiogroup


class CB_AP_SHELL_Get_Config_Wlan_Psk(Test):
    required_components = ['RuckusAP']
    parameters_description = {'ap_tag': 'AP_01',
                              'get_psk_ap':''}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self.psk = self._get_psk()
            
            if not self.psk:
                self.errmsg = "Get psk fail"
                return self.returnResult("FAIL",self.errmsg)
                
        except Exception, ex:
            self.errmsg = 'Get bssid failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Get psk is %s' % self.psk
            return self.returnResult('PASS', pass_msg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'ap_tag': 'AP_01',
                     'get_psk_ap':''}
        self.conf.update(conf)
        self.errmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
        self.get_psk_ap = self.carrierbag[self.conf.get('get_psk_ap')]['ap_ins']
    
    def _update_carrier_bag(self):
        self.carrierbag[self.conf['get_psk_ap']]['config_wlan_psk'] = self.psk
    
    def _get_psk(self): 
        ap_mac = self.get_psk_ap.get_base_mac()
        psk = self.active_ap.get_config_wlan_psk(ap_mac)
        return psk   

