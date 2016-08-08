"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
             -'check_list': {'acct-start':True,'acct-stop':True, 'acct-interim-update':True}
             -'acct_svr_port' : '' 
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - read the packet and check the check_value is exist    
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get or set max lease time success and restart DHCP server success
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import re
import time
from RuckusAutoTest.models import Test

class CB_Server_Verify_Accounting_Packets(Test):
    required_components = ['LinuxServer']
    parameters_description = {'check_list': {'acct-start':True,'acct-stop':True, 'acct-interim-update':True},
                              'acct_svr_port' : ''}
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            logging.info('Verify accounting packets')
            time.sleep(5) #Make sure the packet is generated
            self._verify_acct_ipass_attribute()
        except Exception, ex:
            self.errmsg += ex.message
            
        pass_msg = "Verify accounting packets success"
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', pass_msg)        

    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'check_list': {'acct-start':True,'acct-stop':True, 'acct-interim-update':True},
                    'acct_svr_port' : ''}
        self.conf.update(conf)      
        self.check_list = self.conf['check_list']
        
        self.accounting_server = self.testbed.components['LinuxServer']
                      
        self.errmsg = ''       
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carrier_bag(self):
        pass

    def _get_all_accounting_packets(self):
        res = self.accounting_server.read_tshark(" -R 'udp.port == %s'"% self.conf['acct_svr_port'], return_as_list=False)
        logging.info("Read packets is %s" % res)
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

        start_pattern = "Acct-Status-Type\(40\): Start\(1\)"
        #start_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Start"
        start_re = re.compile(start_pattern)
        
        stop_pattern =  "Acct-Status-Type\(40\): Stop\(2\)"
        #stop_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Stop"
        stop_re = re.compile(stop_pattern)
        
        inter_pattern = "Acct-Status-Type\(40\): Interim-Update\(3\)"
        #inter_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Interim-Update"
        inter_re = re.compile(inter_pattern)

        start_packets = [p for p in packets if start_re.search(p)]
        stop_packets = [p for p in packets if stop_re.search(p)]
        inter_packets = [p for p in packets if inter_re.search(p)]
        
        return {'acct-start': start_packets,
                'acct-stop': stop_packets,
                'acct-interim-update': inter_packets}

    def _verify_acct_ipass_attribute(self):
        acct_packets = self._get_all_accounting_packets()
        
        for key in self.check_list.keys():
            logging.info('Verify the packet info %s on packets:%s' % (key, self.check_list[key]))
            check_value = self.check_list[key]
            error_packets = {}
            if check_value:
                if not acct_packets[key]:
                    self.errmsg += 'There is not any %s packet is captured. ' % key
                    continue
            else:
                if acct_packets[key]:
                    self.errmsg += 'There is %s packet is captured. Wrong behavior' % key
                    continue