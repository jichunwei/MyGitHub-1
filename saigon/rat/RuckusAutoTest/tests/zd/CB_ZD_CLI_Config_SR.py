'''
Created on 2011-2-15
@author: louis.lou@ruckuswireless.com
description:

'''
import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr

class CB_ZD_CLI_Config_SR(Test):
    '''
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.errmsg = self.set_sr_info(self.zdcli, self.sr_conf,self.wait_time)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         sr_conf = {}
                         )
        
        self.conf.update(conf)
        self.sr_conf = conf['sr_conf']
        
        #@author: chentao @2013-08-29  wait some time so that the zd can connect to the peer zd 
        if conf.get('wait_time'):
            self.wait_time = self.conf['wait_time']
        else:
            self.wait_time = 0    
        #@author: chentao @2013-08-29  wait some time so that the zd can connect to the peer zd 
                
        #@author: chentao @2013-08-29  to support ZD_SR testbed
        if self.conf.has_key('target_zd') and self.conf['target_zd']:
            if self.conf['target_zd'] == 'zd1':
                self.zdcli = self.testbed.components['ZDCLI1']
            else:
                self.zdcli = self.testbed.components['ZDCLI2'] 
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        #@author: chentao @2013-08-29  to support ZD_SR testbed
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass 
    
    def set_sr_info(self,zdcli,conf,wait_time):
        sr.set_sr_peer_ip(zdcli, conf)
        sr.set_sr_secret(zdcli, conf)
        wait_time = int(wait_time)
        #@author: chentao @2013-08-29  wait some time so that the zd can connect to the peer zd 
        if wait_time:
            logging.info('Wait %s seconds, so that zd can connect to peer zd'%wait_time)
            time.sleep(wait_time)
        #@author: chentao @2013-08-29  wait some time so that the zd can connect to the peer zd      