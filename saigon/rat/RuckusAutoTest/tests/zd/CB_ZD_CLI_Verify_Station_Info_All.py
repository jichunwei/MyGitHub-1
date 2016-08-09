'''
Description:

    Verify the information on CLI is the same as ZD GUI.
    
Created on 2010-10-14
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import station_info_cli as cli

class CB_ZD_CLI_Verify_Station_Info_All(Test):
    '''
    Verify ZD CLI : show ap all.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        
        if cli.verify_station(self.all_station_info_on_cli, self.all_station_info_on_zd):
            self.passmsg = 'All the station information are corrected'
        else:
            self.errmsg = 'Not all the station information are corrected'
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.all_station_info_on_cli = self.carrierbag['all_station_info_on_cli']
        if self.carrierbag.has_key('all_station_info_on_zd'):
            self.all_station_info_on_zd = self.carrierbag['all_station_info_on_zd']
        else:
            self.all_station_info_on_zd = self.zd.get_active_client_list()
        
        self.passmsg = ""
        self.errmsg = ""
        