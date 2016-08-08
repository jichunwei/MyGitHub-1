# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
       - auth_ser_cfg_list: authentication server configuration list
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Compare aaa servers between GUI set and get
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Data between gui set and get are same
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import aaa_servers_zd as servers


class CB_ZD_Verify_AAA_Server_GUI_Set_Get(Test):
    required_components = []
    parameters_description = {'auth_ser_cfg_list': 'authentication server configuration list'}
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        logging.debug("GUI Set: %s" % self.set_server_cfg_list)
        logging.debug("GUI get: %s" % self.gui_get_server_list)
        
        self._verify_server_gui_set_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "The servers information are same between GUI set and GUI get"
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.conf = {'auth_ser_cfg_list': []}
        
        self.conf.update(conf)
        
        if type(self.conf['auth_ser_cfg_list']) == list:
            self.set_server_cfg_list = self.conf['auth_ser_cfg_list']
        else:
            self.set_server_cfg_list = [self.conf['auth_ser_cfg_list']]
        
        self.gui_get_server_list = self.carrierbag['zdgui_server_info_list']
         
        self.errmsg = ''
        self.passmsg = ''

    def _verify_server_gui_set_get(self):
        logging.info('Verify the AAA server settings between GUI set and GUI get')
        try:
            err_msg = servers.verify_server_cfg_gui_set_get(self.set_server_cfg_list, self.gui_get_server_list)
            if err_msg:
                self.errmsg = err_msg
            
        except Exception, ex:
            self.errmsg = ex.message