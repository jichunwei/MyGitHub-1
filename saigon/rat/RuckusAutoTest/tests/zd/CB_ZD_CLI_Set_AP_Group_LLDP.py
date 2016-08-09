'''
Created on Sep 30, 2014

@author: chen tao
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_ap_group as apgcli
class CB_ZD_CLI_Set_AP_Group_LLDP(Test):
    
    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)

    def test(self):
        self.set_lldp()

        if self.errmsg: 
            if self.negative:
                return self.returnResult('PASS', self.errmsg)
            else:
                return self.returnResult('FAIL', self.errmsg)
        else:
            if self.negative:
                return self.returnResult('FAIL', self.passmsg)
            else:
                return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        pass

    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'name':'System Default',
                     'lldp_cfg':{},
                     'negative':False
                     }
        self.conf.update(conf)
        self.conf['lldp'] = self.conf['lldp_cfg']
        self.conf.pop('lldp_cfg')
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.negative =self.conf['negative']

    def set_lldp(self):
        
        logging.info('Set ap group lldp in ZD CLI')
        
        try:
            res, msg = apgcli.new_ap_group(self.zdcli, self.conf)
            if res:
                self.passmsg = msg

            else:
                self.errmsg = msg

        except Exception, ex:
            self.errmsg = ex.message
