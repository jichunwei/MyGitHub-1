# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: November 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'RuckusAP'
   Test parameters:
       - ap_tag: ap tag. Will get ap components via ap tag in self.testbed.components.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Execute support in AP CLI
        - Verify AP is not reboot:
             a. Ping AP IP address for some time (ping_duration), verify no timeout in result
             b. Get AP uptime, verify it is greater than duration between starting execute support
                command and current time.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Support command is executed in AP CLI and AP is not reboot successfully.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as RU
from RuckusAutoTest.components.lib.apcli import systemgroup

class CB_AP_CLI_Exec_Support_Cmd(Test):
    required_components = ['AP']
    parameters_description = {'ap_tag': 'Access point tag',
                              'ping_duration': 'duration of ping AP ip address, in seconds',
                              'ping_timeout': 'timeout of each ping action, in seconds',
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            for active_ap in self.active_ap_list:
                ap_mac = active_ap.base_mac_addr
                #Start execute support command time.
                start_exec_time = time.time()
                
                logging.info("Execute support command in AP CLI for %s" % ap_mac)
                res_support, msg = systemgroup.exec_support(active_ap)                
                if not res_support: 
                    self.errmsg = msg
                else:
                    res_not_reboot, err_msg = self._verify_ap_not_reboot(active_ap, start_exec_time)
                    if not res_not_reboot: self.errmsg = err_msg
                                        
        except Exception, e:
            self.errmsg = "Fail to execute support command: [%s]" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Execute support command and correctly AP is not reboot"            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(ap_tag = '', #or ['ap1', 'ap2']
                         ping_duration = 180, #seconds
                         ping_timeout = 1, #seconds
                         )
        
        self.conf.update(conf)
        
        self.ping_duration = self.conf['ping_duration']
        self.ping_timeout = self.conf['ping_timeout']*1000  #ms
        
        ap_tag = self.conf['ap_tag']        
        self.active_ap_list = []
        if ap_tag:
            if type(ap_tag) != list:
                ap_tag_list = [ap_tag]
            else:
                ap_tag_list = ap_tag
                
            for aptag in ap_tag_list:
                self.active_ap_list.append(self.carrierbag[aptag]['ap_ins'])
        else:
            #If no ap_tag is specified, will set all ap as specified values.
            self.active_ap_list = self.testbed.components['AP']
            
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_ap_not_reboot(self, active_ap, start_exec_time):
        """
        Verify AP is reboot or not, by ping AP IP address and up time.
        Return: 
            res_not_reboot, msg.
            res_not_reboot = True, AP is not reboot.
            res_not_reboot = False, AP is reboot.
        """
        res_not_reboot = True
        err_msg = ""
                    
        logging.info("Ping AP IP address for %s seconds" % self.ping_duration)
        #Verify AP didn't reboot.
        ap_ip_addr = active_ap.ip_addr
        timeout_s = self.ping_duration
        
        start_time = time.time()
        current_time = start_time
        while current_time - start_time < timeout_s:
            res = RU.ping(ap_ip_addr, self.ping_timeout)
            if 'timeout' in res.lower():
                logging.debug("Ping AP timeout:%s" % res)
                res_not_reboot = False
                err_msg += "AP is reboot after support command;"
                break
            current_time = time.time()   
            
        if res_not_reboot == False:
            #Wait for AP reboot, if ap is reboot.
            logging.info("Wait AP reboot for 60 seconds")
            time.sleep(60)
        
        current_time = time.time()
        #Duration between start execute support and current time.
        duration = current_time - start_exec_time
        logging.debug("Duration:%s" % duration)
        
        logging.info("Get AP Up Time")
        ap_up_time = active_ap.get_up_time()
        logging.debug("Up time:%s" % ap_up_time)
        
        #If up time less than duration, AP is reboot.
        if ap_up_time < duration: 
            res_not_reboot = False
            err_msg += "AP up time is less than %s seconds." % int(duration)
            
        return res_not_reboot, err_msg