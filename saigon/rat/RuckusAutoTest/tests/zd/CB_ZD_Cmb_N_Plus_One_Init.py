'''
put restore file in carriebag
'''

from RuckusAutoTest.models import Test
import logging

class CB_ZD_Cmb_N_Plus_One_Init(Test):
    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        self._update_carrier_bag()
        return "PASS", self.passmsg

    def cleanup(self):
        pass

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        self.carrierbag['restore_file_path']    = self.restore_file_path
        self.carrierbag['sw'] = self.testbed.components['L3Switch']

    def _init_test_params(self, conf):
        self.conf={'restore_file_path':'C:\\Documents and Settings\\lab\\My Documents\\Downloads\\Nplusone_upgrade.bak'}
        self.conf.update(conf)
        self.restore_file_path = self.conf['restore_file_path']
        self.errmsg = ''
        self.passmsg = 'restore_file_path is %s'%self.restore_file_path
        logging.info(self.passmsg)
        
