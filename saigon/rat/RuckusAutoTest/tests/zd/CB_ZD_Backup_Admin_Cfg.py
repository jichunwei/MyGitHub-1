'''
Created on 2011-3-3
@author: serena.tan@ruckuswireless.com

Description: This script is used to backup the admin configuration.

'''


import logging

from RuckusAutoTest.models import Test


class CB_ZD_Backup_Admin_Cfg(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._backupAdminCfg()

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self._updateCarrierbag()

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _backupAdminCfg(self):
        logging.info('Backup the admin configuration.')
        try:
            self.admin_cfg = self.zd.get_admin_cfg()
            self.admin_cfg['admin_pass'] = self.zd.password

            self.admin_cfg['admin_old_pass'] = self.zd.password
            self.admin_cfg['admin_pass1'] = self.zd.password
            self.admin_cfg['admin_pass2'] = self.zd.password

            self.passmsg = 'Backup the admin configuration successfully'

        except Exception, ex:
            self.errmsg = ex.message

    def _updateCarrierbag(self):
        self.carrierbag['bak_admin_cfg'] = self.admin_cfg


