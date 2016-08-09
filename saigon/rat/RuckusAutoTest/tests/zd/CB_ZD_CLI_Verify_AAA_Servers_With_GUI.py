'''
Created on Jan 8, 2011
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the aaa servers' information in ZD CLI with ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas


class CB_ZD_CLI_Verify_AAA_Servers_With_GUI(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAAAServersWithGUI()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_info_list = self.carrierbag['zdcli_server_info_list']
        self.gui_info_list = self.carrierbag['zdgui_server_info_list']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyAAAServersWithGUI(self):
        logging.info('Verify the information of aaa servers in ZD CLI with ZD GUI')
        try:
            res, msg = cas.verify_cli_info_with_gui(self.cli_info_list, self.gui_info_list)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message

