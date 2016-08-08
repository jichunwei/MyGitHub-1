'''
Created on Sep 30, 2014

@author: chen tao
'''

import logging

from RuckusAutoTest.models import Test

class CB_Switch_Set_LLDP(Test):
    required_components = ['L3Switch']
    parameter_description = {}

    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self.set_lldp()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'state':'enable','mgmt_ip':'192.168.0.253'}
        self.conf.update(conf)
        self.switch = self.testbed.components["L3Switch"]

    def set_lldp(self):
        
        logging.info('Set lldp in Swtich')
        try:
            if self.conf['state'].lower() == 'enable':
                self.switch.enable_lldp()
                self.switch.set_lldp_mgmt_ip(self.conf['mgmt_ip'])
                if self.switch.is_lldp_enabled() == True:            
                    self.passmsg = 'Enable lldp in switch successfully.'
                else:
                    self.errmsg = 'Failed to enable lldp in switch'
                return
            if self.conf['state'].lower() == 'disable':
                self.switch.disable_lldp()
                if self.switch.is_lldp_enabled() == False:            
                    self.passmsg = 'Disable lldp in switch successfully.'
                else:
                    self.errmsg = 'Failed to disable lldp in switch'   
        except Exception, ex:
            self.errmsg = ex.message   

