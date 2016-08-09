'''
Description:

Input:
    
Create on 2011-12-12
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd as WLAN
from RuckusAutoTest.components.lib.zd import hotspot_services_zd as HOTSPOT


class CB_ZD_Verify_Grace_Period_In_GUI(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'hotspot_name': "Hotspot name",
                              'wlan_name': "WLAN name",
                              'grace_period': "grace period"
                              }

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            if not self.grace_period:
                self.grace_period = 'Disabled'
                
            if self.conf['hotspot_name']:
                hotspot_name = self.conf['hotspot_name']
                hotspot_info = HOTSPOT.get_profile_by_name(self.zd, hotspot_name)
                logging.info('Hotspot info: %s' % hotspot_info)
                if str(self.grace_period) != hotspot_info['idle_time']:
                    self.errmsg = "Grace period[%s] in hotspot[%s] is not the same as expected: %s." \
                    % (hotspot_info['idle_time'], hotspot_name, self.grace_period)
                
                else:
                    self.passmsg = "Grace period[%s] in hotspot[%s] is correct." \
                    % (hotspot_info['idle_time'], hotspot_name)
                
            elif self.conf['wlan_name']:
                wlan_name = self.conf['wlan_name']
                wlan_info = WLAN.get_wlan_conf_detail(self.zd, wlan_name)
                if not wlan_info:
                    raise Exception("Not found WLAN[%s] in ZD GUI." % wlan_name)
                
                logging.info("WLAN info: %s" % wlan_info)
                if not wlan_info.has_key('grace_period'):
                    raise Exception("No grace period info in WLAN[%s]" % wlan_name)
                
                if str(self.grace_period) != wlan_info['grace_period']:
                    self.errmsg = "Grace period[%s] in WLAN[%s] is not the same as expected: %s." \
                    % (wlan_info['grace_period'], wlan_name, self.grace_period)    
                       
                else:
                    self.passmsg = "Grace period[%s] in WLAN[%s] is correct." \
                    % (wlan_info['grace_period'], wlan_name)
                
        except Exception, e:
            self.errmsg = e.message
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'hotspot_name': '',
                     'wlan_name': '',
                     'grace_period': None #'Disabled'/other value
                     }
        self.conf.update(conf)
        
        if not self.conf['wlan_name'] and not self.conf['hotspot_name']:
            raise Exception('No WLAN name and hotspot profile name')
        
        self.grace_period = self.conf['grace_period']
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        if self.grace_period == None and self.carrierbag.has_key('zd_grace_period'):
            self.grace_period = self.carrierbag['zd_grace_period']
            
    def _update_carribag(self):
        pass
    