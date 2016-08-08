'''
Created on 2011-6-14

@author: serena.tan@ruckuswireless.com

Decription: 

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.common import chariot


class CB_Chariot_Get_Throughput_Info(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getThroughputInfo()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.filename = conf['filename']

        self.errmsg = ''
        self.passmsg = ''

    def _getThroughputInfo(self):
        try:
            self.th_info = chariot.get_throughput_info(self.filename)
            self.passmsg = "Get throughput information from file: %s successfully" % self.filename
            
        except Exception, e:
            self.errmsg = e.message
            
    def _updateCarrierbag(self):
        self.carrierbag['throughput_info'] = self.th_info
