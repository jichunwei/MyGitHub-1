'''
Created on 2010-12-23
@author: serena.tan@ruckuswireless.com

Description: This script is used to edit user in ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Edit_User(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._editUser()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.user_cfg = {'user': '', 'name': '', 'fullname': '', 'role': '', 'password': ''}
        self.user_cfg.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _editUser(self):
        try:
            res = user.edit_user(self.zdcli, self.user_cfg['user'], self.user_cfg['name'], self.user_cfg['fullname'], 
                                 self.user_cfg['role'], self.user_cfg['password'])
            
        except Exception, ex:
            self.errmsg = ex.message
            
        if not self.errmsg:
            if not res:
                self.errmsg = 'Fail to edit user [%s] with cfg [%s] in ZD CLI' % (self.user_cfg['user'], self.user_cfg)
            
            else:
                self.passmsg = 'Edit user [%s] with cfg [%s] in ZD CLI successfully' % (self.user_cfg['user'], self.user_cfg)
