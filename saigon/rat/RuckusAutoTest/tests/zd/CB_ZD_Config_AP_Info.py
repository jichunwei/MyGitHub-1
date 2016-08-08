
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd as ap
class CB_ZD_Config_AP_Info(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)


    def test(self):
        ap_info_on_zd = ap.get_all_ap_info(self.zd)
        self.mac_list = ap_info_on_zd.keys()
        self.device_name_list = []
        for mac in self.mac_list:
            description = 'AP-description-%s' % time.strftime("%H%M%S")
            device_name = 'AP-device-name-%s' % time.strftime("%H%M%S")
            
            self.device_name_list.append(device_name)
            
            logging.info('Configure the AP')
            ap_cfg = dict(mac=mac,description=description,device_name=device_name)
            ap.set_ap_cfg_info(self.zd, ap_cfg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        self.conf = {
                     }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''

    def _update_carrier_bag(self):
        self.carrierbag['mac_list'] = self.mac_list
        self.carrierbag['device_name_list'] = self.device_name_list