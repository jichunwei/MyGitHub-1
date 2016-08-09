'''
Created on 2011-6-14

@author: serena.tan@ruckuswireless.com

Decription: 

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.common import chariot


class CB_Chariot_Clone_Test_File(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._cloneTestFile()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.template_filename = conf['template_filename']
        self.clone_filename = conf['clone_filename']
        self.output_filename = conf['output_filename']
        self.errmsg = ''
        self.passmsg = ''

    def _cloneTestFile(self):
        try:
            chariot.clone_test(self.template_filename, self.clone_filename, self.output_filename)
            self.passmsg = "Clone chariot test file: %s to %s successfully" % (self.template_filename, self.output_filename)
            
        except Exception, e:
            self.errmsg = e.message
            