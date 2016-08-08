"""
   Description: 
   This test class support to ap set director zd via CLI
   @since: May 2014
   @author: Yuyanan

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - set ap director zd      
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: set ap director zd success 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as apinfocli
from RuckusAutoTest.common import lib_Constant as const

class CB_ZD_Make_AP_Connect_To_ZD(Test):
    
    def config(self,conf):
        self._retrive_carrier_bag()
        self._cfgInitTestParams(conf)
    def test(self):
        self._adjust_ap_to_one_zd()
        self._wait_for_aps_rejoin()
        if self.errmsg:
            return ('FAIL', self.errmsg)       
        
        msg = 'ap connect zd success' 
        return ('PASS', msg)
        
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = {'ap_mac': None,
                     'ip_cfg': {'ip_version':None}}
        #ip_cfg={'ip_version': const.IPV4}
        self.conf.update(conf)
        ap_mode = self.conf.get('ip_cfg').get('ip_version')
        self.ap_mac = self.conf.get('ap_mac')
        self.ap_ip = apinfocli.get_ap_ip(self.zdcli,self.ap_mac)
        
        if ap_mode == const.IPV4:
            self.zd_ip = self.get_zd_ip_cfg.get('Device IP Address').get('IP Address')
        else:
            self.zd_ip = self.get_zd_ip_cfg.get('Device IPv6 Address').get('IPv6 Address')

       
    def _retrive_carrier_bag(self):
        self.get_zd_ip_cfg = self.carrierbag['cli_zd_ip_cfg']   
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.zd = self.testbed.components['ZoneDirector']
        
    def _adjust_ap_to_one_zd(self):
        cmd = 'set director addr  '+ self.zd_ip 
        zd_active_ap = RuckusAP(dict(ip_addr = self.ap_ip,username='admin',password='admin')) 
        zd_active_ap.do_cmd(cmd)
        zd_active_ap.reboot()

    def _wait_for_aps_rejoin(self):
        '''
        Wait for all ap rejoin after change ap ip mode.
        '''
        logging.info('Wait for APs are connected [%s]' % self.ap_ip)
        timeout = 480        
        res_aps_connected = []
        res_ap_connected = self._wait_ap_connected(self.ap_mac, timeout)
        if res_ap_connected:
            errmsg = "APs are not connected: %s" % res_aps_connected
            raise Exception(errmsg)
        
    def _wait_ap_connected(self, ap_mac_addr, timeout):
        '''
        Wait ap provisioning, till status is connected.
        '''
        end_time = time.time() + timeout
        err_d = {}
        while True:
            ap_info = self.zd.get_all_ap_info(ap_mac_addr)
            if ap_info:
                if ap_info['status'].lower().startswith("connected"):
                    logging.info("The provision process for the AP %s is completed successfully" % ap_mac_addr)
                    break
            if time.time() > end_time:
                if ap_info:
                    err_msg = "FAIL", "The AP %s is in the %s status instead of \"Connected\" status after %d seconds" % \
                                 (ap_mac_addr, ap_info['status'], timeout)
                    err_d[ap_mac_addr] = err_msg
                else:
                    err_msg = "FAIL", "The AP %s still does not appear in the AP-Summary table after %d seconds" % \
                                     (ap_mac_addr, timeout)
                    err_d[ap_mac_addr] = err_msg
                    
        return err_d 
        