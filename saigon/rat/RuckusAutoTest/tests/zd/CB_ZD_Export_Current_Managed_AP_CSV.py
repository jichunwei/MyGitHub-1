'''
Created on 2011-2-17
@author: liu.anzuo@odc-ruckuswireless.com

Description: This script is used to export currently managed ap CSV.

'''
import random
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import monitor_managed_aps_zd as mmap
from RuckusAutoTest.components import Helpers as lib
import logging

class CB_ZD_Export_Current_Managed_AP_CSV(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        logging.info("sleep 30s")
        time.sleep(30)
        if self.conf.get('filter') == True:
            ap_mac_list = lib.zd.aps.get_all_ap_mac_list(self.zd)
            self.search_term = random.choice(ap_mac_list)
            logging.info('search_term is %s' % self.search_term)
#            lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.search_term)
        
        self.file_path = self._exportCSV(self.search_term)
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
            
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = 'Export CSV successful'
        self.search_term = ''
    
    def _exportCSV(self, search_term):
        return mmap.export_csv(self.zd, search_term=search_term)
        
    def _updateCarrierbag(self):
        self.carrierbag['csv_file_path'] = self.file_path
        if self.conf.get('filter') == True:
            self.carrierbag['search_term'] = self.search_term
        