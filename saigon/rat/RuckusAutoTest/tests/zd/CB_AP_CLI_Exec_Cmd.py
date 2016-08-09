# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: yin.wenling

"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import systemgroup

class CB_AP_CLI_Exec_Cmd(Test):
    required_components = ['AP']
    parameters_description = {'ap_tag': 'Access point tag',
                              'cmd_text' : 'The command to be executed',
                              'cmd_pmt' : 'The command prompt',
                              'force_ssh' : 'The Flag of using ssh to login the AP',
                              'expect_value':'The Value expected'
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            for active_ap in self.active_ap_list:
                ap_mac = active_ap.base_mac_addr
                
                logging.info("Execute command in AP CLI for %s" % ap_mac)
                res, msg = systemgroup.exec_command(active_ap,self.cmd_text,self.cmd_pmt,self.force_ssh,self.expect_value)                
                if not res: 
                    self.errmsg = msg
                                        
        except Exception, e:
            self.errmsg = "Fail to execute support command: [%s]" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Execute command correctly"            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(ap_tag = '', #or ['ap1', 'ap2']
                         cmd_text = '',
                         cmd_pmt = "",
                         force_ssh = False,
                         expect_value = ''
                         )
        
        self.conf.update(conf)
        self.cmd_text = self.conf['cmd_text']
        self.cmd_pmt = self.conf['cmd_pmt']
        self.force_ssh = self.conf['force_ssh']
        self.expect_value = self.conf['expect_value']
        ap_tag = self.conf['ap_tag']        
        self.active_ap_list = []
        if ap_tag:
            if type(ap_tag) != list:
                ap_tag_list = [ap_tag]
            else:
                ap_tag_list = ap_tag
                
            for aptag in ap_tag_list:
                self.active_ap_list.append(self.carrierbag[aptag]['ap_ins'])
        else:
            #If no ap_tag is specified, will set all ap as specified values.
            self.active_ap_list = self.testbed.components['AP']
            
        self.errmsg = ''
        self.passmsg = ''
