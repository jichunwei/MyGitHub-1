# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Linux PC'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Setting the expected option to DHCP server on Linux PC
        - Verify if the service is running
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_server_by_ip_addr

class CB_LinuxPC_Config_DHCPv6_Server_Option(Test):
    required_components = ['LinuxPC']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._execute_dhcp_service()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = 'The configuration %s are executed successfully' % self.conf
        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        if self.cleanup_server:
            try:
                self.server.close()
            except:
                msg = 'Failed to close the connection to linux server'
                logging.debug(msg)

    def _init_test_params(self, conf):
        self.conf = {'start_server': True,
                     'dhcp_service_name': 'radvd',
                     }
        self.conf.update(conf)
        
        self.cleanup_server = False
        if self.conf.get('server_info'):            
            self.server = create_server_by_ip_addr(ip_addr = self.conf['server_info']['ip_addr'],
                                                   username = self.conf['server_info']['username'],
                                                   password = self.conf['server_info']['password'],
                                                   root_password = self.conf['server_info']['root_password'])
            time.sleep(10)
            self.cleanup_server = True
        else:
            self.server = self.testbed.components['LinuxServerIPV6']
                        
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrierbag(self):
        pass
    
    def _execute_dhcp_service(self):
        if self.conf['dhcp_service_name'] == 'radvd':
            return self._execute_radvd_service()
        elif self.conf['dhcp_service_name'] == 'dhcpd6':
            return self._execute_dhcpd6_service()
    
    def _execute_radvd_service(self):
        if self.conf['start_server']:
            msg = 'Start the radvd server'
            logging.info(msg)
            try:
                self.server.restart_radvd()
            except:
                time.sleep(5)
                try:
                    self.server.restart_radvd()
                except Exception, e:
                    self.errmsg = '%s failed! %s' % (msg, e.message)
        else:
            msg = 'Stop the radvd server'
            logging.info(msg)
            try:
                self.server.stop_radvd()
            except:
                time.sleep(5)
                try:
                    self.server.stop_radvd()
                except Exception, e:
                    self.errmsg = '%s failed! %s' % (msg, e.message)
    
    def _execute_dhcpd6_service(self):
        if self.conf['start_server']:
            msg = 'Start the dhcpd6 server'
            logging.info(msg)
            try:
                self.server.restart_dhcpd6()
            except:
                time.sleep(5)
                try:
                    self.server.restart_dhcpd6()
                except Exception, e:
                    self.errmsg = '%s failed! %s' % (msg, e.message)
        else:
            msg = 'Stop the dhcpd6 server'
            logging.info(msg)
            try:
                self.server.stop_dhcpd6()
            except:
                time.sleep(5)
                try:
                    self.server.stop_dhcpd6()
                except Exception, e:
                    self.errmsg = '%s failed! %s' % (msg, e.message)
    