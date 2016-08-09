# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get Current ZD device IP setting via GUI
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If get device IP setting successfully 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import hotspot_services_zd as hotspot

class CB_ZD_Verify_Hotspot_Restrict_IPV6_GUI_Set_Get(Test):
    required_components = []
    parameter_description = {'hotspot_cfg_list': 'Hotspot configuration list'}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        logging.info("Verify hotspot profiles between GUI set and GUI get")
        self._compare_hotspot_gui_set_get()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ipv6_access_list': [],
                     'hotspot_name': None,}
        self.conf.update(conf)
        
        self.hotspot_name = self.conf['hotspot_name']
        self.set_ipv6_access_list = self.conf['ipv6_access_list']
        self.get_hotspot_cfg_list = self.carrierbag['existed_hotspot_profile']

        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        pass
    
    def _compare_hotspot_gui_set_get(self):
        try:
            logging.debug("GUI get hotspot cfg: %s" % self.get_hotspot_cfg_list)
            gui_ipv6_access_list = self._get_ipv6_access_from_cfg_list(self.get_hotspot_cfg_list, self.hotspot_name)
            
            if gui_ipv6_access_list and self.set_ipv6_access_list:
                res = hotspot.compare_hotspot_restricted_ipv6_access_gui_set_get(self.set_ipv6_access_list, gui_ipv6_access_list)
            else:
                if gui_ipv6_access_list == self.set_ipv6_access_list:
                    res = "No restricted ipv6 access in GUI set and get"
                elif not gui_ipv6_access_list:
                    res = "No restricted ipv6 access in GUI Get"
                elif not self.set_ipv6_access_list:
                    res = "No restricted ipv6 access in GUI Set"
            
            if res:
                self.errmsg = "Data between set and get are different: %s" % res
            
        except Exception, e:
            self.errmsg = '[TEST ERROR] %s' % e.message
        
        self.passmsg =  'Hotspot restricted ipv6 access are same between GUI set and GUI get'
        
    def _get_ipv6_access_from_cfg_list(self, hotspot_cfg_list, hotspot_name):
        #Get ipv6 subnet list from gui get hotspot cfg.
        gui_get_hotspot_cfg = {}
        for hotspot_cfg in hotspot_cfg_list:
            if hotspot_cfg['name'] == hotspot_name:
                gui_get_hotspot_cfg = hotspot_cfg
                break
        gui_ipv6_access_list = gui_get_hotspot_cfg.get('restricted_ipv6_list')
        
        return gui_ipv6_access_list