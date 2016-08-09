'''
Description:Download Guest Passes Record, and save file to default folder.
Created on 2010-9-19
@author: cwang@ruckuswireless.com    
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Download_GuestPasses_Record(Test):
    '''
    Download Guest Passes Record, and save file to default folder.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        try:
            self.file_path = lib.zd.ga.download_generated_guestpass_record(self.zd, self.conf['username'], self.conf['password'])
            if not self.file_path:
                return self.returnResult("FAIL", "Download file failed")
            
        except Exception, e:
            return self.returnResult("FAIL", "Download exception [%s]" % e.message)
        
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "Download file [%s] successfully" % self.file_path)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_guest_pass_record_file'] = self.file_path
    
    def _init_test_params(self, conf):
        self.conf = dict(username = 'admin',
                         password = 'admin')
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
