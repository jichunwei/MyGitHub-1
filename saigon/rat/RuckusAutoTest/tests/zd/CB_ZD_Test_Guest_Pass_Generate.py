'''
Created on 2011-3-22
@author: serena.tan@ruckuswireless.com

Description: This script is used to test the guest pass generate in zd.

'''


import logging

from RuckusAutoTest.models import Test


class CB_ZD_Test_Guest_Pass_Generate(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testGuestPassGenerate()
        
        if self.errmsg: 
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'username': '', 
                     'password': '', 
                     'guess_db': 'Local Database',
                     'allow': True}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _testGuestPassGenerate(self):
        logging.info('Test guest pass generate with username[%s] and password[%s]:' % (self.conf['username'], self.conf['password']))
        try:
            res = self.zd.test_user(self.conf['username'], self.conf['password'], self.conf['guess_db'])
            if res == self.conf['allow']:
                if res:
                    self.passmsg = 'Can generate guest pass with username[%s] and password[%s], correct behavior' % (self.conf['username'], self.conf['password'])
                
                else:
                    self.passmsg = 'Can not generate guest pass with username[%s] and password[%s], correct behavior' % (self.conf['username'], self.conf['password'])
            
            else:
                if res:
                    self.errmsg = 'Can generate guest pass with username[%s] and password[%s], wrong behavior' % (self.conf['username'], self.conf['password'])
                
                else:
                    self.errmsg = 'Can not generate guest pass with username[%s] and password[%s], wrong behavior' % (self.conf['username'], self.conf['password'])
            
        except Exception, ex:
            self.errmsg = ex.message
     
                