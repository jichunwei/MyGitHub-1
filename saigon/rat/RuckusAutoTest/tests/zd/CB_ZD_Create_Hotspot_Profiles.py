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
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Create_Hotspot_Profiles(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._create_hotspot_profiles()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrierbag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'hotspot_profiles_list': [],                     
                    }
        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        

        self.errmsg = ''
        self.passmsg = ''
    
    def _create_hotspot_profiles(self):
        if not self.conf['hotspot_profiles_list']:
            self.errmsg = '[TEST BROKEN] There is not any input parameters for the test'
            return
        try:
            for profile in self.conf['hotspot_profiles_list']:
                lib.zdcli.hotspot.config_hotspot(self.zdcli, **profile)

#            cfg_hs_info_list = lib.zd.wispr.get_profile_info_list(self.zd)
#            cfg_hs_name_list = [tmp['name'] for tmp in cfg_hs_info_list]
#
#            for profile in self.conf['hotspot_profiles_list']:
#                if profile['name'] in cfg_hs_name_list:
#                    lib.zd.wispr.cfg_profile(self.zd, profile['name'], **profile)
#                else:
#                    lib.zd.wispr.create_profile(self.zd, **profile)
#                time.sleep(25)
        except Exception, e:
            self.errmsg = '[TEST ERROR] %s' % e.message
            
        hotspot_name_list = []
        for hotspot_cfg in self.conf['hotspot_profiles_list']:
            hotspot_name_list.append(hotspot_cfg['name'])
        
        self.passmsg =  '[HOTSPOT SERVICE] The Hotspot profile(s) %s is(are) created successfully' % hotspot_name_list
           
    def _retrieve_carribag(self):
        if not self.carrierbag.get('existing_authentication_sers'):
            self.carrierbag['existing_authentication_sers'] = lib.zd.aaa.get_auth_server_info_list(self.zd)
        for exit_auth_serv_info in self.carrierbag['existing_authentication_sers']:
            if self.conf.get('auth_svr') and exit_auth_serv_info['name'] == self.conf['auth_svr']:
                self.auth_svr = self.conf['auth_svr']                 
                self.conf.update({'authentication_server_type': exit_auth_serv_info['type']})
            elif self.conf.get('authentication_server') and exit_auth_serv_info['name'] == self.conf['authentication_server']:
                self.auth_svr = self.conf['authentication_server']
                self.conf.update({'authentication_server_type': exit_auth_serv_info['type']})
            else:
                pass
        
    def _update_carrierbag(self):
#        self.carrierbag['existed_hotspot_profile'] = lib.zd.wispr.get_all_profiles(self.zd)
        pass    