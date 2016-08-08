'''
Description:
    show station information on ZDCLI use command 'show station all'.
Created on 2010-10-12
@author: louis.lou@ruckuswireless.com
'''

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as cli


class CB_ZD_CLI_Show_SR(Test):
    '''
    ZD CLI: config-sys-smart-redundancy)#show.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):  
        self.sr_info_on_cli = self._show_sr_info(self.zdcli)
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        self.passmsg = "show SR return: \n %s"  % self.sr_info_on_cli
        
        self._update_carrier_bag()

        return self.returnResult("PASS", self.passmsg)
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        
        self.conf['zdcli'] = 'zdcli1'
        self.conf.update(conf)
        
        self.zdcli = self.carrierbag[self.conf['zdcli']]
        
        self.passmsg = ""
        self.errmsg = ""
    
    def _update_carrier_bag(self):
        self.carrierbag['sr_info_on_cli'] = self.sr_info_on_cli
    
    def _show_sr_info(self,zdcli):
        logging.info('Show Smart Redundancy Information')
        
        sr_info_on_cli = cli.show_sr_info(zdcli)
        logging.info('Smart Redundancy information on CLI is: \n%s' % sr_info_on_cli)
        return sr_info_on_cli
            