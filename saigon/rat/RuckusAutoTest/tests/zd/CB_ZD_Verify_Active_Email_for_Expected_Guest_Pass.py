'''
Created on Jan 24, 2014

@author: jacky luh
'''

import logging

from RuckusAutoTest.models import Test

                                                      
class CB_ZD_Verify_Active_Email_for_Expected_Guest_Pass(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)
        

    def test(self):
        if self.conf['email_format'] == 'valid':
            self._verifyActiveEmailOnSmtpServer()
            
            if self.errmsg: 
                return self.returnResult('FAIL', self.errmsg)
        elif self.conf['email_format'] == 'invalid':
            self._verifyInvalidEmailOnSmtpServer()
            if self.errmsg: 
                return self.returnResult('FAIL', self.errmsg)
        else:
            pass
        
        return self.returnResult('PASS', self.passmsg)
    

    def cleanup(self):
        #self._update_carrier_bag()
        pass

    def _initTestParameters(self, conf):
        '''
        expected_guest_pass_email_info:
        {}
        '''
        self.conf = {'email_guest_pass': '',
                     'email_format': ''}
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''
        self.email = conf['email']
        self.guest_pass = self.carrierbag['guest_pass']
        self.expired_time = self.carrierbag['gp_expired_time']
        self.fullname = self.carrierbag['guest_fullname']
        
        self.linux = self.testbed.components['LinuxServer']
    

    def _verifyActiveEmailOnSmtpServer(self):
        logging.info('Get the active email on the smtp server')
        self._getActiveEmailContents()
        
        if self.email_contents[0].split('|')[1] == self.carrierbag['guest_pass']:
            self.passmsg = 'the guest pass email is corrected.'
        else:
            self.errmsg = "the email's guest pass is not the same with the web page's."
            
    
    def _getActiveEmailContents(self):
        email_folder = '/home/%s/Maildir/new' % self.email.split('@')[0]
        self.email_contents = self.linux.get_mails_list(email_folder)
        if not self.email_contents:
            raise Exception("No found the guest pass email")
            
    
    def _update_carrier_bag(self):
        self.carrierbag['email_guest_pass'] = self.conf['guest_pass']
            
#        except Exception, e:
#            self.errmsg = e.message

