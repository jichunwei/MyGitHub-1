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
       - 'ping_timeout_ms': 'Timeout for ping',
       - 'target_ip_list': 'Target IP address list, ipv4 and ipv6',
       - 'allow': 'Target IP is allowed or not',
       - 'sta_tag': 'staion tag',
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - If self.allow: Verify can ping target IP[ipv4 and ipv6]
        - If not self.allow: Verify cannot ping target IP[ipv4 and ipv6]
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If allow: ping target IP address successfully. If not allow: can not ping target IP successfully. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_Station_Ping_Targets_IPV6(Test):
    required_components = ['Station']
    parameters_description = {'ping_timeout_ms': 'Timeout for ping',
                              'target_ip_list': 'Target IP address list, ipv4 and ipv6',
                              'allow': 'Target IP is allowed or not',
                              'sta_tag': 'staion tag',
                              }    
    
    def _init_params(self, conf):
        self.conf = {'ping_timeout_ms': 15 * 1000,
                     'target_ip_list': ['192.168.0.252'],
                     'allow': False,#ping allow(True|False) in target list.
                     'sta_tag': 'sta_1',
                     'retries': 3,
                     }
        self.conf.update(conf)
        
        self.target_ip_list = self.conf['target_ip_list']
        self.allow = self.conf['allow']
        
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
                        
        self.errmsg = ''
        self.passmsg = ''        
        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info("Station ping target IP list: %s" % self.target_ip_list)
        try:
            retry_count = self.conf['retries'] 
            res_err = {}
            for target_ip in self.target_ip_list:
                if self.allow:
                    logging.info("Verify can ping target %s" % target_ip)
                    for i in range(1, retry_count+1):
                        #err_msg = tmethod.client_ping6_dest_is_allowed(self.target_station, target_ip,
                        #                                           ping_timeout_ms = self.conf['ping_timeout_ms'])
                        #if err_msg:
                        err_msg = tmethod.client_ping_dest_is_allowed(self.target_station, target_ip,
                                                                      ping_timeout_ms = self.conf['ping_timeout_ms'])
                        if not err_msg:
                            break
                        else:
                            time.sleep(10)
                else:
                    logging.info("Verify can not ping target %s" % target_ip)
                    #err_msg = tmethod.client_ping6_dest_not_allowed(self.target_station, target_ip,
                    #                                               ping_timeout_ms = self.conf['ping_timeout_ms'])
                    #if err_msg:
                    err_msg = tmethod.client_ping_dest_not_allowed(self.target_station, target_ip,
                                                                   ping_timeout_ms = self.conf['ping_timeout_ms'])
                    
                if err_msg:
                    res_err.update({target_ip:err_msg})
            
            if res_err:
                self.errmsg = 'Ping target IP list failed: %s' % res_err
                
            if self.allow:
                self.passmsg = "The station could send traffic to destinations."
            else:
                self.passmsg = "The station could not send traffic to destinations."
                
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return  self.returnResult('PASS', self.passmsg)                     
    
    def cleanup(self):
        self._update_carribag()
