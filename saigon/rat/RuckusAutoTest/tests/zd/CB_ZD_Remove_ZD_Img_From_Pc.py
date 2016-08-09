'''
by west.li 2012.2.2
after upgrade/downgrade test,remove the zd img from local pc
'''

import logging
import os
from RuckusAutoTest.models import Test


class CB_ZD_Remove_ZD_Img_From_Pc(Test):
    def config(self, conf):
        self._initTestParameters(conf)
        self._retrive_carrier_bag()

    def test(self):
        if not self.remove_img_after_test:
            return self.returnResult('PASS','need not remove the files')
            
        try:
            os.remove(self.base_img)
        except:
            pass
        
        try:
            os.remove(self.target_img)
        except:
            pass
        
        self.passmsg='ZD img removed successfully'
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.passmsg=''
        self.errmsg=''

    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('base_build_file'):
            self.base_img   = self.carrierbag['base_build_file']
        if self.carrierbag.has_key('target_build_file'):
            self.target_img = self.carrierbag['target_build_file']
        self.remove_img_after_test = self.carrierbag['remove_img_after_test']
    
