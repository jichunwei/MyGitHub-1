'''
Created on Jan 24, 2014

@author: jacky luh
'''
import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Generate_Guest_Pass_with_Email(Test):
    '''
    create the guestaccess policy on zd
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._clean_up_email_inbox('/home/%s/Maildir/new' % self.dest_email.split('@')[0])
        
        
    def test(self):
        logging.info("Generate a Guest Pass on the ZD")
        self._generate_guest_pass_info()    
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        #Jluh@20140428 updated by the 9.8 changed
        if self.dest_email and not self.passmsg:
            self.passmsg = "Generate the guestpass email successufully."
        elif not self.dest_email and not self.passmsg:
            self.passmsg = "Generate the guestpass successufully."
        else:
            pass
        logging.info(self.passmsg)
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)

               
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        if conf.has_key('use_static_key') and conf['use_static_key']:
            self.key = utils.make_random_string(16, type = "alnum")
        else:
            self.key = ""
        
        self.generate_guestpass_cfg = {'type':'single',
                                       'guest_fullname':'',
                                       'duration':'',
                                       'duration_unit': '',
                                       'wlan': '',
                                       'remarks': '',
                                       'profile_file': os.getcwd()+'\\RuckusAutoTest\\tests\\zd\\lib\\batch_guestpass.csv',
                                       'key': self.key,
                                       'is_shared': 'No',
                                       'auth_ser': 'Local Database',
                                       'username': 'test_local',
                                       'password': 'test_local'}
        
        self.multi_expect_gp_cfg = dict()
        if conf.get('g_pass_cfg'):
            self.generate_guestpass_cfg.update(conf['g_pass_cfg'])
        else:
            raise Exception("Not found the guest pass config in the test case param")
        
        #updated by jluh, since@2014-07-03
        if conf.get('multi_expe_gp_cfg'):
            self.multi_expect_gp_cfg.update(conf['multi_expe_gp_cfg'])
        else:
            raise Exception("Not found the multi expect guest pass config in the test case param")
        
        self.zd = self.testbed.components['ZoneDirector']
        self.linux = self.testbed.components['LinuxServer']
        
        #delete the exist guest pass at first.
        ga.delete_all_guestpass(self.zd)
        
        self.email_format_error_text = 'email address is invalid'
        if conf.get('email_format') and conf['email_format'] == 'invalid':
            self.email_invalid_format = conf['email_format']
            self.generate_guestpass_cfg['profile_file'] = os.getcwd()+'\\RuckusAutoTest\\tests\\zd\\lib\\batch_guestpass_email_invalid_format.csv'
        else:
            self.email_invalid_format = ''
        
        self.dest_email = self.generate_guestpass_cfg['email']
        self.gp_type = self.generate_guestpass_cfg['type']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _update_carrier_bag(self):
        if self.generate_guestpass_cfg['type'] == 'single':
            self.carrierbag['guest_pass'] = self.guest_pass_info['single_gp']['guest_pass']
            self.carrierbag['gp_expired_time'] = self.guest_pass_info['single_gp']['expired_time']
            self.carrierbag['guest_fullname'] = self.guest_pass_info['single_gp']['guest_name']
            self.carrierbag['single_gp'] = self.guest_pass_info['single_gp']
        #updated by jluh, since@2014-07-03
        elif self.generate_guestpass_cfg['type'] == 'multiple':
            self.carrierbag['guest_pass'] = self.multi_expect_gp_cfg['expect_guestpass']
            #In the next step, don't need to check this value of expired_time.
            self.carrierbag['gp_expired_time'] = ''
            self.carrierbag['guest_fullname'] = self.multi_expect_gp_cfg['expect_fullname']
        else:
            pass        # stay on this step for the further page.
        
    
    def _generate_guest_pass_info(self):
        try:
            ga.generate_guestpass(self.zd, **self.generate_guestpass_cfg)
            self.guest_pass_info = ga.guestpass_info
            if not self.guest_pass_info and not self.dest_email:
                self.errmsg = "The generated Guest Pass is null."
                logging.debug(self.errmsg)
                raise Exception(self.errmsg)
            #Jluh@20140428, updated by the 9.8 changed
            elif self.email_invalid_format and self.guest_pass_info.get('invalid_csv_file_email_alert'):
                self.passmsg = 'The invalid_csv_file_email_alert dialog is corrected'
                logging.info(self.passmsg) 
            elif self.email_invalid_format and not self.guest_pass_info.get('invalid_csv_file_email_alert'):
                self.errmsg = 'No found the invalid_csv_file_email_alert dialog'
                logging.info(self.errmsg)
            else:
                pass     
        except Exception, ex:
            self.errmsg = '[Guest Pass generating failed] %s' % ex.message
            logging.debug(self.errmsg)
            
            
    def _clean_up_email_inbox(self, dir):
        logging.info('Clean up the inbox of the target email at first')
        self.linux.cmd('cd ' + dir)
        self.linux.cmd('rm -f *')
    
