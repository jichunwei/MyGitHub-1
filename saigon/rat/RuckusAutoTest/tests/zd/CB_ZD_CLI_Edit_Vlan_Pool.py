'''
Created on Dec 15, 2014

@author: chen.tao@odc-ruckuswireless.com
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import vlan_pooling as vp

class CB_ZD_CLI_Edit_Vlan_Pool(Test):

    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        res, value = vp.edit_vlan_pool(self.zdcli, self.vlan_pool_cfg)
        if not res:
            self.errmsg += value
        if self.conf['negative']: 
            if self.errmsg:
                return self.returnResult('PASS', self.errmsg)
            else:
                self.passmsg = 'Editing vlan pool succeeded!'
                return self.returnResult('FAIL', self.passmsg)
        else:
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            else:
                self.passmsg = 'Editing vlan pool succeeded!'
                return self.returnResult('PASS', self.passmsg)               
            

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        '''
        vlan_pool_cfg = {'name':"vlan_pool_eap_test",
                         'new_name':'',
                         'add_vlan':'302',
                         'del_vlan':'100',
                         'new_description':'',
                         'new_option':'',}
        '''
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         vlan_pool_cfg = {},
                         negative = False
                         )
        
        self.conf.update(conf)
             
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
        self.vlan_pool_cfg = self.conf['vlan_pool_cfg']

    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass

