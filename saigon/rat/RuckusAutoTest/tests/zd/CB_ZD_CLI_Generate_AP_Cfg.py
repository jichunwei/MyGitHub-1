'''
Created on 2011-2-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to create the AP configuration for ZD CLI.

'''


import random
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zd import access_points_zd


class CB_ZD_CLI_Generate_AP_Cfg(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getAPSupportRadioCfgOptions()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._getAPCurrentRadioCfg()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._generateAPCfg()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', 'Generate the AP configuration for ZD CLI successfully')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ap_mac_addr': '',
                     'active_radio': '',
                     'wg_name': ''
                     }
        self.conf.update(conf)
        
        self.ap_mac_addr = self.conf['ap_mac_addr']
        self.active_radio = self.conf['active_radio']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getAPCurrentRadioCfg(self):
        active_radio_list = [self.active_radio] if self.active_radio else []
        try:
            self.current_radio_cfgs = access_points_zd.get_ap_radio_config_by_mac(self.zd,
                                                                             self.ap_mac_addr,
                                                                             active_radio_list)
            
        
        except Exception, ex:
            self.errmsg = ex.message
    
    def _getAPSupportRadioCfgOptions(self):
        try:
            self.radio_cfg_options = access_points_zd.get_radio_cfg_options(self.zd, self.ap_mac_addr)
        
        except Exception, ex:
            self.errmsg = ex.message
    
    def _generateAPCfg(self):
        try:
            logging.info('Generate the AP configuration for ZD CLI.')
            self.ap_cfg = {'mac_addr': self.ap_mac_addr,
                           'device_name': utils.make_random_string(random.randint(1,64),type = 'alnum'), 
                           'description': utils.make_random_string(random.randint(1,64),type = 'alnum'), 
                           'location': utils.make_random_string(random.randint(1,64),type = 'alnum'), 
                           'gps_coordinates': {'latitude': '37.3881398',
                                               'longitude': '-122.0258633',
                                               },
                           }

            current_radio_cfg = self.current_radio_cfgs[self.active_radio]
            radio = 'radio_%s' % self.active_radio
            radio_cfg_options = self.radio_cfg_options[radio]
            self.ap_cfg[radio] = {}
            #channelization is not for bg radio mode
            if self.active_radio not in ['bg']:
                radio_cfg_options['channelization'].remove(current_radio_cfg['channelization'])
                self.ap_cfg[radio]['channelization'] = random.choice(radio_cfg_options['channelization'])
            
            radio_cfg_options['channel'].remove(current_radio_cfg['channel'])
            self.ap_cfg[radio]['channel'] = random.choice(radio_cfg_options['channel'])
            radio_cfg_options['power'].remove(current_radio_cfg['power'])
            self.ap_cfg[radio]['power'] = random.choice(radio_cfg_options['power'])
            if self.conf['wg_name']:
                self.ap_cfg[radio]['wlangroups'] = self.conf['wg_name']
            
            else:
                self.ap_cfg[radio]['wlangroups'] = 'Default'
                
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_ap_cfg'] = self.ap_cfg
        