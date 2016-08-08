# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""
    Description: This script support to create one or multiple Hotspot profiles in ZD WebUI.
    @author: An Nguyen - an.nguyen@ruckuswireless.com
    @since: May 2011

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Get_Hotspot_Profiles(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._get_hotspot_profiles()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrierbag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'hotspot_name_list': [],                     
                    }
        
        self.conf.update(conf)
        
        self.hotspot_name_list = self.conf['hotspot_name_list']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        

        self.errmsg = ''
        self.passmsg = ''
    
    def _get_hotspot_profiles(self):
        try:
            hotspot_cfg_list = []
            if self.hotspot_name_list:
                logging.info("Get hotspot profiles for %s via ZD CLI" % self.hotspot_name_list)
                for name in self.hotspot_name_list:
                    hotspot_cfg = lib.zdcli.hotspot.show_config_hotspot(self.zdcli, name)
                    hotspot_cfg_list.extend(hotspot_cfg['hotspot']['id'].values())
            else:
                logging.info("Get all hotspot profiles via ZD CLI")
                hotspot_cfg_list = lib.zdcli.hotspot.show_all_hotspot(self.zdcli)['hotspot']['id'].values()
            
            self.hotspot_cfg_list = hotspot_cfg_list
                
        except Exception, e:
            self.errmsg = '[TEST ERROR] %s' % e.message
        
        self.passmsg =  'Get hotspot profiles successfully via ZD CLI'
        
    def _update_carrierbag(self):
        self.carrierbag['cli_hotspot_profile_list'] = self.hotspot_cfg_list