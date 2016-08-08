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

class CB_LinuxPC_Config_DHCP_Server_Option(Test):
    required_components = ['LinuxPC']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._conf_dhcp_server_option()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
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
        self.conf = {'option_list': [],
                     'start_server': True,
                     'server_info': {}
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
            self.server = self.testbed.components['LinuxServer']
                        
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrierbag(self):
        pass
    
    def _conf_dhcp_server_option(self):
        func_map = {'option 15': self.server.set_dhcp_option_15,
                    'option 43': self.server.set_dhcp_option_43}
        action_map = {'enable': True,
                      'disable': False}
        
        for option in self.conf['option_list']:
            msg = 'On DHCP server %s %s' % (option['action'], option['name'])
            logging.info(msg)
            try:
                func_map[option['name']](action_map[option['action']])
                msg = '%s successfully' % msg
            except:
                self.errmsg = '%s failed!' % msg
    
    def _execute_dhcp_service(self):        
        if self.conf['start_server']:
            msg = 'Start the DHCP server'
            logging.info(msg)
            try:
                self.server.restart_dhcp_server()
            except:
                time.sleep(5)
                try:
                    self.server.restart_dhcp_server()
                except Exception, e:
                    self.errmsg = '%s failed! %s' % (msg, e.message)
        else:
            msg = 'Stop the DHCP server'
            logging.info(msg)
            try:
                self.server.stop_dhcp_server()
            except:
                time.sleep(5)
                try:
                    self.server.stop_dhcp_server()
                except Exception, e:
                    self.errmsg = '%s failed! %s' % (msg, e.message)