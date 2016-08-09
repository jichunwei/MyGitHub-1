'''
Description:Import license from ZD GUI.
Created on 2010-9-21
@author: cwang@ruckuswireless.com
'''
import os

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Import_License(Test):
    '''
    Import license from ZD GUI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        if not os.path.exists(self.file_path):
            return self.returnResult('FAIL', 'File [%s] does not exist' % self.file_path)
        
        try:
            lib.zd.lic.import_license(self.zd, self.file_path)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        self._update_carrier_bag()
        
        return ('PASS', 'License file (%s) import successfully' % self.file_path)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(file_path = '')
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.file_path = self.conf['file_path']        
        self.errmsg = ''
        self.passmsg = ''
    
