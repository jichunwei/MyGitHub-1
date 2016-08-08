'''
Description:

   remove wlan group according wlan group name
   by:west
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Remove_Wlan_Group(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.wg_name=self.conf['wg_name']
        self.zd = self.testbed.components['ZoneDirector']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        lib.zd.wgs.del_wlan_group(self.zd, self.wg_name)
        return 'PASS','remove wlan successfully'
    
    def cleanup(self):
        pass