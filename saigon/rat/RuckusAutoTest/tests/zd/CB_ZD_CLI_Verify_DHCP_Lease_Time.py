"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'wlan_cfg': {},
        - 'sta_tag': 'sta_1'
        - 'ap_tag' : 'active_ap'
        - 'check_time' : 120,
        - 'time_range': 40
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the DHCP lease time of special station from ZD and check the lease time      
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Verify DHCP lease time on ZD success 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Verify_DHCP_Lease_Time(Test):
    required_components = ['RuckusAP','Station']
    parameters_description = {'sta_tag': 'sta_1',
                              'max_lease_time': 120,
                              'check_time' : 120,
                              'time_range': 40}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info("Verify DHCP lease time on ZD")
        try:
            self._verify_zd_lease_time()
           
        except Exception, ex:
            self.errmsg = 'Verify DHCP lease time on ZD fail:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Verify DHCP lease time on ZD success'
            return self.returnResult('PASS', pass_msg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'sta_tag': 'sta_1',
                     'max_lease_time': 120,
                    'check_time' : 120,
                    'time_range': 40}
        self.conf.update(conf)
        self.max_lease_time = self.conf['max_lease_time']
        self.check_time = self.conf['check_time']
        self.time_range = self.conf['time_range']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
    
    def _retrieve_carribag(self):
        self.sta_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        if not self.max_lease_time:
            self.max_lease_time = self.carrierbag['backup_lease_time']
            self.check_time = self.max_lease_time
    
    def _update_carrier_bag(self):
        pass
     
    def _verify_zd_lease_time(self):
        lease_time = lib.zdcli.shell.get_dhcp_lease_time_by_mac(self.zdcli, self.sta_mac)
        logging.info("Get lease time from zd:%s" % lease_time)
        if lease_time['errmsg']:
            self.errmsg = lease_time['errmsg']
            return
        current_time = lease_time['current']
        init_time = lease_time['init']
        if not int(init_time) == int(self.max_lease_time):
            self.errmsg = "The max lease time is incorrect"
        else:
            if int(current_time) > (int(self.check_time) - int(self.time_range)) and int(current_time) <= int(self.check_time) :
                pass
            else:
                self.errmsg = "The lease time %s on ZD is incorrect. lease_time: " % current_time         
