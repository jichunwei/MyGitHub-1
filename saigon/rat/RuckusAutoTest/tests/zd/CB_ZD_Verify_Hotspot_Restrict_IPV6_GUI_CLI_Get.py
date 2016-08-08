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
from RuckusAutoTest.components.lib.zdcli import configure_hotspot as hotspot

class CB_ZD_Verify_Hotspot_Restrict_IPV6_GUI_CLI_Get(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        logging.info("Verify hotspot profiles between GUI get and CLI get")
        self._compare_hotspot_gui_cli_get()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'hotspot_name': ''}        
        self.conf.update(conf)
        
        self.hotspot_name = self.conf['hotspot_name']
        
        self.gui_get_hotspot_cfg_list = self.carrierbag['existed_hotspot_profile']
        self.cli_get_hotspot_cfg_list = self.carrierbag['cli_hotspot_profile_list']
        
        
        self.zd = self.testbed.components['ZoneDirector']        

        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        pass
    
    def _compare_hotspot_gui_cli_get(self):
        try:
            gui_ipv6_access_list = self._get_ipv6_access_from_cfg_list(self.gui_get_hotspot_cfg_list, self.hotspot_name)
            cli_ipv6_access_dict = self._get_ipv6_access_from_cfg_list(self.cli_get_hotspot_cfg_list, self.hotspot_name)
            
            res = ''
            if gui_ipv6_access_list and cli_ipv6_access_dict:
                res = hotspot.compare_hotspot_restrict_ipv6_gui_cli_get(gui_ipv6_access_list, cli_ipv6_access_dict) 
            else:
                if gui_ipv6_access_list == cli_ipv6_access_dict:
                    res = "No restricted ipv6 access in GUI get and CLI get"
                elif not gui_ipv6_access_list:
                    res = "No restricted ipv6 access in GUI get"
                elif not cli_ipv6_access_dict:
                    res = "No restricted ipv6 access in CLI get"
            
            if res:
                self.errmsg = "Data between GUI get and CLI get are different: %s" % res
        except Exception, e:
            self.errmsg = '[TEST ERROR] %s' % e.message
        
        self.passmsg =  'Hotspot restricted ipv6 access are same between GUI get and CLI get'
        
    def _get_ipv6_access_from_cfg_list(self, hotspot_cfg_list, hotspot_name):
        #Get ipv6 subnet list from gui get hotspot cfg.
        hotspot_name_cfg = {}
        for hotspot_cfg in hotspot_cfg_list:
            if hotspot_cfg['name'] == hotspot_name:
                hotspot_name_cfg = hotspot_cfg
                break
            
        ipv6_access_list = []
        if hotspot_name_cfg:
            if hotspot_name_cfg.has_key('restricted_ipv6_list'):
                ipv6_access_list = hotspot_name_cfg['restricted_ipv6_list']
            elif hotspot_name_cfg.has_key('ipv6_rules'):
                ipv6_access_list = hotspot_name_cfg['ipv6_rules']
            else:
                raise Exception("No ipv6 access in hotspot configuration")
        else:
            raise Exception("No ipv6 access in hotspot configuration")
        
        return ipv6_access_list