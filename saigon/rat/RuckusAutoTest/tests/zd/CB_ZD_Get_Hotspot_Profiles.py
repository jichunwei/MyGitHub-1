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

class CB_ZD_Get_Hotspot_Profiles(Test):
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
        
        self.zd = self.testbed.components['ZoneDirector']        

        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrierbag(self):
        self.carrierbag['existed_hotspot_profile'] = self.hotspot_cfg_list
    
    def _get_hotspot_profiles(self):
        try:
            hotspot_cfg_list = []
            if self.hotspot_name_list:
                logging.info("Get hotspot profiles for %s via ZD GUI" % self.hotspot_name_list)
                for name in self.hotspot_name_list:
                    logging.info("Get hotspot profile for %s" % name)
                    hotspot_cfg_list.append(lib.zd.wispr.get_profile_by_name(self.zd, name))
            else:
                logging.info("Get all hotspot profiles via ZD GUI")
                hotspot_cfg_list = lib.zd.wispr.get_all_profiles(self.zd)
            
            self.hotspot_cfg_list = hotspot_cfg_list
                
        except Exception, e:
            self.errmsg = 'Get hotspot profiles failed: %s' % e.message
        
        self.passmsg =  'Get hotspot profiles successfully'