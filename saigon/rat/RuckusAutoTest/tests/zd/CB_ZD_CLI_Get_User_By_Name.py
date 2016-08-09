'''
Created on 2010-11-5
@author: serena.tan@ruckuswireless.com

Description: This script is used to get a dictionary of the user information from ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Get_User_By_Name(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getUserByName()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.name = conf['name']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _getUserByName(self):
        try:
            self.user_info = user.get_user_by_name(self.zdcli, self.name)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        self.passmsg = 'Get the information of user [%s] from ZD CLI successfully' % self.name
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_user_dict'] = self.user_info