'''
Created on 2010-11-5
@author: serena.tan@ruckuswireless.com

Description: This script is used to delete the user from ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Delete_User(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._deleteUserByName()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.name = conf['name']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _deleteUserByName(self):
        try:
            user.delete_user(self.zdcli, self.name)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        self.passmsg = 'Delete user [%s] from ZD CLI successfully' % self.name
            
