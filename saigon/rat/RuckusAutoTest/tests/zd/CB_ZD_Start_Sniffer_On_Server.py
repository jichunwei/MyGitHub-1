# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: chris.wang
   @contact: chris.wang@ruckuswireless.com
   @since: Oct. 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Start sniffer server in ipv6 server.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Start sniffer server successfully. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.models import Test

class CB_ZD_Start_Sniffer_On_Server(Test):
    required_components = ['LinuxPC']
    parameters_description = {}

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        try:
            self.is_sniffing = False
            logging.info('Start Sniffer on Server [%s]' % self.acct_svr_ip_addr)
            self._start_sniffer_on_server()
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = 'Start Sniffer on Server [%s] Successfully' % self.acct_svr_ip_addr
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.accounting_server = self.testbed.components['LinuxServer']
        self.acct_svr_ip_addr = self.accounting_server.ip_addr
        
        self.errmsg = ''
    
    def _update_carrier_bag(self):
        self.carrierbag['sniffer_enable'] = self.is_sniffing
        
    def _start_sniffer_on_server(self):        
        ip_type = const.IPV4
        server_interface = self.accounting_server.get_interface_name_by_ip(self.acct_svr_ip_addr, ip_type = ip_type)
        self.accounting_server.start_sniffer("-i %s udp" % (server_interface))
        self.is_sniffing = True