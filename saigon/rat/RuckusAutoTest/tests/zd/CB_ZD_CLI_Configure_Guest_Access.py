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
            - Go to ZD CLI - Under config-guest_access mode, execute the setting commands.
            - Make sure the command is existed and be used without any issue.
            - Verify the Guset Access information if changed under AP CLI.
            - Verify the Guset Access information is shown correctly on WebUI.

   3. Cleanup:
            - If test case is cleanup, return.

   How it is tested?
"""
import time

from RuckusAutoTest.components import Helpers
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib
from rat.RuckusAutoTest.components.lib.apcli.cli_regex import INCOMPLETE_CMD_MSG,\
    INVALID_CMD_MSG

class CB_ZD_CLI_Configure_Guest_Access(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'guest_access_conf': ''}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        if self.test_conf['init_env']:
            return self.returnResult('PASS', 'Testbed is ready for the test.')
        
        if self.test_conf['cleanup']:  
            Helpers.zdcli.guest_access.delete_all_guest_access_profiles(self.zdcli)#@author:yuyanan @since:2015-1-4 @change:clean up guest access
            return self.returnResult('PASS', '')
        
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
        self.guest_access_conf = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180}
        
        if conf.has_key('guest_access_conf'):
            self.guest_access_conf = conf['guest_access_conf']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
        if self.test_conf['init_env']:
            pass
        
        if self.test_conf['cleanup']:
            pass
    
    def _verify_command_execution(self):
        logging.log_info('Configure Guest Access', 'Execute commands', 'Guest Access setting: %s' % self.guest_access_conf)
        try:
            lib.zdcli.guest_access.config_guest_access(self.zdcli, **self.guest_access_conf)            
            time.sleep(5) #waiting for the setting is applied
            self.passmsg = 'The configure set %s is configured successfully. ' % self.guest_access_conf
        except Exception, e:
            self._verify_exception_msg(e)
    
    def _verify_exception_msg(self, e):
        if INVALID_CMD_MSG in e.message:
            msg = '[INVALID COMMAND] %s' % e.message
            if self.test_conf['pass_expected']:
                self.errmsg = msg
            else:
                self.passmsg += '[CORRECT BEHAVIOR]%s. ' % msg
            return
           
        if INCOMPLETE_CMD_MSG in e.message:
            msg = '[INCOMPLETE COMMAND] %s' % e.message
            if self.test_conf['pass_expected']:
                self.errmsg = msg
            else:
                self.passmsg += '[CORRECT BEHAVIOR]%s. ' % msg
            return
        
        raise Exception, e
    
    def _resolve_dict(self, guest_access_info_cli_dict):
        for key in guest_access_info_cli_dict:
            if key in ["authentication", "redirection", "validity_period"]:
                guest_access_info_cli_dict[key] = guest_access_info_cli_dict[key]['mode']
            
            if key == "terms_of_use":
                guest_access_info_cli_dict[key] = guest_access_info_cli_dict[key]['status']
                
    
    def _verify_setting_under_zd_cli(self):
        logging.log_info('Verify under ZD CLI mode', 'Guest Access', 'Expected setting: %s' % self.guest_access_conf)
        
        #@author: yanan.yu @since: 2015-4-16 @change: adapt to 9.10 self-service guestpass
        if self.guest_access_conf.get("name"):
            zdcli_info = lib.zdcli.guest_access.show_config_guest_access(self.zdcli,self.guest_access_conf.get("name"))['guest_access']
        else:
            zdcli_info = lib.zdcli.guest_access.show_config_guest_access(self.zdcli)['guest_access']
        
        self._resolve_dict(zdcli_info)
        
        for key in self.guest_access_conf.keys():
            if key not in zdcli_info.keys():
                continue
            
            expect = self.guest_access_conf[key]
            actual = zdcli_info[key]
            
            if type(expect)== type('str') and type(actual) == type('str'):
                # don't need to verify the '.' - remove the '.' at end of line.
                if zdcli_info[key].strip('.') != self.guest_access_conf[key].strip('.'):
                    self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zdcli_info[key], self.guest_access_conf[key])
                    return
            elif type(expect)==dict and type(actual)== dict:
                for subkey in expect.keys():
                    if subkey not in actual.keys():
                        continue
                    if actual[subkey] != expect[subkey]:
                        self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (subkey, actual[subkey], expect[subkey])
            else:
                if actual != expect:
                    self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zdcli_info[key], self.guest_access_conf[key])
                    return
        #@author: yanan.yu @since: 2015-3-24 @change: adapt to 9.10 self-service guestpass
        
        self.passmsg += 'The guest access setting is shown correctly under ZD CLI. ' 
     
    
    def _verify_setting_on_zd_webui(self):
        logging.log_info('Verify under ZD WebUI', 'Guest Access', 'Expected setting: %s' % self.guest_access_conf)
        
        #@author: yanan.yu @since: 2015-4-16 @change: adapt to 9.10 self-service guestpass
        if self.guest_access_conf.get("name"):
            zdcli_info = lib.zd.ga.get_guest_access_config(self.zd,guest_access_name = self.guest_access_conf.get("name"))
        else:  
            zdcli_info = lib.zd.ga.get_guest_access_config(self.zd)
       
        for key in self.guest_access_conf.keys():
            if key not in zdcli_info.keys():
                continue
            # don't need to verify the '.' - remove the '.' at end of line.
            if zdcli_info[key].strip('.') != self.guest_access_conf[key].strip('.'):
                self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zdcli_info[key], self.guest_access_conf[key])
                return
        
        self.passmsg += 'The guest access setting is shown correctly on WebUI.'