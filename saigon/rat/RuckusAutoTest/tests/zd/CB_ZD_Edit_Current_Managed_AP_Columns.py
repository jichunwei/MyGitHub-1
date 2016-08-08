'''
Created on 2011-2-17
@author: liu.anzuo@odc-ruckuswireless.com

Description: This script is used to edit currently managed ap column.

'''
import random
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import monitor_managed_aps_zd as map

column_list = ['Application Capability','Bonjour Gateway','Channel',
               'Clients','Description','Device Name','External IP:Port',
               'IP Address','Location','Mesh Mode','Model','Status','VLAN',]

class CB_ZD_Edit_Current_Managed_AP_Columns(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        if self.show_all_columns:
            self.enable_columns = self.disable_columns
            self.disable_columns = []
        else:
            self.enable_columns = random.sample(column_list, random.randint(1, len(column_list)))
            self.disable_columns = list(set(column_list).difference(set(self.enable_columns)))
        
        self.errmsg = map.edit_currently_managed_aps_column(self.zd, self.enable_columns, self.disable_columns)
        
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
        self.passmsg = ''
        self.disable_columns = self.carrierbag.get('disable_columns')
        self.show_all_columns = conf.get('show_all')
    
        
    def _updateCarrierbag(self):
        self.carrierbag['enalbe_columns'] = self.enable_columns + ['MAC Address', 'Action']
        self.carrierbag['disable_columns'] = self.disable_columns
        