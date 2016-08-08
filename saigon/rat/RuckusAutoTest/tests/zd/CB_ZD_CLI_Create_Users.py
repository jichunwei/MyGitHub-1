'''
Created on 2010-12-23
@author: serena.tan@ruckuswireless.com

Description: This script is used to create users in ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Create_Users(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._createUsers()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.user_cfg = {'name': '', 'fullname': '', 'role': '', 'password': '', 'number': 1}
        self.user_cfg.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _createUsers(self):
        try:
            res = user.create_user(self.zdcli, self.user_cfg['name'], self.user_cfg['fullname'], self.user_cfg['role'],
                                        self.user_cfg['password'], self.user_cfg['number'])
            
        except Exception, ex:
            self.errmsg = ex.message
        
        if not self.errmsg:
            if not res:
                self.errmsg = 'Fail to create users in ZD CLI'
            
            else:
                self.passmsg = 'Create users in ZD CLI successfully: %s' % self.user_cfg
