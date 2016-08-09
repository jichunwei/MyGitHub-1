'''
Description:
    Create multiple AP Groups and verify the numbers.
    
Created on OCT 2, 2011
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group as hlp


class CB_ZD_Create_Multi_AP_Groups(Test):
    '''       
    '''
    def config(self,conf):
        self.conf = {'numbers':1,
                     'apg_cfg':{'apg_prefix_name':'ap_group',
                                'an_wg_prefix_name': 'Default',
                                'gn_wg_prefix_name': 'Default',                   
                                'an': {'channel': '36',
                                       'channelization': '20',
                                       'mode': 'Auto',
                                       'power': 'Full',
                                       'wlangroups': 'Default', 
                                       },
                                'gn': {'channel': '11',
                                        'channelization': '40',
                                        'mode': 'N/AC-only',
                                        'power': '-1dB',
                                        'wlangroups': 'Default'},                    
                     }}
        self.conf.update(**conf)
        self._init_test_params(self.conf)
        self.numbers = self.conf.pop('numbers')
        self.apg_cfg = self.conf.pop('apg_cfg')
        self.apg_prefix_name = self.apg_cfg.pop('apg_prefix_name')
        self.an_wg_prefix_name = self.apg_cfg.pop('an_wg_prefix_name')
        self.gn_wg_prefix_name = self.apg_cfg.pop('gn_wg_prefix_name')
    
    def test(self):
        for i in range(self.numbers):
            apg_name = '%s%d' % (self.apg_prefix_name, i+1)
            
            if self.apg_cfg.has_key('gn') and self.gn_wg_prefix_name != 'Default':
                self.apg_cfg['gn']['wlangroups'] = '%s%d' % (self.gn_wg_prefix_name, i+1)
            else:
                self.apg_cfg['gn']['wlangroups'] = 'Default'
    
            if self.apg_cfg.has_key('an') and self.an_wg_prefix_name != 'Default':
                self.apg_cfg['an']['wlangroups'] = '%s%d' % (self.an_wg_prefix_name, i+1)
            else:
                self.apg_cfg['an']['wlangroups'] = 'Default'
            try:
                hlp.create_ap_group(self.zd, apg_name, **self.apg_cfg)            
            except Exception, e:
                return self.returnResult('ERROR', e.message)
        size = hlp.get_apg_total_number(self.zd) 
        if (size -1) == self.numbers:
            return self.returnResult('PASS', 
                                     'Have created %d AP Group' % self.numbers)
        else:
            return self.returnResult('FAIL', 
                                     'Expected %d AP Group created, actual %d' \
                                     % (self.numbers, size -1))
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass
    