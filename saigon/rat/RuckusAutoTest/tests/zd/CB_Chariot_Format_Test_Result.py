'''
Created on 2011-6-14

@author: serena.tan@ruckuswireless.com

Decription: 

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.common import chariot


class CB_Chariot_Format_Test_Result(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._formatTestResult()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.res_filename = conf['res_filename']
        self.output_filename = conf['output_filename']
        self.args = ""
        if conf.has_key('args'):
            self.args = conf['args']

        self.errmsg = ''
        self.passmsg = ''

    def _formatTestResult(self):
        try:
            chariot.format_test_result(self.res_filename, self.output_filename, self.args)
            self.passmsg = "Format chariot test result file: %s to: %s successfully" % \
                           (self.res_filename, self.output_filename) 
            
        except Exception, e:
            self.errmsg = e.message
            
