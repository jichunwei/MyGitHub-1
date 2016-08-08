'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the AAA server's configuration in ZD CLI with ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas


class CB_ZD_CLI_Verify_AAA_Server_Cfg_In_GUI(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAAAServerCfgInGUI()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_cfg_dict = conf['aaa_server_cfg']
        self.gui_info_dict = self.carrierbag['zdgui_server_info_list'][0]
        self.errmsg = ''
        self.passmsg = ''

    def _verifyAAAServerCfgInGUI(self):
        logging.info('Verify the AAA server configuration in ZD GUI')
        try:
            res, msg = cas.verify_cli_cfg_in_gui(self.cli_cfg_dict, self.gui_info_dict)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
