'''
Created on 2013-10-08
@author: ye.songnan@odc-ruckuswireless.com
description:
    Browse bonjour services.
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import bonjour_gateway as bg

class CB_Station_Browse_Bonjour_Service(Test):
    '''
    Browse bonjour services.

        C:\Users\lab>dns-sd -B _ruckus-zd._tcp.
        Browsing for _ruckus-zd._tcp.
        Timestamp     A/R Flags if Domain                    Service Type              I
        nstance Name
        21:30:02.070  Add     3 13 local.                    _ruckus-zd._tcp.          RuckusController
        21:30:02.070  Add     2 13 local.                    _ruckus-zd._tcp.          ruckus
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
        bonjour_record_list = self.target_station.browse_bonjour_service(self.serv_type)        

        if bonjour_record_list == '[]':
            if self.tag_null:
                self.errmsg = ''
            else:
                self.errmsg = 'Should browse service [%s], but nothing can be browsed.' %self.serv_type       
        else:
            for record in eval(bonjour_record_list):
                logging.info('Add %s' %record['name'])                                             
                               
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass
    

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = 'Browse bonjour services successfully.'
        self.conf = dict(
                         service_name= "AirPlay",
                         port = 40000,
                         tag_null = False
                         )
        
        self.conf.update(conf)
        self.tag_null = self.conf['tag_null']
        self.service_name = self.conf['service_name']        
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']        
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass

