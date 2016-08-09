'''
by Louis Lou (louis.lou@ruckuswireless.com)
initialize the ZD CLI Environment of Smart Redundancy.
    +Call two ZD up;
    +create two ZD CLI. 
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components import create_zd_cli_by_ip_addr
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_CLI_SR_Init_Env(Test):
    
    def config(self,conf):
        
        self._cfgInitTestParams(conf)
    
    def test(self):
        
        self._update_carrierbag()
        msg = 'Initial Test Environment of Test'
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        
        self.errmsg = ''
        self.conf = dict(
                       debug=False,
                       zd1_ip_addr = '192.168.0.2',
                       zd2_ip_addr = '192.168.0.3',
                       username = 'admin',
                       password = 'admin',
                       shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB',
                       share_secret = 'testing',
                       )
        self.conf.update(conf)
        
        try: 
            self.zd1 = self.testbed.components['ZoneDirector']
        except:
            self.zd1 = ZoneDirector(dict(ip_addr=self.conf['zd1_ip_addr']))
        
        try:
            self.zdcli1 = self.testbed.components['ZoneDirectorCLI']
        except:
            self.zdcli1 = create_zd_cli_by_ip_addr(ip_addr = self.conf['zd1_ip_addr'],
                                                   username = self.conf['username'],
                                                   password = self.conf['password'],
                                                   shell_key = self.conf['shell_key']
                                                   )
        
        self.zd2 = ZoneDirector(dict(ip_addr=self.conf['zd2_ip_addr']))
        self.zdcli2 = create_zd_cli_by_ip_addr(ip_addr = self.conf['zd2_ip_addr'],
                                                   username = self.conf['username'],
                                                   password = self.conf['password'],
                                                   shell_key = self.conf['shell_key']
                                                   )
        
        self.share_secret = self.conf['share_secret'] 
    
    def _update_carrierbag(self):
            
        self.carrierbag['zd1'] = self.zd1
        self.carrierbag['zd2'] = self.zd2
        self.carrierbag['share_secret'] = self.share_secret
        
        self.carrierbag['zdcli1'] = self.zdcli1
        self.carrierbag['zdcli2'] = self.zdcli2
