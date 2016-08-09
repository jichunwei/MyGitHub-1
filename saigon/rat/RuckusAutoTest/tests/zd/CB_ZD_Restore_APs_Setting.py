'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to restore the APs to their original setting.

'''


import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd


class CB_ZD_Restore_APs_Setting(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._restoreAPSetting()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.bak_aps_setting = self.carrierbag['bak_aps_setting']
        self.ap_mac_list = self.bak_aps_setting.keys()
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _restoreAPSetting(self):
        logging.info('Restore APs %s to their original setting.' % self.ap_mac_list)
        try:
            for mac_addr in self.ap_mac_list:
                ap_cfg = self.bak_aps_setting[mac_addr]
                access_points_zd.set_ap_config_by_mac(self.zd, mac_addr, 
                                                      ap_cfg['general_info'], 
                                                      ap_cfg['radio_config'], 
                                                      ap_cfg['ip_config'], 
                                                      ap_cfg['mesh_config'])
            
            time.sleep(60)
            self.passmsg = 'Restore APs %s to their original setting successfully' % self.ap_mac_list
            
        except Exception, ex:
            self.errmsg = ex.message
            
                