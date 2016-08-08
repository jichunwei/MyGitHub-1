'''
Description:
    config:
        
    test:
    
    cleanup:
    
    WLAN Config:
        'ssid': 'wlan-dpsk',
        'auth': 'PSK',
        'wpa_ver': 'WPA',
        'encryption': 'AES',
        'type': 'standard',
        'key_string': '1234567890',
        'key_index': '',
        'auth_svr': '',
        'do_zero_it': True,
        'do_dynamic_psk': True,
                    
Created on 2010-6-9
@author: cwang@ruckuswireless.com
'''
import logging
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_Multi_DPSK(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)
    
    def test(self):
        passmsg = []
        repeat_cnt = self.conf['repeat_cnt']
        self.dpsk_cfg = {'psk_expiration': self.conf['psk_expiration'],
                         'wlan': self.wlan_cfg['ssid'],                    
                         'expected_response_time': self.conf['expected_response_time'],
                         'number_of_dpsk': self.conf['number_of_dpsk'],
                         'repeat_cnt':repeat_cnt,              
                         }     
                
        while repeat_cnt:                    
            self._generate_multiple_dpsk(self.dpsk_cfg)
            repeat_cnt = repeat_cnt - 1
            
            if self.errmsg:
                return ["FAIL", self.errmsg]
        self.passmsg = "totally create %d dpsk" % (self.dpsk_cfg['repeat_cnt'] * self.dpsk_cfg['number_of_dpsk'])
        logging.info(self.passmsg)
        
        passmsg.append(self.passmsg)
        
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        #"wlan-dpsk" must support dynamic PSK method.
        if self.carrierbag.has_key('wlan-dpsk'):            
            self.wlan_cfg = self.carrierbag['wlan-dpsk']
    
    def _update_carrier_bag(self):
        
        self.carrierbag['existed_dpsk_cfg'] = self.dpsk_cfg
    
    def _init_test_params(self, conf):
        '''
            total_dpsk = number_of_dpsk * repeat_cnt
            
            for example:
                1000 = 100 * 10
        '''
        self.conf = {'number_of_dpsk': 100,
                'repeat_cnt': 10,                
                'psk_expiration': 'Unlimited',
                'expected_response_time': 30,
                'wlan_cfg':{'ssid': 'wlan-dpsk',
                            'auth': 'PSK',
                            'wpa_ver': 'WPA',
                            'encryption': 'AES',
                            'type': 'standard',
                            'key_string': '1234567890',
                            'key_index': '',
                            'auth_svr': '',
                            'do_zero_it': True,
                            'do_dynamic_psk': True,                 
                            },
                }      
        self.conf.update(conf)          
        self.wlan_cfg = None
        self.wlan_cfg = self.conf['wlan_cfg']        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
                
    
    def _generate_multiple_dpsk(self, dpsk_conf):
        
        gen_msg = "Try to generate %s Dynamic PSKs automatically." % \
                      dpsk_conf['number_of_dpsk']
        pass_msg = "%s Dynamic PSKs were generated successfully. "
        pass_msg = pass_msg % dpsk_conf['number_of_dpsk']
        logging.info(gen_msg)
        lib.zd.wlan.generate_multiple_dpsk(self.zd, dpsk_conf)
        logging.info(pass_msg)
        