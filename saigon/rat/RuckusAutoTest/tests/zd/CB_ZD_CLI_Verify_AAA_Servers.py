'''
Description:Checking all AAA Servers info between GUI and CLI.
Created on 2010-10-26
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import aaa_servers as lib

class CB_ZD_CLI_Verify_AAA_Servers(Test):
    '''
     Checking all AAA Servers info between GUI and CLI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):            
        pass_msg = []
        err_msg = []
        for svr in self.server_list:
            aaa_type = svr['type']
            aaa_type = lib.decode_type(aaa_type)
            for svr_d in self.svr_list:
                name = svr_d['Name']
                if name == svr['server_name']:                
                    self._chk_svr_info(svr, svr_d, name, aaa_type, pass_msg, err_msg)
        
        if err_msg:
            return self.returnResult("FAIL", err_msg)
        elif len(pass_msg) < 4:
            return self.returnResult("FAIL", 'Miss some of servers, please check')
        else:
            return self.returnResult("PASS", pass_msg)        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.svr_list = self.carrierbag['zdcli_aaa_server_list']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(server_list = [{
            'server_name': 'RADIUS',
            'server_addr': '192.168.0.252',
            'radius_auth_secret': '1234567890',
            'server_port': '1812',
            'type'       :'radius-auth'},],            
            )
        self.conf.update(conf)        
        self.server_list = self.conf['server_list']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
    
    def _chk_svr_info(self, gui_d, cli_d, name, type, pass_msg, error_msg):
        r, c = lib.verify_aaa_server_by_type(self.zdcli, gui_d, cli_d, type)
        if r:
            pass_msg.append('server [%s] existed and information checking is correct' % name)
        else:
            error_msg.append(c)
    
