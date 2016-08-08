'''
Created on 2011-2-15
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd as sr_zd


class CB_ZD_CLI_Verify_SR_Set_GUIGet(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        cli_set = self.sr_conf
        gui_get = sr_zd.get_sr_info(self.zd)
        
        if cli_set['peer_ip_addr'] != gui_get['Peer IP Address']:
            self.errmsg = "FAIL, [CLISet]: Peer IP Address is [%s] but GUI Get is [%s]" %(cli_set['peer_ip_addr'],gui_get['Peer IP Address'])
    
        if cli_set['secret'] != gui_get['Shared Secret']:
            self.errmsg = "FAIL, [CLISet]: Secret is [%s] but GUIGet is [%s]" %(cli_set['secret'],gui_get['Shared Secret'])
        
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
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         