'''
Created on Dec 15, 2014

@author: chen.tao@odc-ruckuswireless.com
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import vlan_pooling as vp

class CB_ZD_CLI_Add_Vlan_Pool(Test):

    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        pool_num = vp.get_vlan_pool_num(self.zdcli)
        logging.info('Before operation, vlan pool num is %s'%pool_num)
        res, value = vp.cfg_vlan_pool(self.zdcli, self.vlan_pool_cfg)
        time.sleep(2)
        pool_list = vp.get_vlan_pool_list(self.zdcli)
        logging.info('After operation, vlan pool num is %s'%len(pool_list))
        if len(pool_list) == pool_num:
            if self.conf['operation_type'] != 'edit':
                self.errmsg += 'Vlan pool num did not change after operation. '
        if not res:
            self.errmsg += value
        if self.conf['negative']: 
            if self.errmsg:
                return self.returnResult('PASS', self.errmsg)
            else:
                self.passmsg = 'Adding vlan pool succeeded!'
                return self.returnResult('FAIL', self.passmsg)
        else:
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            else:
                self.passmsg = 'Adding vlan pool succeeded!'
                return self.returnResult('PASS', self.passmsg)               
            

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         vlan_pool_cfg = {},
                         operation_type = '',
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

