'''
by west.li@2012.2.2
reconnect all zd cli in test enviroment
used after upgrade/restore/reboot or something like that can make ssh disconnect
'''

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient

class CB_ZD_CLI_Reconnect_Zdcli(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):
        for zdcli in self.zdcli_list:
            try:
                zdcli.do_shell_cmd('')
            except:
                zdcli.zdcli = sshclient(zdcli.ip_addr, zdcli.port,'admin','admin')
                zdcli.login()
        
        self.passmsg = 'all zdcli is connected' 
        logging.info(self.passmsg)       
        self._update_carrier_bag()
        
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('sim_version'):
            self.sim_version = self.carrierbag['sim_version']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli_list = [self.testbed.components['ZoneDirectorCLI']]
        
        if self.carrierbag.has_key('zdcli1') and self.carrierbag.has_key('zdcli2'):
            self.zdcli_list = [self.carrierbag['zdcli1'],self.carrierbag['zdcli2']]
            
        if self.conf.has_key('zd'):
            if self.conf['zd']== 'standby':
                self.zdcli_list = [self.carrierbag['standby_zd_cli']]
            elif self.conf['zd']== 'active':
                self.zdcli_list = [self.carrierbag['active_zd_cli']]
            elif self.conf['zd']== 'zd1':
                self.zdcli_list = [self.carrierbag['zdcli1']]
            elif self.conf['zd']== 'zd2':
                self.zdcli_list = [self.carrierbag['zdcli2']]
                
                            
        self.errmsg = ''
        self.passmsg = ''
