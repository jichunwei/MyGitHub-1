"""
Description: This script is support to confgiure wlan group with wlan on zd
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Create_Wlan_Group(Test):
    
    def config(self, conf):
        self.__cfg_init_test_params(conf)
        
    def test(self):
        self._create_wlan_group_without_wlan()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag['wgs_cfg'] = self.wgs_cfg
        msg = 'Create wlan group [%s] on ZD successfully' % self.wgs_cfg['name']
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def __cfg_init_test_params(self, conf):
        self.errmsg = ''
        default_wgs_cfg = dict(ap_rp={'bg':{'wlangroups':'WLAN_GROUP_1'}},
                               name='WLAN_GROUP_1',
                               description='WLAN_GROUP_1')
        self.conf = conf.copy()
        self.wgs_cfg = self.conf['wgs_cfg'] if self.conf['wgs_cfg'] else default_wgs_cfg
        self.zd = self.testbed.components['ZoneDirector']
         
    def _create_wlan_group_without_wlan(self):
        self.errmsg = zhlp.wgs.create_wlan_group( self.zd, 
                                                  self.wgs_cfg['name'],
                                                  [],
                                                  False,
                                                  self.wgs_cfg['description'])
        
