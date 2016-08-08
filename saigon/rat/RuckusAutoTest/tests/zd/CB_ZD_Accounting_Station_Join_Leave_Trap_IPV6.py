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
       'acct_svr_port': 'Accounting server port',
       'acct_enable': 'Wether accounting server is enabled in the wlan',
       'pause': 'Pause time after station associated.'       
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Verify station join and leave trap in radius accounting server: 
            if acct_enable, trap should be sent out;
            else, trap should not be sent out.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Join and trap is/not found in packets. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Accounting_Station_Join_Leave_Trap_IPV6(Test):
    required_components = ['LinuxServerIPV6']
    parameters_description = {'acct_svr_port': 'Accounting server port',
                              'acct_enable': 'Wether accounting server is enabled in the wlan',
                              'pause': 'Pause time after station associated.'
                              }
    
    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        try:
            if self.is_sniffing:
                time.sleep(self.conf['pause'])
                logging.info('Stop sniffer on server')
                self._stop_sniffer_server()

                logging.info('Verify station join and leave trap')
                self._verify_join_leave_trap()
            else:
                self.errmsg = 'Sniffer is not started in server [%s]' % self.acct_svr_ip_addr

        except Exception, ex:
            self.errmsg = ex.message

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf = {'acct_svr_port': '50002',
                     'acct_enable': True,
                     'pause': 2.0}
        self.conf.update(conf)

        self.accounting_server = self.testbed.components['LinuxServerIPV6']
        self.acct_svr_ip_addr = self.accounting_server.ip_addr

        if self.carrierbag.has_key('sniffer_enable'):
            self.is_sniffing = self.carrierbag['sniffer_enable']
        else:
            self.is_sniffing = False

        self.errmsg = ''
        self.passmsg = ''

    def _update_carrier_bag(self):
        self.carrierbag['sniffer_enable'] = self.is_sniffing

    def _stop_sniffer_server(self):
        self.accounting_server.stop_sniffer()
        self.is_sniffing = False

    def _verify_join_leave_trap(self):
        if self.conf['acct_enable']:
            # check trap packets on server
            if len(self._find_account_packets('Value: Start')) == 0:
                self.errmsg = "ZD not sent out trap accounting when client associate to wlan"
            elif len(self._find_account_packets('Value: Stop')) == 0:
                self.errmsg = "ZD not sent out trap accounting when client associate to wlan"
        else:
            if len(self._find_account_packets('Value: Start')):
                self.errmsg = "ZD sent out trap accounting when Accounting server disabled on wlan"

        self.passmsg = "ZD send out trap packet to Accounting Server whenever client join/leave work properly"

    def _find_account_packets(self, search_pattern = '', filter = ''):
        if filter:
            packets_captured = self.accounting_server.read_sniffer(filter)
        else:
            packets_captured = self.accounting_server.read_sniffer("dst port %s" % self.conf['acct_svr_port'])

        acct_trap_packets = []
        for packet in packets_captured:
            if search_pattern in packet:
                acct_trap_packets.append(packet)

        logging.debug(acct_trap_packets)

        return acct_trap_packets
