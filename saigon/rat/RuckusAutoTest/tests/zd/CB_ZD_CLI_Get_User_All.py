'''
Created on 2010-11-5
@author: serena.tan@ruckuswireless.com

Description: This script is used to get a dictionary of all users from ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Get_User_All(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getUserAll()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _getUserAll(self):
        try:
            self.all_user = user.get_user_all(self.zdcli)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        self.passmsg = 'Get the information of all users from ZD CLI successfully'
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_all_users_dict'] = self.all_user