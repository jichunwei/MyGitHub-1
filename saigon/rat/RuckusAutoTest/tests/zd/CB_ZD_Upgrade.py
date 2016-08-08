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

import os
import re
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient


class CB_ZD_Upgrade(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'':''}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyUpgradeZDSW()
        #Chico@2014-8-25, fix bug of ZF-9797
        if not self.errmsg:
            logging.info('zd upgrade successfully,try to relogin zdcli')
        else:
            raise Exception('zd upgrade fails with error %s' % self.errmsg)
        #Chico@2014-8-25, fix bug of ZF-9797
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
        elif self.carrierbag.has_key('target_build_file') and self.carrierbag['target_build_file']:
            self.conf['image_file_path'] = self.carrierbag['target_build_file']
        else:
            pass
            
        if self.conf.has_key('build') and self.conf['build']=='target':
            if self.carrierbag.has_key('upgrade_keep'):
                self.conf['keep']=self.carrierbag['upgrade_keep']
            else:
                self.conf['keep']=120
        else:
            self.conf['keep']=2
        
        logging.info('upgrade img is :%s' % self.conf['image_file_path'])
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
        self.zdcli=self.testbed.components['ZoneDirectorCLI']
        if self.carrierbag.has_key('active_zd'):
            self.zdcli=self.carrierbag['active_zd_cli']
            self.zdcli2=self.carrierbag['standby_zd_cli']
        self.ap_mac_list=self.testbed.ap_mac_list
        self.errmsg = ''
        self.passmsg = ''

    def _verifyUpgradeZDSW(self):
        try:
            logging.info('I will keep %d minutes after upgrade'%self.conf['keep'])
            self.zd.upgrade_sw(filename = self.conf['image_file_path'],
                               force_upgrade = self.conf['force_upgrade'],
                               rm_data_files = False)
            self.passmsg = 'The upgrade process worked successfully'
        except Exception, e:
            self.errmsg = '[Upgrade error]: %s' % e.message
            
        
#deleted by West,download img will be done in another API    
#    def _download_build(self, build_stream, build_number):
#        build_url = build_access.get_build_url(build_stream, build_number)
#
#        if not build_url:
#            errmsg = 'There is not any URL for the build %s.%s'
#            errmsg = errmsg % (build_stream.split('_')[1], build_number)
#            raise Exception(errmsg)
#    
#        return build_access.download_build(build_url)
