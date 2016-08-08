'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the user's configuration in ZD CLI with ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user


class CB_ZD_CLI_Verify_User_Cfg_In_GUI(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyUserCfgInGUI()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_cfg_dict = conf['user_cfg']
        self.gui_info_dict = self.carrierbag['zdgui_user_dict']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyUserCfgInGUI(self):
        logging.info('Verify the user configuration in ZD GUI')
        try:
            res, msg = user.verify_user_cfg_in_gui(self.cli_cfg_dict, self.gui_info_dict)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
