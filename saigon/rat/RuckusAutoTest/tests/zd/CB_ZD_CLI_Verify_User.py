'''
Created on 2010-12-23
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify whether the information of a user in ZD CLI is the same as in ZD GUI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Verify_User(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyUserByGUI()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_user_dict = self.carrierbag['zdcli_user_dict']
        self.gui_user_dict = self.carrierbag['zdgui_user_dict']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyUserByGUI(self):
        try:
            res = user.verify_user_by_gui(self.cli_user_dict, self.gui_user_dict)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        if not self.errmsg:
            if not res:
                self.errmsg = 'The information of user shown in ZD CLI is not the same as in ZD GUI'
            
            else:
                self.passmsg = 'The information of user shown in ZD CLI is the same as in ZD GUI'

