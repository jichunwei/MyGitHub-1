'''
The ZD_GuestAccess_Common provides a template and common methods for any test class relating to the Guest Access section on the ZD.

@author: Phan Nguyen
@email: phannt@s3solutions.com.vn
'''

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.components import Helpers as lib

class ZD_GuestAccess_Common(Test):

    def config(self, conf):
        self.tc2f = {}

        self.conf = {}

        self._cfgInitTestParams(conf)

        self._cfgRemoveAllConfigOnZD()

        self._cfgCreateWlanOnZD()

        self._cfgAuthServerOnZD()


    def test(self):
        self.tc2f[self.conf['testcase']]()

        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", self.passmsg.strip())

    def cleanup(self):
        #self._cfgRemoveAllConfigOnZD()

        self._cfgRemoveFiles()

        Test.cleanup(self)


    def _cfgInitTestParams(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.station = self.testbed.components['Station']

        self.errmsg = ''
        self.passmsg = ''

        self.filelist = []


    def _cfgRemoveAllConfigOnZD(self):
        logging.info("Remove all WLANs configured on the ZD")
        lib.zd.wlan.delete_all_wlans(self.zd)
        logging.info('Reset to use "Local Database" to generate and authenticate the guest passes')
        self.zd.set_guestpass_policy('Local Database')
        logging.info("Remove all AAA servers configured on the ZD")
        lib.zd.aaa.remove_all_servers(self.zd)
        logging.info("Remove all user")
        self.zd.remove_all_users()
        logging.info("Remove all guest passes")
        lib.zd.ga.delete_all_guestpass(self.zd)


    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] as a Guest Access WLAN on the ZD" % self.wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.wlan_cfg)
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")


    def _cfgAuthServerOnZD(self):
        if self.conf['auth_server_type'] == 'local':
            logging.info('Create user "%s" on the ZD' % self.conf['username'])
            self.zd.create_user(self.conf['username'], self.conf['password'])
            logging.info('Use "Local Database" to generate and authenticate the guest passes')
            self.zd.set_guestpass_policy('Local Database')
        elif self.conf['auth_server_type'] in ['radius', 'ad', 'ldap']:
            logging.info('Create an %s server on the ZD' % self.conf['auth_server_type'].upper())
            lib.zd.aaa.create_server(self.zd, **self.conf['auth_server_info'])
            msg = 'Use "%s Server" to generate and authenticate the guest passes'
            msg = msg % self.conf['auth_server_type'].upper()
            logging.info(msg)
            self.zd.set_guestpass_policy(self.conf['auth_server_info']['server_name'])
        else:
            errmsg = 'Do not support to test with  "%s" authentication server'
            errmsg = errmsg % self.conf['auth_server_type'].upper()
            raise Exception(errmsg)


    def _cfgRemoveFiles(self):
        for afile in self.filelist:
            if afile:
                os.remove(afile)



