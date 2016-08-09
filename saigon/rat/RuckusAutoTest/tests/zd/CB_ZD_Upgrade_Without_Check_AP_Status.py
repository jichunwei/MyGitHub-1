# Copyright (C) 2013 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This case is for upgrading ZD image, but not checking AP status.
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
"""

import os
import re
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient


class CB_ZD_Upgrade_Without_Check_AP_Status(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'':''}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyUpgradeZDSW()
        
        # added by west.li after upgrade login zdcli
        if self.carrierbag.has_key('active_zd'):
            try:
                self.zdcli2.do_shell_cmd('')
            except:
                self.zdcli2.zdcli = sshclient(self.zdcli2.ip_addr, self.zdcli2.port,'admin','admin')
                self.zdcli2.login()
                
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
            
        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        # the 'image_file_path': is the path of the *.gz file that contain the image of the ZD.
        self.conf = {'force_upgrade':False}
        self.conf.update(conf)
        
        if self.conf.has_key('build') and self.conf['build']=='base':
            self.conf['image_file_path'] = self.carrierbag['base_build_file']
        else:
            self.conf['image_file_path'] = self.carrierbag['target_build_file']
        
        logging.info('upgrade img is :%s' % self.conf['image_file_path'])
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
            self.zdcli=self.carrierbag['active_zd_cli']
            self.zdcli2=self.carrierbag['standby_zd_cli']
        else:
            self.zd = self.testbed.components['ZoneDirector']
            self.zdcli=self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyUpgradeZDSW(self):
        try:
            self.zd.upgrade_sw(filename = self.conf['image_file_path'],
                               force_upgrade = self.conf['force_upgrade'],
                               rm_data_files = False)
            self.passmsg = 'The upgrade process worked successfully'
        except Exception, e:
            self.errmsg = '[Upgrade error]: %s' % e.message