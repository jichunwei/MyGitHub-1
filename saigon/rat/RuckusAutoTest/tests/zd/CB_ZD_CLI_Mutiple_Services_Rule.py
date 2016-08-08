'''
Created on 2013-09-24
@author: ye.songnan@odc-ruckuswireless.com
description:
    21 well-known types of services rule, 48 rules per type.
    1 other unknown types of services rule, 16 rules per type.
    Total: 21*48 + 1*16 = 1024
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import bonjour_gateway as bg

class CB_ZD_CLI_Mutiple_Services_Rule(Test):
    '''
    21 well-known types of services rule, 48 rules per type.
    1 other unknown types of services rule, 16 rules per type.
    Total: 21*48 + 1*16 = 1024
    
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        dict_names_types = bg.map_names_types()
        service_list = dict_names_types.keys()
        #21 well-known types
        #Create well-known tpyes of rule: 21*10 = 210
        for service in service_list:
            to_vlan = 20
            for from_vlan in range(10, 20): 
                (v, self.errmsg) = bg.new_services_rule(self.zdcli, service, from_vlan, to_vlan, self.note)                 
                if self.errmsg:
                    return self.returnResult('FAIL', self.errmsg)
                to_vlan += 1 
                time.sleep(2)
        #Create unknown tpyes of rule: 16
        to_vlan = 20
        for from_vlan in range(10, 56):
            (v, self.errmsg) = bg.new_services_rule(self.zdcli, '_other-test._tcp.', from_vlan, to_vlan, self.note)                 
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            to_vlan += 1 
            time.sleep(2)  
               
        if bg.get_rule_nums(self.zdcli) == 256:
            self.passmsg = 'Create 256  services rules successfully.'
        else:
            return self.returnResult('FAIL', 'The services rules num is not 256.')
            
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass
    

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
            note = 'Num:128 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                         )
        
        self.conf.update(conf) 
        self.note = self.conf['note']       
                
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass
    
