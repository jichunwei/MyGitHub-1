'''
Created on 2010-6-25

@author: louis.lou@ruckuswireless.com
'''
#import os
#import re
import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_SR_Select_Active_Upgrade(Test):
    '''
    Check the ZD's version, if zd's version is the same as expected, return PASS

    else return FAIL
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)

    def test(self):
        if self.check_version(self.active_zd):
            self.passmsg = 'The ZD %s was Upgraded' % self.active_zd.ip_addr
        else:
            self._click_upgrade_local_button(self.active_zd)
            logging.info("Waiting for the ZD %s upgrading", self.active_zd.ip_addr)
            time.sleep(300)
            self.active_zd.refresh()
            self.active_zd._check_upgrade_sucess()
            self.active_zd.login()

        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        pass



    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         zd_type = 'standby',
                         expect_version = ''
                         )

        self.conf.update(conf)

        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        self.expect_version = self.conf['expect_version']

    def check_version(self,zd):
        zd.refresh()
        zd.navigate_to(zd.ADMIN, zd.ADMIN_PREFERENCE)

        version = zd._get_version()
        current_version = version['version']
        if current_version == self.expect_version:
            logging.info( 'The current version %s and the expect version are same' % current_version)
            return True
        else:
            logging.info( 'The current version % s was not the expect version %s' % (current_version,self.expect_version))
            return False
    def _click_upgrade_local_button(self,zd):
        red.click_upgrade_from_local_zd(zd)

