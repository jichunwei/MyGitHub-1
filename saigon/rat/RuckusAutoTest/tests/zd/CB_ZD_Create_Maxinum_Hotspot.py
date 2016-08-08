'''
Description:
Created on 2010-8-16
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_Maxinum_Hotspot(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
                
        self._create_maxinum_hotspot()
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "All of hotspot entries create successfully")        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(num_of_hotspots = 31,
                         num_of_rules = 16,
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']   
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        self.errmsg = ''
        self.passmsg = ''

    def _create_maxinum_hotspot(self):
            h_cnt = self.conf['num_of_hotspots']
            r_cnt = self.conf['num_of_rules']
            h_cfg = {
                'name': '',
                'login_page': 'http://www.example.net',
                'start_page': None,
                'session_timeout': None,
                'idle_timeout': None,
                'auth_svr': '',
                'acct_svr': '',
                'interim_update_interval': None,
                'radius_location_id': '',
                'radius_location_name': '',
                'walled_garden_list': [],
                'restricted_subnet_list': [],
                'enable_mac_auth': None,
            }
            r_cfg = {'description': '',
                      'action': 'Allow',
                      'destination_addr': 'Any',
                      'application': 'Any',
                      'protocol': None,
                      'destination_port': None,
                      }
            r_list = []
            for i in range(1, r_cnt + 1):
                r_list.append(r_cfg.copy())
                
            h_cfg['restricted_subnet_list'] = r_list
            h_list = []
            for i in range(1, h_cnt + 1):
                h_cfg_tmp = h_cfg.copy()
                h_cfg_tmp['name'] = 'Test_Hotspots_%d' % i
                h_list.append(h_cfg_tmp)
                
            h_cfg = h_list.pop()
            lib.zd.wispr.create_profile(self.zd, **h_cfg)
            logging.info('hotspot [%s] created successfully' % h_cfg['name'])
            for h in h_list:
                lib.zd.wispr.clone_profile(self.zd, h_cfg['name'], h['name'])
                logging.info('hotspot [%s] cloned successfully' % h['name'])         
    
