'''
modified by west
after fail over,modify active_zd/standby_zd/active_zd_cli/standby_zd_cli in carrierbag
'''
#import os
#import re
#import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Failover(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('Test for fail over button in active ZD(%s)'%self.active_zd.ip_addr)
        active_zd_ipaddr=self.active_zd.ip_addr
        self._failover_active_zd(self.active_zd)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self.carrierbag['active_zd']=self.standby_zd
        self.carrierbag['standby_zd'] = self.active_zd
        self.carrierbag['active_zd_cli'] = self.standby_zdcli
        self.carrierbag['standby_zd_cli'] = self.active_zdcli
        self.testbed.components['ZoneDirectorCLI'] = self.carrierbag['active_zd_cli']
        self.testbed.components['ZoneDirector']    = self.carrierbag['active_zd']
        msg = 'Failover zd %s successfully,after failover,%s is active zd,%s is standby zd'%(active_zd_ipaddr,self.standby_zd.ip_addr,self.active_zd.ip_addr)
        
        active_zd = self._get_active_zd(self.zd1,self.zd2)
        if active_zd !=self.carrierbag['active_zd']:
            return self.returnResult('FAIL', 'zd state is not right after failover')
        return self.returnResult('PASS', msg)
    
    
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict()
        
        self.conf.update(conf)
                
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        self.active_zdcli = self.carrierbag['active_zd_cli']
        self.standby_zdcli = self.carrierbag['standby_zd_cli']
       

    def _failover_active_zd(self,zd):
        logging.info('Click failover button on ZD %s',zd.ip_addr)
        red.failover(zd)
        
        
    def _get_active_zd(self,zd1,zd2):
        retry_time=5
        for retry in range(1,retry_time+1):
            zd1_state=red.get_local_device_state(zd1)
            zd2_state=red.get_local_device_state(zd2)
#            try:
#                zd1_state=red.get_local_device_state(zd1)
#                zd2_state=red.get_local_device_state(zd2)
#            except:
#                import pdb
#                pdb.set_trace()
            if zd1_state == 'active' and zd2_state == 'standby':
                return zd1
            elif zd1_state == 'standby' and zd2_state == 'active':
                return zd2
        raise('get wrong state %s after %d retries'% (zd1_state,retry)) 
    
    