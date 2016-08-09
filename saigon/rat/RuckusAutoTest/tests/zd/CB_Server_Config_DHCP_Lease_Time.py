"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'lease_time': 'max lease time'
        - 'cfg_type': 'get, set'
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - if cfg_type = get: get the max lease time of DHCP server
        - if cfg_type = set: set the max lease time of DHCP server and restart DHCP server
                             if lease_time = '' ,use the lease time in carrie bag       
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get or set max lease time success and restart DHCP server success
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test

class CB_Server_Config_DHCP_Lease_Time(Test):
    required_components = ['LinuxServer']
    parameters_description = {'lease_time': '',
                              'is_clearup': False}
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Config DHCP lease time')
        try:
            if self.isclearup:
                if self.backup_lease_time:
                    self._set_dhcp_lease_time(int(self.backup_lease_time))
                else:
                    self.errmsg("Can't find backup_lease_time in carrie bag")
            else:
                self._set_dhcp_lease_time(int(self.lease_time))                              
        except Exception, ex:
            self.errmsg = 'Config DHCP lease time fail:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Config DHCP lease time success'
            return self.returnResult('PASS', pass_msg)        
        
        
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'lease_time': 3200,
                    'is_clearup': False}
        self.conf.update(conf)       
        self.lease_time = self.conf['lease_time']
        self.backup_lease_time = ''
        self.isclearup = self.conf['is_clearup']
        self.server = self.testbed.components['LinuxServer']                
        self.errmsg = ''        
    
    def _retrieve_carribag(self):
        if self.carrierbag.has_key('backup_lease_time'):
            self.backup_lease_time = int(self.carrierbag['backup_lease_time'])
    
    def _update_carrier_bag(self):
        pass
 
    def _set_dhcp_lease_time(self, lease_time=""):
        return self.server.set_dhcp_lease_time('set', lease_time)