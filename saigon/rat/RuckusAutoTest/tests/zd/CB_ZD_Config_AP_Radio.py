import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Config_AP_Radio(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)


    def test(self):
        passmsg = ''
        if 'init' == self.conf['cfg_type']:
            self._config_ap_disable_wlan_service(
                self.conf['all_ap_mac_list']
            )

        if 'config' == self.conf['cfg_type']:
            if self.conf.get('radio_band_type'):
                if self.conf['radio_band_type'] == 'override':
                    self._config_ap_radio_band(self.ap_mac_addr, self.conf['radio_band_value'])

            self._config_ap_wlan_service(
                self.ap_mac_addr,
                self.conf['ap_cfg'].get('radio',None),
                self.conf['ap_cfg'].get('channel'),
                self.conf['ap_cfg']['wlan_service']
            )
            time.sleep(30)

            self.carrierbag[self.ap_tag]['ap_ins'] = self.active_ap
            passmsg = 'Config active AP [%s %s] successfully' % \
                      (self.ap_tag, self.ap_mac_addr)

        if 'teardown' == self.conf['cfg_type']:
            self._config_ap_enable_wlan_service(
                self.conf['all_ap_mac_list']
            )

        return self.returnResult('PASS', passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        self.conf = {'ap_tag': '',
                     'ap_cfg':
                         {'radio': '', 'channel': '',
                          'wlan_service': ''
                          },
                     'cfg_type': 'config', #['init', 'config', 'teardown']
                     }
        self.conf.update(conf)

        if conf.get('zd_tag'):
            self.zd = self.carrierbag[conf.get('zd_tag')]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        self.conf['all_ap_mac_list'] = lib.zd.aps.get_all_ap_mac_list(self.zd)

        if 'config' == self.conf['cfg_type']:
            self.ap_tag = self.conf['ap_tag']
            self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
            self.ap_mac_addr = self.active_ap.base_mac_addr
        
        if self.conf['cfg_type'] in ['init', 'teardown']:
            if not self.conf['all_ap_mac_list']:
                self.conf['all_ap_mac_list'] = [ap['mac'] for ap in self.zd.get_all_ap_info()]

        self.errmsg = ''
        self.passmsg = ''


    def _config_ap_wlan_service(self, ap_mac_addr, radio = None, channel = None,
                                wlan_service = False):
        '''
        '''
        cfg_set = {'radio': '', 'channel': '', 'wlan_service': wlan_service}
        
        if channel:
            cfg_set.update({'channel':channel})

        supported_radio = lib.zd.ap.get_supported_radio(self.zd, ap_mac_addr)

        for r in supported_radio:
            if not radio:
                cfg_set.update({'radio': r, 'wlan_service': wlan_service})

            elif r == radio:
                cfg_set.update({'radio': radio, 'wlan_service': wlan_service})
                
            else:
                continue

            lib.zd.ap.cfg_ap(self.zd, ap_mac_addr, cfg_set)


    def _config_ap_disable_wlan_service(self, ap_mac_list):
        '''
        '''
        for ap_mac in ap_mac_list:
            self._config_ap_wlan_service(ap_mac, wlan_service = False)


    def _config_ap_enable_wlan_service(self, ap_mac_list):
        '''
        '''
        for ap_mac in ap_mac_list:
            self._config_ap_wlan_service(ap_mac, wlan_service = True)

    def _config_ap_radio_band(self, ap_mac_addr, new_radio_band):
        '''
        '''
        cfg_set = {'band_switch': new_radio_band}
        lib.zd.ap.cfg_ap(self.zd, ap_mac_addr, cfg_set)
