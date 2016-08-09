'''
by:West.li
verify whether active zd is the same as expected one
 '''
#import os
#import re
import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Verify_Active_ZD(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if self.conf['wait_time']:
            logging.info("Sleep %s seconds" % self.conf['wait_time'])
            time.sleep(self.conf['wait_time'])
            
        active_zd = self.get_active_zd(self.zd1,self.zd2)
        if self.expected_azd!=active_zd:
            self.errmsg = 'active zd is not expected one,active zd is %s,expect is %s'%(active_zd.ip_addr,self.expected_azd.ip_addr)
        self.carrierbag['active_zd'] = active_zd
        self.testbed.components['ZoneDirector']=active_zd
        if active_zd==self.zd1:
            self.carrierbag['standby_zd']=self.zd2
            self.carrierbag['active_zd_cli']=self.carrierbag['zdcli1']
            self.carrierbag['standby_zd_cli']=self.carrierbag['zdcli2']
        else:
            self.carrierbag['standby_zd']=self.zd1
            self.carrierbag['active_zd_cli']=self.carrierbag['zdcli2']
            self.carrierbag['standby_zd_cli']=self.carrierbag['zdcli1']
        self.testbed.components['ZoneDirectorCLI']=self.carrierbag['active_zd_cli']
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)     
        else:
            msg = 'The active ZD %s is the same as expected' % self.carrierbag['active_zd'].ip_addr
            return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(wait_time = 10,
                         expect_zd = 'zd1')
        
        self.conf.update(conf)
        self.expected_azd = self.carrierbag[self.conf['expect_zd']]
                
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
       
    def get_active_zd(self,zd1,zd2):
        retry_time=5
        for retry in range(1,retry_time+1):
            zd1_state=red.get_local_device_state(zd1)
            if zd1_state == 'active':
                return zd1
            elif zd1_state == 'standby':
                return zd2
            
        raise('get wrong state %s after %d retries'% (zd1_state,retry)) 