'''
Created on 2011-2-16
@author: louis.lou@ruckuswireless.com
description:

'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import mgmt_interface_info as mgmt

class CB_ZD_CLI_Verify_MGMT_IF_No_Vlan(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        mgmt_info_cli = mgmt.show_mgmt_if_info(self.zdcli)
        mgmt.verify_no_mgmt_if_info(mgmt_info_cli)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         