'''
Created on 2012.1.16
@author: West.li
'''

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient

class CB_ZD_CLI_Reboot_ZD(Test):
    
    def config(self, conf):
        self.retrive_carribag()
        self.init_param(conf)        
    
    def test(self):
        try:
            self.zdcli.do_shell_cmd('reboot')
        except:
            pass
            
        reconnect_cli_success='N'
        time_start=time.time()
        logging.info('begin to connect zdcli after zd reboot')
        while reconnect_cli_success=='N':
            if time.time()-time_start>self.timeout:
                logging.error('time out when reconnect cli after reboot')
                self.errormsg='time out when reconnect cli after reboot'
                break
            try:
                self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
                self.zdcli.login()
                reconnect_cli_success='Y'
                self.passmsg='reboot succ,connect to cli succ'
                logging.error(self.passmsg)
            except:
                pass
        self.update_carribag()
        if self.errormsg: return self.returnResult("FAIL", self.errormsg)            
        return self.returnResult("PASS", self.passmsg)
                    
    def cleanup(self):
        pass 
    
    def init_param(self, conf):
        self.conf = {'timeout':600, 'zd_tag': ''}
        self.conf.update(conf)
        
        zd_tag = self.conf.get('zd_tag')
        
        if zd_tag:
            self.zdcli = self.carrierbag[zd_tag]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.timeout=self.conf['timeout']
        self.passmsg = []
        self.errormsg = []
    
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
        