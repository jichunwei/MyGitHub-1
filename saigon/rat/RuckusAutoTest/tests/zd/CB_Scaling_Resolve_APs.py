# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.
'''
Resolve APs info from ZD's UI, and make sure all of testbed APs are connected.
'''
from RuckusAutoTest.models import Test

from u.zd.scaling.lib import scaling_zd_lib as zdHelper

class CB_Scaling_Resolve_APs(Test):
    required_components = ["ZoneDirector"]
    parameter_description = {}
    
    def config(self, conf):
        self.conf = conf        
        self.zd = self.testbed.components['ZoneDirector']
        
    
    def test(self):
        aps = zdHelper.resolve_verify_all_aps(self.zd)
        try:
            self._verify_aps_from_testbed(aps)
            
        except Exception, e:
            
            return ("FAIL", "Fail info [%s]" % e)
        
        self.carrierbag['existing_aps_list'] = aps
        
        return ("PASS", "All of APs are connected.")
        
    
    def cleanup(self):
        pass

    def _verify_aps_from_testbed(self, aplist):        
        dictList = self.testbed.get_aps_sym_dict_as_mac_addr_list()
        for ap in aplist :
            if not ap['mac'] in dictList:
                raise Exception("AP[%s] has not connected." % ap['mac'])
                