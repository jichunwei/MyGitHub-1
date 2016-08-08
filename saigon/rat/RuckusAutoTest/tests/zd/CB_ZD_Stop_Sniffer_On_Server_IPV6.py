# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Nov 2011

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

from RuckusAutoTest.models import Test

class CB_ZD_Stop_Sniffer_On_Server_IPV6(Test):
    required_components = ['LinuxServerIPV6']
    parameters_description = {}

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        try:
            if self.is_sniffing:
                logging.info('Stop Sniffer on Server [%s]' % self.acct_svr_ip_addr)
                self._stop_sniffer_server()()
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = 'Stop Sniffer on Server [%s] Successfully' % self.acct_svr_ip_addr
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf = {'server_tag': 'linuxserver',
                     'svr_ip_addr': '2020:db8:1::251'}
        self.conf.update(conf)
        
        carrier_bag_server_tag = self.conf['server_tag']
        self.accounting_server = carrier_bag_server_tag['server_ins']
        self.acct_svr_ip_addr = self.conf['svr_ip_addr']
        
        if carrier_bag_server_tag.has_key('sniffer_enable'):
            self.is_sniffing = carrier_bag_server_tag['sniffer_enable']
        else:
            self.is_sniffing = False
        
        self.errmsg = ''
    
    def _update_carrier_bag(self):
        self.carrierbag[self.conf['server_tag']]['sniffer_enable'] = self.is_sniffing
        
    def _stop_sniffer_server(self):
        self.accounting_server.stop_sniffer()
        self.is_sniffing = False