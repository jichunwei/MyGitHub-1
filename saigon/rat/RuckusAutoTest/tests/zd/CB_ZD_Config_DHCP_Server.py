# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
enable or disable dhcp server in zd
by west.li
       -
"""

import logging
import copy

from RuckusAutoTest.models import Test


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Config_DHCP_Server(Test):

    def config(self, conf):
        """
        """
        self._initTestParameters(conf)

    def test(self):
        """
        """
        # The ZD DHCP server only works with static IP
        if self.option == 'enable':
            self._testDHCPSerWithStaticIP()
            if self.errmsg:
                return ('FAIL', self.errmsg)

        # Verify for DHCP server WebUI fields
        else:
            self._verifyDHCPSerConfig({})
            if self.errmsg:
                return ('FAIL', self.errmsg)

        return ('PASS', '')

    def cleanup(self):
        """
        """
        pass

    def _testDHCPSerWithStaticIP(self):
        """
        """
        # Setting Zone Director to use static IP
        if '192.168.0' in self.zd_ip:
            self.zd.set_ip_cfg(self.valid_ip_conf)
        else:
            logging.info('ZD is already at static IP')

        # Verify if 'DHCP Server' is visible and could be configured successfully
        self._verifyDHCPSerConfig(self.testing_dhcpser_conf)
        if self.errmsg: return

    def _verifyDHCPSerConfig(self, dhcp_ser_conf, expected = True):
        """
        """
        logging.info('Verify the DHCP Server configuration')
        try:
            self.zd.set_dhcp_server(dhcp_ser_conf)
        except Exception, e:
            if expected:
                logging.info('Configuration Failed! [Incorrect behavior]')
                self.errmsg = e
            else:
                logging.info('Configuration Failed! [Correct behavior]: [%s]' % e)
                self.errmsg = ''
            return
        self.errmsg = ''
        logging.info('Configuration successfully! [%s]' % str(dhcp_ser_conf))

    def _initTestParameters(self, conf):
        """
        """
        self.conf = conf
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_ip = self.zd.ip_addr
        self.option=self.conf['option']


        self.valid_ip_conf = {'ip_addr':self.zd_ip, 'net_mask':'255.255.255.0',
                              'gateway':'192.168.0.253', 'pri_dns':'', 'sec_dns':''}

        if conf.has_key('dhcpser_conf'):
            self.testing_dhcpser_conf = conf['dhcpser_conf']
            
        elif self.option == 'enable':
            
            zd_ip_subsection_list = self.zd_ip.split('.')
            start_ip_subsection_list = copy.copy(zd_ip_subsection_list)
            start_ip_subsection_list[3] = str(int(zd_ip_subsection_list[3]) + 1)
            start_ip = start_ip_subsection_list[0]+'.'+start_ip_subsection_list[1]+'.'+start_ip_subsection_list[2]+'.'+start_ip_subsection_list[3]
                
            self.testing_dhcpser_conf = {'enable': True,'start_ip': start_ip, 'number_ip': 99}
        
        else:
            self.testing_dhcpser_conf = {}


