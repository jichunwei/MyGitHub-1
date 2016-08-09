'''
Created on 2011-3-3
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure admin in ZD CLI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_admin as adm


class CB_ZD_CLI_Configure_Admin(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._configureAdmin()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.admin_cfg = conf['admin_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _configureAdmin(self):
        try:
            res, msg = adm.configure_admin(self.zdcli, self.admin_cfg)
            self.zdcli.username = self.admin_cfg.get('admin_name')
            self.zdcli.password = self.admin_cfg.get('admin_pass')
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message