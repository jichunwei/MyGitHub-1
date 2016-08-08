"""
chen.tao 2015-01-06
"""

import logging

from RuckusAutoTest.models import Test

class CB_SW_Add_Port_To_Isolate_Group(Test):
    required_components = ['L3Switch']
    parameter_description = {}

    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        component = None
        if not self.conf['tag']:
            component = self.testbed.components['ZoneDirector']
            
        else:
            if 'zd' in self.conf['tag']:
                component = self.carrierbag[self.conf['tag']]
            else:
                component = self.carrierbag[self.conf['tag']]['sta_ins']
        if not component:
            return self.returnResult("FAIL", "Unable to get component.")
        self.add_port_to_isolate_group(component,self.conf['group_id'])

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
        self.conf = {'tag':'',
                     'group_id':'1'
                     }        
        self.errmsg = ''
        self.passmsg = ''
        self.conf.update(conf)
        self.switch = self.testbed.components["L3Switch"]

    def add_port_to_isolate_group(self,component,group_id):

        try:
            eth_mac = component.eth_mac
            port = self.switch.mac_to_interface(eth_mac)
            if not eth_mac or not port or not group_id:
                raise Exception('Error,lease check the eth_mac,port or group_id.')
            self.switch.add_port_to_isolate_group(port,group_id)            
            ports = self.switch.get_port_isolate_group(group_id)
            if not port in ports:
                raise Exception('Port %s should be in isolate group %s, but actually not.'%(port,group_id))
            else:
                self.passmsg = 'Adding port to isolate group successfully.'
        except Exception, ex:
            self.errmsg = ex.message   