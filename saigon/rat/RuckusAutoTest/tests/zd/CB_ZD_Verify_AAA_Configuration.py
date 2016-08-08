'''
verify the configuration of aaa servers is the same as configuration
west.li
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.aaa_servers_zd import verify_server_cfg_by_name


class CB_ZD_Verify_AAA_Configuration(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        for server in self.conf:
            self.errmsg+=verify_server_cfg_by_name(self.zd,server,self.conf[server])
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        '''
        conf={
                'super_user_server':{
                               'server_name':'super_user_server',
                               'server_type':'tacacs_plus',
                               'server_addr':server_ip_addr,
                               'server_port':'49',
                               'tacacs_auth_secret':'ruckus',
                               'tacacs_service':'ap-login'
                               },
                'monitor_user_server':{
                               'server_name':'monitor_user_server',
                               'server_type':'tacacs_plus',
                               'server_addr':server_ip_addr,
                               'server_port':'49',
                               'tacacs_auth_secret':'ruckus',
                               'tacacs_service':'ap-login'
                               }
            }
        '''   
        self.conf=conf 
        for server in  self.conf:
            if self.conf[server].has_key('server_type'):
                self.conf[server]['type']=self.conf[server]['server_type']
                del self.conf[server]['type']
            if self.conf[server].has_key('server_type'):
                self.conf[server]['tacacs_auth_secret']=self.conf[server]['tacacs_auth_secret']
                del self.conf[server]['tacacs_auth_secret']
            
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
    
    def _updateCarrierbag(self):
        pass
            
                