'''
Description:
    show management interface information on ZDCLI '.
Created on 2010-10-19
@author: louis.lou@ruckuswireless.com
'''

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import mgmt_interface_info as cli


class CB_ZD_CLI_Show_Mgmt_Interface(Test):
    '''
    ZD CLI: show management interface information .
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):  
        logging.info('Show MGMT-IF information via CLI')
        try:
            self.mgmt_interface_info_on_cli = cli.show_mgmt_if_info(self.zdcli)
            logging.info('All the MGMT-IF information on CLI is: \n%s' % self.mgmt_interface_info_on_cli)
        except Exception, e:
            self.errmsg = "Get a Error message:[%s]" % e.message
            logging.warning(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        
        self.passmsg = "MGMT-IF show return: \n %s"  % self.mgmt_interface_info_on_cli
        
        self._update_carrier_bag()

        return self.returnResult("PASS", self.passmsg)
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
#        self.zdcli = create_zd_cli_by_ip_addr(**default_cfg)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.passmsg = ""
        self.errmsg = ""
    
    def _update_carrier_bag(self):
        self.carrierbag['mgmt_interface_info_on_cli'] = self.mgmt_interface_info_on_cli    