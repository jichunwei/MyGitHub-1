# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Aprial 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'L3Switch'
   Test parameters:
       - 'is_ipv6_server': 'if true, get ipv6 server from test bed components, else get ipv4 server',
       - 'is_start_server': 'if true, start dns server; false, stop dns server',
       - 'dns_service_name': 'dns service name, default is "dnsmasq"'
        
   Test procedure:
    1. Config:
        - initialize test parameters
        - Get ipv4 or ipv6 server from testbed components.
    2. Test:
        - start or stop DNS service on server
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: DNS is start or stop successfully. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from RuckusAutoTest.models import Test

class CB_ZD_Start_Stop_DNS_On_Server(Test):
    required_components = ['L3Switch']
    parameters_description = {'is_ipv6_server': 'if true, get ipv6 server from test bed components, else get ipv4 server',
                              'is_start_server': 'if true, start dns server; false, stop dns server',
                              'dns_service_name': 'dns service name, default is "dnsmasq"'}
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        try:
            if self.is_start_server:
                logging.info("Start DNS service on server %s" % (self.server.ip_addr))
                if self.dns_service_name:
                    self.server.start_dns_server(self.dns_service_name)
                else:
                    self.server.start_dns_server()
            else:
                logging.info("Stop DNS service on server %s" % (self.server.ip_addr))
                if self.dns_service_name:
                    self.server.stop_dns_server(self.dns_service_name)
                else:
                    self.server.stop_dns_server()
        except Exception, ex:
            self.errmsg = "Error:%s" % ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrierbag()
            msg = 'Start or stop DNS server successfully'
            return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        self.conf = {'is_ipv6_server': False,
                     'is_start_server': True,
                     'dns_service_name': 'named'}
        
        self.conf.update(conf)
        
        self.is_start_server = self.conf['is_start_server']
        self.dns_service_name = self.conf['dns_service_name']
        
        if self.conf['is_ipv6_server']:            
            self.server = self.testbed.components['LinuxServerIPV6']
        else:
            self.server = self.testbed.components['LinuxServer']
            
        self.errmsg = ''
        
    def _update_carrierbag(self):
        pass      