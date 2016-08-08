'''
Created on 2011-2-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the AP's information in ZD CLI with ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_ap


class CB_ZD_CLI_Verify_AP_Cfg_With_GUI(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAPsWithGUI()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_cfg = self.carrierbag['zdcli_ap_cfg']
        self.gui_info = self.carrierbag['zdgui_ap_info']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyAPsWithGUI(self):
        logging.info('Verify the configuration of AP in ZD CLI with ZD GUI')
        try:
            res, msg = configure_ap.verify_ap_cli_cfg_in_gui(self.cli_cfg, self.gui_info)
            if res:
                self.passmsg = "The configuration of AP is correct in ZD GUI"
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
