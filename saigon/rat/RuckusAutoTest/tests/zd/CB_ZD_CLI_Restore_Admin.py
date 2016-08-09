'''
Created on 2011-3-3
@author: serena.tan@ruckuswireless.com

Description: This script is used to restore the admin to backup value via ZD CLI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_admin as adm


class CB_ZD_CLI_Restore_Admin(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._restoreAdmin()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.admin_cfg = self.carrierbag['bak_admin_cfg']
        self.errmsg = ''
        self.passmsg = ''

    def _restoreAdmin(self):
        logging.info('Restore the admin configuration to original value via ZD CLI')
        try:
            res, msg = adm.configure_admin(self.zdcli, self.admin_cfg)
            if res:
                self.zd.username = self.admin_cfg['admin_name']
                self.zd.password = self.admin_cfg['admin_pass']
                self.passmsg = 'Restore the admin cfg to original value successfully'
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message

                