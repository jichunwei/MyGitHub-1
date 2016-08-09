# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: December 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirector'
   Test parameters:
       - 'ping_duration': 'duration of ping ZD ip address, in seconds',
       - 'ping_timeout': 'timeout of each ping action, in seconds',
       - 'debug_info': 'configuration for save_debug_info'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Execute support in ZD CLI (config>save_debug_info)
        - Verify ZD is not reboot:
             a. Ping ZD IP address for some time (ping_duration), verify no timeout in result
             b. Get ZD uptime, verify it is greater than duration between starting execute support
                command and current time.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Support command is executed in ZD CLI and ZD is not reboot successfully.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as RU
from RuckusAutoTest.components.lib.zdcli import debug_mode_functions as debug
from RuckusAutoTest.components.lib.zdcli import sys_basic_info as sysinfo

class CB_ZD_CLI_Exec_Support_Verify_ZD_Not_Reboot(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'ping_duration': 'duration of ping ZD ip address, in seconds',
                              'ping_timeout': 'timeout of each ping action, in seconds',
                              'debug_info': 'configuration for save_debug_info'
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            #Start execute support command time.
            start_exec_time = time.time()
            print("ZDCLI prompt:%s" % self.zdcli.current_prompt)
            logging.info("Execute support command in ZD CLI")
            err_msg = self._save_debug_info_zd_cli(self.zdcli, self.debug_info)
            if err_msg:
                self.errmsg = err_msg             
            else:
                print("ZDCLI prompt 2:%s" % self.zdcli.current_prompt)
                res_not_reboot, err_msg = self._verify_zd_not_reboot(self.zdcli, start_exec_time)
                if not res_not_reboot: self.errmsg = err_msg
                                        
        except Exception, e:
            self.errmsg = "Fail to execute support command: [%s]" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Execute support command and correctly ZD is not reboot"            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(ping_duration = 180, #seconds
                         ping_timeout = 1, #seconds
                         debug_info = {'tftp_server_ip': '192.168.0.100'},
                         )
        
        self.conf.update(conf)
        
        self.ping_duration = self.conf['ping_duration']
        self.ping_timeout = self.conf['ping_timeout']*1000  #ms
        self.debug_info = self.conf['debug_info']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
            
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_zd_not_reboot(self, zdcli, start_exec_time):
        """
        Verify ZD is reboot or not, by ping ZD IP address and up time.
        Return: 
            res_not_reboot, msg.
            res_not_reboot = True, ZD is not reboot.
            res_not_reboot = False, ZD is reboot.
        """
        res_not_reboot = True
        err_msg = ""
                    
        logging.info("Ping ZD IP address for %s seconds" % self.ping_duration)
        #Verify ZD didn't reboot.
        zd_ip_addr = zdcli.ip_addr
        timeout_s = self.ping_duration
        
        start_time = time.time()
        current_time = start_time
        while current_time - start_time < timeout_s:
            res = RU.ping(zd_ip_addr, self.ping_timeout)
            if 'timeout' in res.lower():
                logging.debug("Ping ZD timeout:%s" % res)
                res_not_reboot = False
                err_msg += "ZD is reboot after support command;"
                break
            current_time = time.time()   
            
        if res_not_reboot == False:
            #Wait for ZD reboot, if ZD is reboot.
            logging.info("Wait ZD reboot for 60 seconds")
            time.sleep(60)
        
        current_time = time.time()
        #Duration between start execute support and current time.
        duration = current_time - start_exec_time
        logging.debug("Duration:%s" % duration)
        
        logging.info("Get ZD Up Time")
        zd_up_time = None
        try:
            zd_up_time = sysinfo.get_sys_uptime(zdcli)                
            logging.debug("Up time:%s" % zd_up_time)
        except Exception,ex:
            err_msg = "Can't get ZD uptime:%s" % ex.message
            
        if not err_msg:
            if not zd_up_time:
                err_msg = "Can't get ZD uptime"
            else:
                #If up time less than duration, ZD is reboot.
                if zd_up_time < duration: 
                    res_not_reboot = False
                    err_msg += "ZD up time is less than %s seconds." % int(duration)
            
        return res_not_reboot, err_msg
    
    def _save_debug_info_zd_cli(self, zdcli, debug_info):
        """
        Execute save_debug_info in debug mode in ZD CLI.
        """
        errmsg = ""
        logging.info('Debug - Execute command save_debug_info')
        try:
            var, res = debug.save_debug_info(zdcli, debug_info['tftp_server_ip'], **{'time_out': 60})
            logging.info('Debug Save Debug Info, Return Output %s' % res)
            if not var:
                errmsg = 'The command "save_debug_info" could not execute'
        except Exception, e:
            errmsg = '[DEBUG MODE][PS] %s' % e.message
            
        return errmsg