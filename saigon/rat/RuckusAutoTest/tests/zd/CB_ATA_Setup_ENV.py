'''
BindPort to veriwave:
    Usage: bindport portName chassis slotNumber portNumber [options]
    Sample:bindPort wifi_01 172.18.110.31 9 4
    
Created on Oct 15, 2013
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import AtaWrapper as AW


class CB_ATA_Setup_ENV(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):        
        self.conf = dict(ports = [{'port_name':self.testbed.wifi_01,
                                   'ip_addr':self.testbed.veriwave_IP,
                                   'slot':self.testbed.wifi_blade_01,
                                   'port':self.testbed.wifi_port_01
                                   },                                   
                                   ],
                         )
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.port_cfgs = self.conf.get('ports')                
        logging.info("====Initialize Params DONE====")
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):   
        for port_cfg in self.port_cfgs:            
            self.ata.bind_vw_port(**port_cfg)
            logging.info('Bind port as parameters %s DONE' % port_cfg)
        
                 
        return self.returnResult('PASS', 'ATA ENV is ready.')
    
    def cleanup(self):
        self._update_carribag()