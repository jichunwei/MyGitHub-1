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

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Configure_Hotspot_Restrict_Access(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'hotspot_restrict_access_conf': ''}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        if self.test_conf['init_env']:
            return self.returnResult('PASS', 'Testbed is ready for the test.')
        
        if self.test_conf['cleanup']:
            self._delete_hotspot_rule()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            return self.returnResult('PASS', self.passmsg)
        
        if self.test_conf['test'] == 'delete':
            self._delete_hotspot_restrict_access_rule()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            return self.returnResult('PASS', self.passmsg)
        
        self._verify_command_execution()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_under_zd_cli()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_on_zd_webui()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.hotspot_restrict_access_conf = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180,
                          'hotspot_name': '',
                          'test':''}
        
        if conf.has_key('hotspot_restrict_access_conf'):
            self.hotspot_restrict_access_conf = conf['hotspot_restrict_access_conf']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
        if self.test_conf['init_env']:
            lib.zdcli.hotspot.config_hotspot(self.zdcli, **{'name': self.test_conf['hotspot_name'],
                                                            'login_page_url': conf['login_page_url']})
        
        if self.test_conf['cleanup']:
            pass
    
    def _verify_command_execution(self):
        name = self.test_conf['hotspot_name']
        order = self.hotspot_restrict_access_conf['order']
        cfg = self.hotspot_restrict_access_conf
        logging.log_info('Configure Hotspot Restrict Access', 'Execute commands', 'Hotspot Restrict Access setting: %s' % cfg)
        try:
            lib.zdcli.hotspot.config_hotspot_restrict_access(self.zdcli, name, order, **cfg)
            time.sleep(5) #waiting for the setting is applied
        except Exception, e:
            import traceback
            logging.logging.error(traceback.format_exc())
            self.errmsg = e.message

        self.passmsg = 'Configure hotspot restrict access %s DONE' % name 
        
    def _verify_setting_under_zd_cli(self):
        logging.log_info('Verify under ZD CLI mode', 'Hotspot Restrict Access', 'Expected setting: %s' % self.hotspot_restrict_access_conf)
        zdcli_info = lib.zdcli.hotspot.get_expected_hotspot_config_info(self.zdcli, self.test_conf['hotspot_name'])
        zdcli_info = zdcli_info.get('ipv4_rules')
        if not zdcli_info:
            self.errmsg = '[Verify under ZD CLI mode] There is no IPV4 rule in list'
            return
             
        logging.log_info('HOTSPOT RESTRICTED INFO', 'ZD CLI', zdcli_info)
        rule = zdcli_info.get(self.hotspot_restrict_access_conf['order'])
        if not rule:
            self.errmsg = '[Verify under ZD CLI mode] There is no rule order %s in list' % self.hotspot_restrict_access_conf['order']

        for key in self.hotspot_restrict_access_conf.keys():
            if key not in rule.keys():
                continue
            if rule[key].lower() != self.hotspot_restrict_access_conf[key].lower():
                self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, rule[key], self.hotspot_restrict_access_conf[key])
                return
                  
        self.passmsg += 'The Hotspot Restrict Access setting %s is shown correctly under ZD CLI. ' % self.hotspot_restrict_access_conf     
        return
         
    def _verify_setting_on_zd_webui(self):
        logging.log_info('Verify under ZD WebUI', 'Hotspot Restrict Access', 'Expected setting: %s' % self.hotspot_restrict_access_conf)
        zd_info = lib.zd.wispr.get_profile_by_name(self.zd, self.test_conf['hotspot_name'])
        zd_info = zd_info['restricted_subnet_list']
        
        logging.log_info('HOTSPOT RESTRICTED INFO', 'ZD WEBUI', zd_info)
        for rule in zd_info:
            if rule['order'] != self.hotspot_restrict_access_conf['order']:
                continue
            for key in self.hotspot_restrict_access_conf.keys():
                if key not in rule.keys():
                    continue
                if self.hotspot_restrict_access_conf[key].lower() not in rule[key].lower():
                    self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, rule[key], self.hotspot_restrict_access_conf[key])
                    return
        
            self.passmsg += 'The Hotspot Restrict Access setting %s is shown correctly on WebUI.' % self.hotspot_restrict_access_conf
            return
        
        self.errmsg = 'There is no rule order %s in list' % self.hotspot_restrict_access_conf['order']
        
    def _delete_hotspot_restrict_access_rule(self):
        logging.log_info('Delete', 'Hotspot Restrict Access', 'Expected setting: %s' % self.hotspot_restrict_access_conf)
        lib.zdcli.hotspot.delete_a_hotspot_restrict_access(self.zdcli, self.test_conf['hotspot_name'],
                                                           self.hotspot_restrict_access_conf['order'])
        
        self.passmsg = 'The rule %s is deleted.' % self.hotspot_restrict_access_conf
    
    def _delete_hotspot_rule(self):
        logging.log_info('Delete', 'Hotspot', 'Expected setting: %s' % self.test_conf['hotspot_name'])
        lib.zdcli.hotspot.delete_a_hotspot(self.zdcli, self.test_conf['hotspot_name'])
        
        self.passmsg = 'The rule %s is deleted.' % self.test_conf['hotspot_name']
