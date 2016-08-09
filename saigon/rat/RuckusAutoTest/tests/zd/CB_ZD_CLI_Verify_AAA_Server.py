'''
Description:Checking AAA Server info between GUI and CLI.
Created on 2010-10-26
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import aaa_servers as lib

class CB_ZD_CLI_Verify_AAA_Server(Test):
    '''
     Checking AAA Server info between GUI and CLI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):            
        
        r, c = lib.verify_aaa_server_by_type(self.zdcli, self.server_conf, self.zdcli_aaa_server_cfg, self.aaa_type)
        if r:            
            return self.returnResult('PASS', 'AAA Server [%s] checking between GUI and CLI is correct' % self.server_conf['server_name'])
        else:
            return self.returnResult('FAIL', c)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_aaa_server_cfg = self.carrierbag['zdcli_aaa_server_cfg']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(server_conf = {
            'server_name': 'RADIUS',
            'server_addr': '192.168.0.252',
            'radius_auth_secret': '1234567890',
            'server_port': '1812',
            'type'       :'radius-auth',},
            )
        self.conf.update(conf)        
        self.server_conf = self.conf['server_conf']
        self.aaa_type = self.server_conf['type']
        self.aaa_type = lib.decode_type(self.aaa_type)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
