'''
Created on 2011-6-14

@author: serena.tan@ruckuswireless.com

Decription: 

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.common import chariot


class CB_Chariot_Run_Test(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._runTest()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.tst_filename = conf['tst_filename']
        self.res_filename = conf['res_filename']
        self.timeout = 1800
        self.return_test_detail = False
        if conf.has_key('timeout'):
            self.timeout = conf['timeout']
            
        if conf.has_key('return_test_detail'):
            self.return_test_detail = conf['return_test_detail']
               
        self.errmsg = ''
        self.passmsg = ''

    def _runTest(self):
        try:
            chariot.run_test(self.tst_filename, 
                             self.res_filename, 
                             self.timeout, 
                             self.return_test_detail)
            self.passmsg = "Run chariot test: %s and put the result to: %s successfully" % \
                           (self.tst_filename, self.res_filename) 
            
        except Exception, e:
            self.errmsg = e.message
            