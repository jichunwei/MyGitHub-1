'''
Description: Get all AAA servers.
Created on 2010-10-26
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import aaa_servers as lib

class CB_ZD_CLI_Get_All_AAA_Servers(Test):
    '''
    Get all AAA servers.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        try:
            res = lib.get_all_aaa_servers(self.zdcli)
            if res and res.has_key('AAA'):
                aaa = res['AAA']
                id = aaa['ID']
                svr_list = id.values()
                passmsg.append('Get All AAA Servers [%s] successfully' % svr_list)
            else:
                return self.returnResult('FAIL', 'Have not any AAA information') 
            self._update_carrier_bag(svr_list)
        
        except Exception, e:
            logging.warning(e.message)
            return self.returnResult('FAIL', e.message)
        
        return self.returnResult('PASS', passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self, svr_l):
        self.carrierbag['zdcli_aaa_server_list'] = svr_l
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    