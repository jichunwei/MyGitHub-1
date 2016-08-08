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
            - Go to ZD CLI - Under config-guest_restrict_access mode, execute the setting commands.
            - Make sure the command is existed and be used without any issue.
            - Verify the Guest Restrict Access information if changed under AP CLI.
            - Verify the Guest Restrict Access information is shown correctly on WebUI.

   3. Cleanup:
            - If test case is cleanup, delete the guest restrict access rule.

   How it is tested?
"""
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib
from rat.RuckusAutoTest.components.lib.apcli.cli_regex import INCOMPLETE_CMD_MSG,\
    INVALID_CMD_MSG

class CB_ZD_CLI_Configure_Guest_Restrict_Access(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'guest_restrict_conf': ''}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        if self.test_conf['init_env']:
            return self.returnResult('PASS', 'Testbed is ready for the test.')
        
        if self.test_conf['cleanup'] or self.test_conf['test'].lower() == 'delete':
            self._delete_guest_restrict_access_rule()
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
        self.guest_restrict_conf = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'test': '',
                          'init_env': False,
                          'time_out': 180}
        #@author: Liang Aihua,@since: 2015-1-14,@change: zf-11551 for configure params: {'guest_restrict_conf': {'order': '2'}}
        #*************************
        if conf.has_key('guest_restrict_conf'):
            if len(conf['guest_restrict_conf']) == 1 or conf['guest_restrict_conf'].has_key(str(conf['guest_restrict_conf']['order'])):
                self.guest_restrict_conf.update(conf['guest_restrict_conf'])
            else:
                self.guest_restrict_conf['order']= conf['guest_restrict_conf']['order']
                conf['guest_restrict_conf'].pop('order')
                self.guest_restrict_conf[str(self.guest_restrict_conf['order'])]=conf['guest_restrict_conf']
        #*******************************************
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
        if self.test_conf['init_env']:
            #changed by Liang Aihua on 2015-1-14
            lib.zdcli.guest_access.config_guest_access(self.zdcli)
        
        if self.test_conf['cleanup']:
            lib.zdcli.guest_access.delete_all_guest_access_profiles(self.zdcli)
    
    def _verify_command_execution(self):
        logging.log_info('Configure Guest Restrict Access', 'Execute commands', 'Guest Restrict Access setting: %s' % self.guest_restrict_conf)
        try:
           
            #@author: Liang Aihua,@since: 2015-1-14,@change: zf-11551 for configure params: {'guest_restrict_conf': {'order': '2'}}
            #****************************
            if len(self.guest_restrict_conf)== 1:
                lib.zdcli.guest_access.config_guest_restrict_access(self.zdcli, self.guest_restrict_conf['order'])
            else:
                #@author: Jane.Guo @since: 2013-08 fix bug, the parameter is wrong
                lib.zdcli.guest_access.config_guest_restrict_access(self.zdcli, self.guest_restrict_conf['order'],
                                                                **self.guest_restrict_conf[str(self.guest_restrict_conf['order'])])
            #*****************************************
            
            time.sleep(5) #waiting for the setting is applied
            self.passmsg = 'The configure set %s is configured successfully. ' % self.guest_restrict_conf
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
        logging.log_info('Verify under ZD CLI mode', 'Guest Restrict Access', 'Expected setting: %s' % self.guest_restrict_conf)
        zdcli_info = lib.zdcli.guest_access.show_config_guest_access(self.zdcli)
        #@author: Jane.Guo @since: 2013-10 adapt to 9.8 Guest Access improvement  
        zdcli_info = zdcli_info['guest_access']['restricted_subnet_access']['rules']
        logging.log_info('', '', zdcli_info)
        
        #Behavior change
        #@author: Jane.Guo @since: 2013-08 support change the rule's order
        # self.guest_restrict_conf {'order': '2','2':{'destination_address': '192.168.0.0/16', 'type': 'Allow','order':'1'}} 
        #zdcli_info {'1': {'protocol': 'Any', 'destination_port': 'Any', 'type': 'Allow', 'destination_address': '192.168.0.0/16', 'description': ''}}
        for order in zdcli_info.keys():
            #@author: Liang Aihua,@since: 2015-1-14,@change: zf-11551 for configure params: {'guest_restrict_conf': {'order': '2'}}
            #***********************
            if self.guest_restrict_conf.has_key(str(self.guest_restrict_conf['order'])):
                change_order = self.guest_restrict_conf[str(self.guest_restrict_conf['order'])].get('order')
            else:
                change_order = ''
            #**************************************
            
            if change_order:
                if int(order) != int(change_order):
                    continue
            else:
                if int(order) != int(self.guest_restrict_conf['order']):
                    continue

            get_rule = zdcli_info[order]
            
            #@author: Liang Aihua,@since: 2015-1-14,@change: zf-11551 for configure params: {'guest_restrict_conf': {'order': '2'}}
            #***********************
            set_rule = self.guest_restrict_conf.get(str(self.guest_restrict_conf['order']))           
            if set_rule:
                for key in set_rule.keys():
                    if key == 'order':
                        continue
                    if key not in get_rule.keys():
                        continue
                    if set_rule[key].lower() != get_rule[key].lower():
                        self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, get_rule[key].lower(), set_rule[key].lower())
                        return
            #*******************************************
                
            self.passmsg += 'The guest restrict access setting %s is shown correctly under ZD CLI. ' % self.guest_restrict_conf
            return
                        
        self.errmsg = 'There is no information for rule %s' % self.guest_restrict_conf
    
    def _verify_setting_on_zd_webui(self):
        logging.log_info('Verify under ZD WebUI', 'Guest Restrict Access', 'Expected setting: %s' % self.guest_restrict_conf)
        
        #@author: Liang Aihua,@since: 2015-1-14,@change: zf-11551 for configure params: {'guest_restrict_conf': {'order': '2'}}
        #*********************
        if self.guest_restrict_conf.has_key(str(self.guest_restrict_conf['order'])):
            #@author: Jane.Guo @since: 2013-08 support change the rule's order
            change_order = self.guest_restrict_conf[str(self.guest_restrict_conf['order'])].get('order')
        else:
            change_order = ''
        #******************************
            
        if change_order:
            zdcli_info = lib.zd.ga.get_restricted_subnet_entry(self.zd, str(change_order))
        else:
            zdcli_info = lib.zd.ga.get_restricted_subnet_entry(self.zd, self.guest_restrict_conf['order'])
        logging.log_info('', '', zdcli_info)
        map = {'order': 'order', 
               'description': 'description', 
               'type': 'action', 
               'destination_address': 'dst_addr',
               'protocol': 'protocol',
               'destination_port': 'dst_port'}
        
        #@author: Liang Aihua,@since: 2015-1-14,@change: zf-11551 for configure params: {'guest_restrict_conf': {'order': '2'}}
        #*********************
        set_rule = self.guest_restrict_conf.get(str(self.guest_restrict_conf['order']))
        if set_rule:
            for key in set_rule.keys():
                if not map.has_key(key):
                    continue
                elif map[key] not in zdcli_info.keys():
                    continue
                if key == 'protocol' and set_rule[key].lower()!='any':
                    import re
                    b=re.search("\d",zdcli_info[map[key]]) 
                    zdcli_info[map[key]]=b.group(0)   
                if zdcli_info[map[key]].lower() != set_rule[key].lower():
                    self.errmsg = 'The value "%s" is "%s" instead of "%s"' % (key, zdcli_info[map[key]], set_rule[key])
                    return
        #****************************************
       
        self.passmsg += 'The guest restrict access setting %s is shown correctly on WebUI.' % self.guest_restrict_conf
    
    def _delete_guest_restrict_access_rule(self):
        logging.log_info('Delete', 'Guest Restrict Access', 'Expected setting:' % self.guest_restrict_conf)
        lib.zdcli.guest_access.delete_a_guest_restrict_access(self.zdcli, self.guest_restrict_conf['order'])
        
        self.passmsg = 'The rule %s is deleted.' % self.guest_restrict_conf