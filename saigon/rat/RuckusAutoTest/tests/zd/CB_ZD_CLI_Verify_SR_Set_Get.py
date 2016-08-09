'''
Created on 2011-2-15
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr


class CB_ZD_CLI_Verify_SR_Set_Get(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        cli_set = self.sr_conf        
        cli_get = sr.show_sr_info(self.zdcli)
        
        logging.info("Verify CLI Set and CLI Get")
        if 'Peer IP/IPv6 Address' in cli_get['Smart Redundancy']:            
            tgt_info = cli_get['Smart Redundancy']['Peer IP/IPv6 Address']
        else:
            tgt_info = cli_get['Smart Redundancy']['Peer IP Address']
            
        if cli_set['peer_ip_addr'] != tgt_info:
            self.errmsg = "FAIL, Get Peer IP Address:[%s] expect Set:[%s]" % (cli_get['Smart Redundancy']['Peer IP Address'],cli_set['peer_ip_addr'])
    
        if cli_set['secret'] != cli_get['Smart Redundancy']['Shared Secret']:
            self.errmsg = "SR Config secret is [%s] and CLI Get is [%s]" %(cli_set['secret'],cli_get['Smart Redundancy']['Shared Secret'])
             
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
                         sr_conf = {}
                         )
        
        self.conf.update(conf)
        self.sr_conf = conf['sr_conf']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         