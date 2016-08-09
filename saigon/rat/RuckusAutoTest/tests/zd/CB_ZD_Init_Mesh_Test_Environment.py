# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:
    This script support to clean up the mesh testing environment:
    @author: An Nguyen - an.nguyen@ruckuswireless.com
    @since: Oct 2010
    
    Required components:
    Test parameters:
        - task: initial/cleanup
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        - Remove all ZD non default configuration        
    2. Test:
        - if task is clean up the the script will configure the L3 Switch 
          following ZD_Stations test bed to make sure all APs become ROOT   
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import NetgearSwitchRouter

from RuckusAutoTest.tests.zd import Test_Methods as tmethod


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Init_Mesh_Test_Environment(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)
        self._cleanup_non_default_config_on_zd()
        self._define_the_l3_router()

    def test(self):
        if self.conf['task'] == 'cleanup':
            logging.debug('Make all APs become ROOT')
            res, msg = tmethod.emesh.test_all_aps_become_root(**self.mconf)
            if res == 'PASS':
                msg = 'Finished cleanup test environment'
        else:
            res, msg = 'PASS', 'Finished initial test environment'
        return self.returnResult(res, msg)

    def cleanup(self):
        pass
    
    def _init_test_parameters(self, conf):
        self.conf = {'task': 'initial'}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.mconf = {'testbed': self.testbed,
                     }

    def _define_the_l3_router(self):
        self.testbed.components['L3Router'] = NetgearSwitchRouter.NetgearSwitchRouter(self.testbed.components['L3Switch'].conf)

    def _cleanup_non_default_config_on_zd(self):
        logging.info("Remove all configuration on the Zone Director")
        self.zd.remove_all_cfg()