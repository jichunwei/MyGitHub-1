'''
Created on 2010-12-23
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify whether the information of all users in ZD CLI is the same as in ZD GUI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Verify_User_All(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyAllUsersByGUI()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_info_dict = self.carrierbag['zdcli_all_users_dict']
        self.gui_info_list = self.carrierbag['zdgui_all_users_list']
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyAllUsersByGUI(self):
        try:
            res = user.verify_all_user_by_gui(self.cli_info_dict, self.gui_info_list)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        if not self.errmsg:
            if not res:
                self.errmsg = 'The information of all users shown in ZD CLI is not the same as in ZD GUI'
            
            else:
                self.passmsg = 'The information of all users shown in ZD CLI is the same as in ZD GUI'
