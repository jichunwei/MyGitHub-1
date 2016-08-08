'''
Description: Guest Passes Record file Parser
Created on 2010-9-19
@author: cwang@ruckuswireless.com
'''
import csv
import os

from RuckusAutoTest.models import Test

class CB_ZD_Parse_Guest_Passes_Record_File(Test):
    '''
    Guest Passes Record file Parser.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        if os.path.exists(self.file_path):
            data = csv.reader(open(self.file_path, "r"))
            self.records = [ x for x in data ]
            if self.records:
                self.records[1:]
            else:
                return self.returnResult("FAIL", "Current Guest Passes is empty")
        else:
            return self.returnResult("FAIL", "Doesn't exist file [%s]" % self.file_path)
                
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "Parse guest passes record from file [%s] successfully" % self.file_path)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.file_path = self.carrierbag['existed_guest_pass_record_file']
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_guest_passes_record'] = self.records
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
    
