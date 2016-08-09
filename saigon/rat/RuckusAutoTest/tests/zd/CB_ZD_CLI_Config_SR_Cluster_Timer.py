'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import logging
from copy import deepcopy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr

class CB_ZD_CLI_Config_SR_Cluster_Timer(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            sr.set_sr_cluster_timer(self.zdcli, self.conf['cluster_timer'])
        except Exception, ex: 
            self.errmsg = ex.message
        self.passmsg = 'Setting SR cluster timer succeeded.'
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'zdcli_tag':'',
                     'cluster_timer':{'t_min':'1',
                                      't_day':'60'
                                     }
                     }
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
