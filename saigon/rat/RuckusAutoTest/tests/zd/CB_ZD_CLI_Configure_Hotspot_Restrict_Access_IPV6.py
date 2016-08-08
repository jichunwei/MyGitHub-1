# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
            - Prepare a testbed with ZD and APs under ZD control.
   2. Test:
            - Go to ZD CLI - Under config_hotspot_restrict_access mode, execute the setting commands.
            - Make sure the command is existed and be used without any issue.
            - Verify the Hotspot Restrict Access information if changed under AP CLI.
            - Verify the Hotspot Restrict Access information is shown correctly on WebUI.

   3. Cleanup:
            - If test case is cleanup, delete the Hotspot Restrict Access rule.

   How it is tested?
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Configure_Hotspot_Restrict_Access_IPV6(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'hotspot_restrict_access_list': ''}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        if self.conf['init_env']:
            return self.returnResult('PASS', 'Testbed is ready for the test.')
        if self.conf['cleanup']:
            self._delete_hotspot_rule()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            return self.returnResult('PASS', self.passmsg)
        
        if self.conf['test'] == 'delete':
            self._delete_hotspot_restrict_access_rule()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            return self.returnResult('PASS', self.passmsg)
        
        self._update_hotspot_ipv6_access_list()
        if not self.errmsg:
            self._verify_setting_under_zd_cli()
            
        self.passmsg = "Configure hotspot restricted ipv6 access successfully and data are same between set and get"
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'pass_expected': True,
                     'cleanup': False,
                     'init_env': False,
                     'time_out': 180,
                     'hotspot_name': '',
                     'test':''}
        
        self.conf.update(conf)
        
        self.hotspot_restrict_access_list = []
        if self.conf.has_key('hotspot_restrict_access_list'):
            self.hotspot_restrict_access_list = self.conf['hotspot_restrict_access_list']
            
        self.hotspot_name = self.conf['hotspot_name']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
        if self.conf['init_env']:
            default_hotspot_cfg = {'name': self.conf['hotspot_name'],
                                   'login_page_url': conf['login_page_url']}
            lib.zdcli.hotspot.config_hotspot(self.zdcli, **default_hotspot_cfg)
        if self.conf['cleanup']:
            pass
    
    def _update_carrier_bag(self):
        self.carrierbag['cli_hotspot_profile_list']= self.cli_hotspot_profile_list
    
    def _update_hotspot_ipv6_access_list(self):
        logging.info('Configure Hotspot Restrict IPV6 Access List Setting: %s' % self.hotspot_restrict_access_list)
        res_dict = {}        
        for ipv6_access in self.hotspot_restrict_access_list:
            result, errmsg = lib.zdcli.hotspot.config_hotspot_restrict_access_ipv6(self.zdcli,
                                                                             self.hotspot_name, 
                                                                             ipv6_access['order'],
                                                                             **ipv6_access)
            if not result:
                res_dict[ipv6_access['order']] = errmsg
            
        time.sleep(5) #waiting for the setting is applied
        if res_dict:
            self.errmsg = "Configure Hotspot IPV6 access failed"
            logging.warning("Configure Hotspot IPV6 access faile:%s" % (res_dict))
        
    def _verify_setting_under_zd_cli(self):
        logging.info("Verify hotspot restricted ipv6 access between set and get")
        cli_hotspot_profile = lib.zdcli.hotspot.show_config_hotspot(self.zdcli, self.conf['hotspot_name'])
        self.cli_hotspot_profile_list = cli_hotspot_profile['hotspot']['id'].values()
        
        get_ipv6_access_dict = self.cli_hotspot_profile_list[0].get('ipv6_rules')
        
        if not get_ipv6_access_dict:
            self.errmsg = '[Verify under ZD CLI mode] There is no IPV6 rule in list'
        else:
            logging.info("Compare data between CLI set and CLI get")
            cli_get_ipv6_access_list = self._get_ipv6_access_from_cfg_list(self.cli_hotspot_profile_list, self.conf['hotspot_name'])
            cli_set_ipv6_access_list = self.hotspot_restrict_access_list
            
            if cli_get_ipv6_access_list and cli_set_ipv6_access_list:
                res = lib.zdcli.hotspot.compare_hotspot_restrict_ipv6_cli_set_get(cli_set_ipv6_access_list, cli_get_ipv6_access_list)
            else:
                if cli_get_ipv6_access_list == cli_set_ipv6_access_list:
                    res = "No restricted ipv6 access in CLI set and get"
                elif not cli_get_ipv6_access_list:
                    res = "No restricted ipv6 access in CLI Get"
                elif not cli_set_ipv6_access_list:
                    res = "No restricted ipv6 access in CLI Set"
            if res:
                self.errmsg = "Data between CLI set and get are different: %s" % res
                
    def _get_ipv6_access_from_cfg_list(self, hotspot_cfg_list, hotspot_name):
        #Get ipv6 subnet list from gui get hotspot cfg.
        hotspot_name_cfg = {}
        for hotspot_cfg in hotspot_cfg_list:
            if hotspot_cfg['name'] == hotspot_name:
                hotspot_name_cfg = hotspot_cfg
                break
            
        ipv6_access_list = []
        if hotspot_name_cfg.has_key('restricted_ipv6_list'):
            ipv6_access_list = hotspot_name_cfg['restricted_ipv6_list']
        elif hotspot_name_cfg.has_key('ipv6_rules'):
            ipv6_access_list = hotspot_name_cfg['ipv6_rules']
        else:
            raise Exception("No ipv6 access in hotspot configuration")
        
        return ipv6_access_list
         
    def _delete_hotspot_restrict_access_rule(self):
        logging.info('Delete Hotspot Restrict IPV6 Access rule')
        lib.zdcli.hotspot.delete_a_hotspot_restrict_access_ipv6(self.zdcli, self.conf['hotspot_name'],
                                                           self.hotspot_restrict_access_list['order'])
        
        self.passmsg = 'The rule %s is deleted.' % self.hotspot_restrict_access_list
    
    def _delete_hotspot_rule(self):
        logging.info('Delete Hotspot %s via ZD CLI' % self.conf['hotspot_name'])
        lib.zdcli.hotspot.delete_a_hotspot(self.zdcli, self.conf['hotspot_name'])
        
        self.passmsg = 'The rule %s is deleted.' % self.conf['hotspot_name']
        
    def _convert_list_to_dict(self, cfg_list, key_name):
        '''
        Convert server cfg list to dict, key is server name.
        '''     
        cfg_dict = {}
        
        for cfg in cfg_list:
            cfg_dict[cfg[key_name]] = cfg
        
        return cfg_dict