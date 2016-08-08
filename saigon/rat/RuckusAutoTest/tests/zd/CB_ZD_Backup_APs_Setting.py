'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to backup the APs' setting.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd


class CB_ZD_Backup_APs_Setting(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._backupAPSetting()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.ap_mac_list = conf['ap_mac_list']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _backupAPSetting(self):
        logging.info('Backup the setting of APs: %s.' % self.ap_mac_list)
        try:
            self.aps_setting = dict()
            for mac_addr in self.ap_mac_list:
                ap_cfg = access_points_zd.get_ap_config_by_mac(self.zd, mac_addr)
                self.aps_setting.update({mac_addr: ap_cfg})
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['bak_aps_setting'] = self.aps_setting
        self.passmsg = 'Backup the setting of APs %s successfully' % self.ap_mac_list
            
                