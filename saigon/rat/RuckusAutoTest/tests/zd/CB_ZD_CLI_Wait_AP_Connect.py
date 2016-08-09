'''
Created on 2012.1.16
@author: Wst.li
'''

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components.lib.zdcli import ap_info_cli
import libZD_TestConfig as tconfig

class CB_ZD_CLI_Wait_AP_Connect(Test):
    
    def config(self, conf):
        self.retrive_carribag()
        self.init_param(conf)        
    
    def test(self):
        t0 = time.time()
        while True:
            if time.time()-t0 >self.timeout:
                return self.returnResult("FAIL", 'ap did not connected to zd after %s seconds'%self.timeout)
            status = ap_info_cli.get_ap_status(self.zdcli, self.ap_mac)
            if 'connected'==status:
                logging.info('ap %s connected to zd'%self.ap_mac)
                break
            logging.info('ap %s not connected to zd yet'%self.ap_mac)
        return self.returnResult("PASS", self.passmsg)
                    
    def cleanup(self):
        pass 
    
    def init_param(self, conf):
        self.conf = {'timeout':600, 'zd_tag': '' , 'ap_mac':'','ap_tag':''}
        self.conf.update(conf)
        
        zd_tag = self.conf.get('zd_tag')
        
        if zd_tag:
            self.zdcli = self.carrierbag[zd_tag]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        #@author: yuyanan @since: 2014-11-3 optimize ap tag
        if self.conf.get('ap_tag'):
            self.ap_mac = tconfig.get_active_ap_mac(self.testbed,self.conf['ap_tag'])
        else:
            self.ap_mac = self.conf['ap_mac']
        self.timeout=self.conf['timeout']
        self.passmsg = 'ap %s has connected to ZD'%self.ap_mac
        self.errormsg = ''
    
    def retrive_carribag(self):        
        pass       
    
    def update_carribag(self):
        try:
            self.carrierbag.pop('existed_stamgrlist')
        except:
            pass
        try:
            self.carrierbag.pop('existed_apmgrlist')
        except:
            pass
        try:
            self.carrierbag.pop('existed_weblist')
        except:
            pass
        