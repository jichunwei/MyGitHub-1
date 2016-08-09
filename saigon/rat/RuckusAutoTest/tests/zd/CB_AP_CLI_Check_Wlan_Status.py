'''
Created on Nov 14, 2014

@author: Yin.wenling
'''


import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import radiogroup


class CB_AP_CLI_Check_Wlan_Status(Test):
    required_components = ['RuckusAP']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'wlan_name':'',
                     'ap_tag' : 'AP_01',
                     'expect_status':'up',
                     'wait_time':5,
                     'force_ssh':False}
        self.conf.update(conf)
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']        
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):    
        st = time.time()
        ap_mac = self.active_ap.base_mac_addr
        if self.conf['wlan_name'] == '': 
            self.conf['wlan_name'] = "island-%s" % ap_mac.replace('-','').replace(':','')[6:]
        time.sleep(self.conf['wait_time'])
        while time.time() - st < 230:
            if self.conf['force_ssh']:
                wlan_list = radiogroup.get_wlanlist(self.active_ap,force_ssh = True)  
            else:
                wlan_list = radiogroup.get_wlanlist(self.active_ap)          
            cnt = 0
            for wlan in wlan_list:
                if 'AP' == wlan.get('type') and self.conf['expect_status'] == wlan.get('status') and self.conf['wlan_name'].upper() == wlan.get('ssid').upper():
                    return self.returnResult('PASS', 'The WLANs status is correct')
                
            time.sleep(10)
        if 'wlan_list' in locals():
            logging.info(wlan_list)
                
        return self.returnResult('FAIL', 'The WLANs status is incorrect, please check')
    
    
    def cleanup(self):
        self._update_carribag()