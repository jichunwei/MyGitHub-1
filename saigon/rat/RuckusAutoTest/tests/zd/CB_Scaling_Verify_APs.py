# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

'''
Verify all of APs[RuckusAPs, SIMAPs] are connected.
'''
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import scaling_zd_lib as zdHelper

class CB_Scaling_Verify_APs(Test):
    
    
    def config(self, conf):
        self.conf= dict(timeout = 1800, chk_gui = False, chk_mac = False)
        self.conf.update(conf)        
        self.chk_gui = self.conf['chk_gui']
        self.timeout = self.conf['timeout']
        self.chk_mac = self.conf['chk_mac']
        if self.testbed.components.has_key('ZoneDirector') and self.testbed.components.has_key('ZoneDirectorCLI'):
            self.zd = self.testbed.components['ZoneDirector']
            self.zdcli = self.testbed.components['ZoneDirectorCLI']   
        if self.testbed.components.has_key('zd1')and self.testbed.components.has_key('ZDCLI1'):
            self.zd = self.testbed.components['zd1']                
            self.zdcli = self.testbed.components['ZDCLI1'] 
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        if self.carrierbag.has_key('active_zd_cli'):
            self.zdcli = self.carrierbag['active_zd_cli']
        if self.carrierbag.has_key("existing_aps_list"):
            self.aps = self.carrierbag['existing_aps_list']
        else:
            self.aps = self.testbed.get_aps_sym_dict()
                
        self.passmsg = ""
        self.errmsg = ""        
            
    def test(self):                
        res = zdHelper.check_all_aps_status_from_cmd(self.zdcli, self.aps, time_out=self.timeout, chk_mac = self.chk_mac)
        if not res:
            self.errmsg = "time out when try to wait for all APs connecting against CLI."
            return ("FAIL", self.errmsg)
        
        if self.chk_gui:            
            res = zdHelper.check_aps_status_from_gui(self.zd, self.aps, time_out = self.timeout)
            if not res :
                self.errmsg = "time out when try to wait for all APs connecting against GUI."
                return ("FAIL", self.errmsg)
        
        self.passmsg = 'All of APs are connected.'
        logging.debug(self.passmsg)
        self._update_carrier_bag()
        
        return ("PASS", self.passmsg) 
                    
    def cleanup(self):
        pass
    
    
    def _update_carrier_bag(self):               
        self.carrierbag['existing_aps_list'] = self.aps
        
                
