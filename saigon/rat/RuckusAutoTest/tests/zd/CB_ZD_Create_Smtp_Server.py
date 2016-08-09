'''
Created on Jan 24, 2014

@author: jacky luh
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_Smtp_Server(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'smtp_server_conf': ''}
    
    
    def config(self, conf):
        self._init_test_parameters(conf)


    def test(self):
        #create the local user
        self._create_smtp_server(self.test_conf)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = 'Configure the smtp server in ZD CLI successfully!'
        return self.returnResult('PASS', self.passmsg)
        
               
    def cleanup(self):
        pass


    def _init_test_parameters(self, conf):
        self.guest_access_conf = {}
        self.test_conf = {}   
        if conf.has_key('smtp_serv_cfg'):
            self.test_conf = conf['smtp_serv_cfg']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
    
    def _create_smtp_server(self, conf):
        logging.log_info('Configure SMTP Server', 'Execute commands', 'SMTP Server Setting')
        (result, msg) = lib.zdcli.system.set_email_server(self.zdcli, self.test_conf)
        
        if result:
            self.passmsg = msg
        else:
            self.errmsg = msg