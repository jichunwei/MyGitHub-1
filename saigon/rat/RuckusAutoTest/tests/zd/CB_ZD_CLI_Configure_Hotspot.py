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
            - Go to ZD CLI - Under config-hotspot mode, execute the setting commands.
            - Make sure the command is existed and be used without any issue.
            - Verify the Hotspot information if changed under AP CLI.
            - Verify the Hotspot information is shown correctly on WebUI.

   3. Cleanup:
            - If test case is cleanup, delete the Hotspot rule.

   How it is tested?
"""
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas
from rat.RuckusAutoTest.components.lib.apcli.cli_regex import INCOMPLETE_CMD_MSG,\
    INVALID_CMD_MSG

class CB_ZD_CLI_Configure_Hotspot(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'hotspot_conf': ''}

    def config(self, conf):
        self._init_test_parameters(conf)
        #create aaa server; jluh-2012-08-22
        self._create_authentication_server(conf)
        self._create_accounting_server(conf)
    def test(self):
        if self.test_conf['init_env']:
            return self.returnResult('PASS', 'Testbed is ready for the test.')
        
        if self.test_conf['cleanup']:
            self._delete_hotspot_rule()
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
        self.hotspot_conf = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180,
                          }
        
        if conf.has_key('hotspot_conf'):
            self.hotspot_conf = conf['hotspot_conf']
        
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
        logging.log_info('Configure Hotspot', 'Execute commands', 'Hotspot setting: %s' % self.hotspot_conf)
        try:
            lib.zdcli.hotspot.config_hotspot(self.zdcli, **self.hotspot_conf)
            if self.hotspot_conf.has_key('session_timeout') and self.hotspot_conf['session_timeout']!= 'Disabled':
                self.hotspot_conf['session_timeout'] = 'Enabled'
                
            time.sleep(5) #waiting for the setting is applied
            self.passmsg = 'The configure set %s is configured successfully. ' % self.hotspot_conf
            
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
    
    def _verify_setting_under_zd_cli(self):
        logging.log_info('Verify under ZD CLI mode', 'Hotspot', 'Expected setting: %s' % self.hotspot_conf)
        zdcli_info = lib.zdcli.hotspot.show_config_hotspot(self.zdcli, self.hotspot_conf['name'])
        zdcli_info = zdcli_info['hotspot'].values()[0].values()[0]
        logging.log_info('', '', zdcli_info)
        
        if self.hotspot_conf.has_key('idle_timeout'):
            grace_period = self.hotspot_conf.pop('idle_timeout')
            if grace_period == 'Disabled':
                if zdcli_info['grace_period']['status'] != 'Disabled':
                    self.errmsg = 'Grace period in CLI is: %s, instead of: %s' \
                    % (zdcli_info['grace_period'], self.hotspot_conf['idle_timeout'])
                    return
                
            elif grace_period:
                if zdcli_info['grace_period']['status'] != 'Enabled' \
                or zdcli_info['grace_period']['period'] != '%s Minutes' % grace_period:
                    self.errmsg = 'Grace period in CLI is: %s, set info is: %s\n' % (zdcli_info['grace_period'], self.hotspot_conf['idle_timeout'])
                    return
                       
        for key in self.hotspot_conf.keys():
            if key not in zdcli_info.keys():
                continue
            
            #@author: Jane.Guo @since: 2013-7-30 fix bug to support the value is empty.
            if self.hotspot_conf.get(key) == None:
                continue
            
            e_value = self.hotspot_conf[key]
            a_value = zdcli_info[key]
            
            if type(e_value) == bool:
                if e_value:
                    e_value = 'Enabled'
                else:
                    e_value = 'Disabled'
            logging.log_info('','','key %s:set is %s, get is %s'%(key, e_value, a_value))                      
            #zj 2014-0214  fixed because of no "http://"  but "https://"  in e_value -- Login Page
            if "http://" in e_value or "https://" in e_value :
#            if "http://" in e_value:
                pass
            else:
                e_value = e_value.split('.')[0]                      

            if type(a_value) is dict and 'status' in a_value.keys():
                a_val = a_value['status']
                if e_value != a_val:
                    self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zdcli_info[key], self.hotspot_conf[key])
                    return
                else:
                    continue
            elif type(a_value) is dict and 'server' in a_value.keys():
                a_val = a_value['server']
                if e_value != a_val:
                    self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zdcli_info[key], self.hotspot_conf[key])
                    return
                else:
                    continue             
            elif e_value not in a_value:                                
                self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zdcli_info[key], self.hotspot_conf[key])
                return
        
        self.passmsg += 'The Hotspot setting %s is shown correctly under ZD CLI. ' % self.hotspot_conf
     
    
    def _verify_setting_on_zd_webui(self):
        logging.log_info('Verify under ZD WebUI', 'Hotspot', 'Expected setting: %s' % self.hotspot_conf)
        zd_info = lib.zd.wispr.get_profile_by_name(self.zd, self.hotspot_conf['name'])
        logging.log_info('', '', zd_info)
        map = {'name': 'name',
               'login_page_url': 'login_page',               
               'accounting_server': 'acct_svr',
               'authentication_server': 'auth_svr',
               'location_id': 'radius_location_id',
               'location_name': 'radius_location_name',
               'idle_timeout': 'idle_time',
               }
 
        for key in self.hotspot_conf.keys():
            if 'walled_garden' in key:
                #@author: Jane.Guo @since: 2013-7-30 fix bug to compare two list.
                #set info is ['192.168.0.252','192.168.0.253'] get info is [u'192.168.0.252', u'192.168.0.253']
                set_list = self.hotspot_conf[key]
                walled_list = zd_info['walled_garden_list']
                for i in range(len(walled_list)):
                    walled_list[i] = str(walled_list[i])
                
                set_list.sort()
                walled_list.sort()               
                if not cmp(set_list,walled_list) == 0:
                    self.errmsg = 'The value "%s" is "%s" not show in WebUI %s' % (key, set_list,
                                                                                 walled_list)
                continue
            
            if key not in map.keys():
                continue
            
            if map[key] not in zd_info.keys():
                continue
            #zj 2014-0214  fixed because of no "http://"  but "https://"  in e_value -- Login Page
#            if "http://" in zd_info[map[key]]:
            if "http://" in zd_info[map[key]] or "https://" in zd_info[map[key]] :
                pass
            else:
                zd_info[map[key]] = zd_info[map[key]].split('.')[0]
                
            if zd_info[map[key]] != self.hotspot_conf[key]:
                self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zd_info[map[key]], self.hotspot_conf[key])
                return
            
        self.passmsg += 'The Hotspot setting %s is shown correctly on WebUI.' % self.hotspot_conf
    
    def _delete_hotspot_rule(self):
        logging.log_info('Delete', 'Hotspot', 'Expected setting: %s' % self.hotspot_conf)
        lib.zdcli.hotspot.delete_a_hotspot(self.zdcli, self.hotspot_conf['name'])
        
        self.passmsg = 'The rule %s is deleted.' % self.hotspot_conf['name']
        
    def _create_authentication_server(self, conf):
        if conf.has_key('auth_server_cfg') and conf['auth_server_cfg']:
            cas.configure_aaa_servers(self.zdcli, [conf['auth_server_cfg']])
            
    def _create_accounting_server(self, conf):
        if conf.has_key('acct_server_cfg') and conf['acct_server_cfg']:
            cas.configure_aaa_servers(self.zdcli, [conf['acct_server_cfg']])
            
            
