'''
Created on 2011-3-3
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the ZD CLI admin configuration in ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_admin as adm


class CB_ZD_CLI_Verify_Admin_Cfg_In_GUI(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAdminCfgInGUI()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_cfg = conf['admin_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyAdminCfgInGUI(self):
        try:
            self.gui_info = self.zd.get_admin_cfg()
            
            logging.info('Verify the admin configuration in ZD GUI')
            res, msg = adm.verify_cli_admin_cfg_in_gui(self.cli_cfg, self.gui_info)
            if res:
                self.passmsg = 'Verify the admin configuration in ZD GUI successfully'
            
            else:
                self.errmsg = msg
                
        except Exception, ex:
            self.errmsg = ex.message
            
