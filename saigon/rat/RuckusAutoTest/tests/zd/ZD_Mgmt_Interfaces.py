'''
ZD Manageability
7.2 Combination Test
7.2.1    Originial MGMT Interface - Manual and DHCP
7.2.2    Originial MGMT Interface with VLAN tagging
7.2.3    Additional MGMT Interface - Manual
7.2.4    Additional MGMT Interface with VLAN tagging


Implementation:


config:
. params:
  . ip_cfg | ami_cfg
  . zd_mgmt


test:
. config the ip_cfg | ami_cfg
. config zd_mgmt
. make sure new webpage can be launched and logged in
  . pass/fail is determined here

clean up:
. re-set the ip_cfg | ami_cfg to default
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_zd_by_ip_addr


class ZD_Mgmt_Interfaces(Test):

    def config(self, conf):
        '''
        . removing all mgmt access ctrl
        '''
        self.zd = self.testbed.components['ZoneDirector']
        self.l3sw = self.testbed.components['L3Switch']
        
        self.p = conf
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)


    def test(self):
        '''
        . first config the ip_cfg or ami_cfg
        . then create the mgmt access ctrl
        '''
        logging.info('Configuring the IP Management Settings')
        if 'ip_cfg' in self.p:
            lib.zd.sys.set_device_ip_settings(self.zd, self.p['ip_cfg'], 'ipv4', self.l3sw)
            if 'ip_addr' in self.p['ip_cfg']:
                # manual case
                ip_addr = self.p['ip_cfg']['ip_addr']
            else:
                # dhcp case
                ip_addr = self.zd.conf['ip_addr']
        else:
            lib.zd.sys.set_additional_mgmt_if(self.zd, self.p['ami_cfg'])
            ip_addr = self.p['ami_cfg']['ami_ip_addr']

        # TODO: reboot or re-navigate is needed here??!

        logging.info('Creating a ZD Management Access Control')
        lib.zd.sys.create_mgmt_access_ctrl(self.zd, self.p['zd_mgmt'])

        time.sleep(10)
        self.zd.re_navigate()

        return self._test_launch_webui(ip_addr)


    def cleanup(self):
        '''
        . remove all the mgmt access ctrl
        '''
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)
        self._reset_ip_settings()

        self.zd.re_navigate()


    def _test_launch_webui(self, ip_addr):
        try:
            zd = create_zd_by_ip_addr(ip_addr)
            zd.destroy()
        except:
            return ['FAIL', 'Unable to launch ZD web UI']

        return ['PASS', 'Management Access Control is created successfully']


    def _reset_ip_settings(self):
        if 'ip_cfg' in self.p:
            lib.zd.sys.set_device_ip_settings(self.zd, dict(ip_alloc='dhcp'), 'ipv4', self.l3sw)
        else:
            lib.zd.sys.enable_additional_mgmt_if(self.zd, enabled = False)
