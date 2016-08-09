'''
Description: Get AAA server via AAA server name
Created on 2010-10-26
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import aaa_servers as lib

class CB_ZD_CLI_Get_AAA_Server_By_Name(Test):
    '''
    Get AAA server via AAA server name.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        try:
            res = lib.get_aaa_server_by_name(self.zdcli, self.server_name)
            if res and res.has_key('AAA'):
                aaa = res['AAA']
                id = aaa['ID']
                svr_d = id.values()[0]
                passmsg.append('Get AAA Server [%s] successfully' % self.server_name)
            self._update_carrier_bag(svr_d)            
            
        except Exception, e:
            logging.warning(e.message)
            return self.returnResult('FAIL', e.message)
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self, svr_d):
        self.carrierbag['zdcli_aaa_server_cfg'] = svr_d
    
    def _init_test_params(self, conf):
        self.conf = dict(server_name = 'ldap')
        self.conf.update(conf)
        self.server_name = self.conf['server_name']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    