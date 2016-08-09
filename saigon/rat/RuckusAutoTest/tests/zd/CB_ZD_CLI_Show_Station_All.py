'''
Description:
    show station information on ZDCLI use command 'show station all'.
Created on 2010-10-12
@author: louis.lou@ruckuswireless.com
'''

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import station_info_cli as cli


class CB_ZD_CLI_Show_Station_All(Test):
    '''
    ZD CLI: Show AP ALL.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):  
        logging.info('Show station all')
        self.all_station_info_on_cli = cli.show_station_all(self.zdcli)
        logging.info('All the station information on CLI is: \n%s' % self.all_station_info_on_cli)
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        self.passmsg = "show station all return: \n %s"  % self.all_station_info_on_cli
        
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
        self.carrierbag['all_station_info_on_cli'] = self.all_station_info_on_cli    