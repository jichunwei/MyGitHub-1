'''
Created on Jan 24, 2014

@author: jacky luh
'''

import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.apcli.cli_regex import INCOMPLETE_CMD_MSG, INVALID_CMD_MSG

class CB_ZD_Create_Guest_User_and_Profile(Test):

    required_components = ['ZoneDirector']
    test_parameters = {'guest_access_conf': ''}


    def config(self, conf):
        self._init_test_parameters(conf)

        
    def test(self):
        #verify the invalid email content can not be saved in the zd web page.
        if self.email_format == 'invalid':
            if self._email_content_can_not_save_with_invalid_format(self.invalid_email_content):
                self.passmsg = 'The invalid_email_content warning dialog is shown in the zd web'
                return self.returnResult('PASS', self.passmsg)
            else:
                self.errmsg = 'No found the invalid_email_content warning dialog shown in the zd web'
                return self.returnResult('FAIL', self.errmsg)
            
        #create the local user
        self._create_local_guest_user()
        self._verify_command_execution()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = "Create the guest user and the guest profile successfully"
        return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass


    def _init_test_parameters(self, conf):
        self.guest_access_conf = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180,
                          'username': 'test_local',
                          'password': 'test_local',
                          }   
        if conf.has_key('guest_access_conf'):
            self.guest_access_conf = conf['guest_access_conf']
        elif conf.has_key('g_prof_cfg'):
            self.guest_access_conf = conf['g_prof_cfg']
        else:
            pass
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        if self.guest_access_conf.get('email_content'):
            self.ga_email_content = self.guest_access_conf['email_content']
        else:
            self.ga_email_content = ''
        if conf.get('email_format'):
            self.email_format = conf['email_format']
        else:
            self.email_format = ''
            
        if self.guest_access_conf.get('invalid_email_content'):
            self.invalid_email_content = self.guest_access_conf['invalid_email_content']
        else:
            self.invalid_email_content = ''
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
    
    
    def _create_local_guest_user(self):
        logging.log_info('Configure Local User', 'Execute commands', 'User setting: %s, %s' % (self.test_conf['username'],self.test_conf['password']))
        lib.zdcli.user.create_user(self.zdcli, self.test_conf['username'], password=self.test_conf['password'])
        
        
    def _create_ga_email_content(self, content):
        _email_info = lib.zd.ga.config_ga_email_content(self.zd, content)
        if not _email_info:
            logging.logging.info('Created the guest email content successfully.')
        else:
            raise Exception('The guest email content can not be created.')
        
        
    def _email_content_can_not_save_with_invalid_format(self, invalid_format_content):
        logging.logging.info('try to create the invalid format email content')
        if not invalid_format_content:
            raise Exception('no defined the invalid_format email content')
        _alert = lib.zd.ga.config_ga_email_content(self.zd, invalid_format_content)
        if 'four pairs parentheses' in _alert:
            return True
        else:
            return False
        
    
    def _verify_command_execution(self):
        logging.log_info('Configure Guest Access', 'Execute commands', 'Guest Access setting: %s' % self.guest_access_conf)
        try:
            lib.zdcli.guest_access.config_guest_access(self.zdcli, **self.guest_access_conf)
            time.sleep(2)
            lib.zd.ga.config_ga_email_content(self.zd, self.ga_email_content)            
            time.sleep(3) #waiting for the setting is applied
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
    