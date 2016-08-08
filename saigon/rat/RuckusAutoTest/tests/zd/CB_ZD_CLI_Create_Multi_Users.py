'''
Created on 
@author: 

Description: This script is used to create users in ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Create_Multi_Users(Test):
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
        self.user_cfg = dict(
                         user_cfg_list =[],
                         )
        
        self.user_cfg.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _createUsers(self):
        for user_conf in self.user_cfg['user_cfg_list']:
            try:
                res = user.create_user(self.zdcli, 
                                       user_conf['username'], 
                                       user_conf['fullname'], 
                                       user_conf['role'],
                                       user_conf['password'])
                
            except Exception, ex:
                self.errmsg = ex.message
            
            if not self.errmsg:
                if not res:
                    self.errmsg = 'Fail to create users in ZD CLI'
                
                else:
                    self.passmsg = 'Create users in ZD CLI successfully: %s' % user_conf
