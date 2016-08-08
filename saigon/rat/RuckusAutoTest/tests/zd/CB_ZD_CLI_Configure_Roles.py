'''
Created on 2011-3-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure roles in ZD CLI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import roles


class CB_ZD_CLI_Configure_Roles(Test):
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        self._configureRoles()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.role_cfg_list = conf['role_cfg_list']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _configureRoles(self):
        logging.info('Configure roles in ZD CLI')
        try:
            fail_roles = {}
            pass_roles = {}
            for role_cfg in self.role_cfg_list:
                res, msg = roles.configure_single_role(self.zdcli, role_cfg)
                if res:
                    pass_roles.update({role_cfg['role_name']: msg})
                
                else:
                    fail_roles.update({role_cfg['role_name']: msg})
                
            if fail_roles:
                self.errmsg = '%s' % fail_roles
            
            else:
                self.passmesg = '%s' % pass_roles
            
        except Exception, ex:
            self.errmsg = ex.message
            
            