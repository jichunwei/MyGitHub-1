'''
Created on 2013-10-08
@author: ye.songnan@odc-ruckuswireless.com
description:
    Register a bonjour service.
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import bonjour_gateway as bg

class CB_Station_Register_Bonjour_Service(Test):
    '''
    Register a bonjour service.
       
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        dict_names_types = bg.map_names_types()
        if self.service_name in dict_names_types.keys():
            self.serv_type = dict_names_types[self.service_name]
        else:
            self.serv_type = '_other-test._tcp.'
        self.errmsg = self.target_station.register_bonjour_service(self.service_name, self.serv_type, self.port)           
                               
        if self.errmsg != 'None':
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass
    

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = 'Register bonjour service successfully.'
        self.conf = dict(
                         service_name= "AirPlay",
                         port = 40000
                         )
        
        self.conf.update(conf)
        self.service_name = self.conf['service_name']
        self.port = self.conf['port']
        
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']        
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass
        #self.carrierbag['service_name_list'] = self.serv_name_list

