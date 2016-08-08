# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
            -
   2. Test:
            -

   3. Cleanup:
            -

   How it is tested?
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Constant as const

class CB_ZD_Backup(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'':''}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        
        self._verifyBackupZDConfig()
        if self.errmsg:
            return ('FAIL', self.errmsg)

        if not self.carrierbag.get('bak_files'):
            self.carrierbag['bak_files'] = {}
        self.carrierbag['bak_files'][self.conf['related_bak']] = self.bak_file_path

        self._collectBackupInfo()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'related_bak': 'unspecific',
                     'save_to':'',
                     'zd':''
                     }
        self.conf.update(conf)
        self.conf['save_to'] = const.save_to
        if self.conf['zd']:
            self.zd = self.carrierbag[self.conf['zd']]
        else:
            if 'active_zd' in self.carrierbag:
                self.zd = self.carrierbag['active_zd']
            else:
                self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyBackupZDConfig(self):
        try:
            self.bak_file_path = lib.zd.bkrs.backup(self.zd, save_to = self.conf['save_to'])
            self.passmsg = 'The current configuration of Zone Director is backup at "%s"' % self.bak_file_path
        except Exception, e:
            self.errmsg = '[Backup error]: %s' % e.message

    def _collectBackupInfo(self):
        self.carrierbag['backup_info'] = {}
        backup_info_key = ['existing_wlans_cfg']
        for key in backup_info_key:
            if self.carrierbag.get(key):
                self.carrierbag['backup_info'][key] = self.carrierbag[key]

