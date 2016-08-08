# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: This API is used to verify the START and INTERIM update packets from ZD 
                to accounting server with the IPass (Radius Class attribute) 
   @author: An Nguyen    
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       interim_update - 'Interim update for accounting server',
       acct_svr_port - 'Accounting server port'
              
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Verify interim update between zd and station when accounting is enabled.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Interim update is same as duration between update package. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const

class CB_ZD_Accounting_IPass_Verifying(Test):
    required_components = ['LinuxServer']
    parameters_description = {'acct_ipass_value': 'The expected IPASS of the accounting authenticated user',
                              'acct_svr_port': 'Accounting server port'
                              }

    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        try:
            if self.is_sniffing:
                logging.info('Stop sniffer on server')
                self._stop_sniffer_server()

            logging.info('Verify the IPASS value in the accounting packets')            
            self._verify_acct_ipass_attribute()
            
        except Exception, ex:
            self.errmsg += ex.message

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'acct_svr_addr': '192.168.0.252',
                     'acct_svr_port': '1813',
                     'acct_ipass_value': ''}
        self.conf.update(conf)

        self.accounting_server = self.testbed.components['LinuxServer']

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
    
    def _get_all_accounting_packets(self):
        res = self.accounting_server.read_sniffer("dst port %s" % self.conf['acct_svr_port'], return_as_list=False)
        lines = res.split("\r\n")[2:]
        packets = []
        tmp = ""
        for line in lines:
            packet_entry = False if line.startswith('\t') else True
            if packet_entry:
                if tmp:
                    packets.append(tmp) 
                tmp = line
            else:
                tmp += line
        if packets and tmp != packets[-1]:
            packets.append(tmp)
        
        start_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Start"
        start_re = re.compile(start_pattern)
        stop_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Stop"
        stop_re = re.compile(stop_pattern)
        inter_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Interim-Update"
        inter_re = re.compile(inter_pattern)

        start_packets = [p for p in packets if start_re.search(p)]
        stop_packets = [p for p in packets if stop_re.search(p)]
        inter_packets = [p for p in packets if inter_re.search(p)]
        
        return {'acct-start': start_packets,
                'acct-stop': stop_packets,
                'acct-interim-update': inter_packets}
    
    
    def _verify_acct_ipass_attribute(self):
        acct_packets = self._get_all_accounting_packets()
        
        ipass_pattern = "Class Attribute \(25\), length: [\d]+, Value: ([\w ]+)"
        ipass_re = re.compile(ipass_pattern)
        
        error_packets = {}
        
        for key in acct_packets.keys():
            logging.info('Verify the IPASS info [Class=%s] on %s packets' % (self.conf['acct_ipass_value'], key))
            error_packets[key] = []
            if not acct_packets[key]:
                self.errmsg += 'There is not any %s packet is captured. ' % key
                continue
            for packet in acct_packets[key]:
                ires = ipass_re.search(packet)
                if not ires:
                    error_packets[key].append(packet)
                elif ires.group(1) != self.conf['acct_ipass_value']:
                    logging.debug('The Class value = %s' % ires.group())
                    error_packets[key].append(packet)
        
        for key in error_packets.keys():
            if error_packets[key]:
                self.errmsg += 'The expected IPASS info [Class=%s]is not in %s %s packets' % (self.conf['acct_ipass_value'],
                                                                                              len(error_packets[key]), key)
                debug_msg = 'The expected IPASS info [Class=%s] is not in %s packets: %s' % (self.conf['acct_ipass_value'],
                                                                                             key, error_packets[key])
                logging.debug(debug_msg)
        
        self.passmsg = 'The expected IPASS info [Class=%s] is shown correctly in all accounting packets' % self.conf['acct_ipass_value']