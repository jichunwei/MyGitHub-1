'''
Description:
    Test the grace period setting in 'Hotspot Services' page
    or WLAN page under 'Configure->WLANs'.

Input:
    hotspot_cfg: Hotspot cfg, if it's not None, 
                 set the grace period in 'Hotspot Services' page",
    wlan_cfg: WLAN cfg, if it's not None and 'hotspot_cfg' is None, 
              set the grace period in WLAN page under 'Configure->WLANs',
    random: Set the grace period to a random number or not,
    random_range: Range of the random number, active when 'random' is True,
    grace_period: Grace period to be set, active when 'random' is False,
    
Create on 2011-12-12
@author: serena.tan@ruckuswireless.com
'''


import logging
import random
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd as WLAN
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as WGS
from RuckusAutoTest.components.lib.zd import hotspot_services_zd as HOTSPOT


ACTIVE_GP_RANGE = (1, 144000)


class CB_ZD_Test_Grace_Period_Setting(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'hotspot_cfg': "Hotspot cfg, if it's not None, set the" 
                                             "grace period in 'Hotspot Services' page",
                              'wlan_cfg': "WLAN cfg, if it's not None and 'hotspot_cfg'"
                                          "is None, set the grace period in"
                                          "WLAN page under 'Configure->WLANs'",
                              'random': "Set the grace period to a random number or not",
                              'random_range': "Range of the random number",
                              'grace_period': "Grace period to be set",
                              }

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            if self.conf['hotspot_cfg']:
                hotspot_cfg = self.conf['hotspot_cfg']
                current_profilelist = HOTSPOT.get_profile_name_list(self.zd)
                if hotspot_cfg['name'] in current_profilelist:
                    logging.info("Edit hotspot profile[%s] on ZD" % hotspot_cfg['name'])
                    HOTSPOT.cfg_profile(self.zd, hotspot_cfg['name'], **hotspot_cfg)
                
                else:
                    logging.info("Create hotspot profile[%s] on ZD" % hotspot_cfg['name'])
                    HOTSPOT.create_profile(self.zd, **hotspot_cfg)
            
            if self.conf['wlan_cfg']:
                wlan_cfg = self.conf['wlan_cfg']
                current_wlanlist = WLAN.get_wlan_list(self.zd)
                if wlan_cfg['ssid'] in current_wlanlist:
                    logging.info("Edit WLAN[%s] on ZD" % wlan_cfg['ssid'])
                    WLAN.edit_wlan(self.zd, wlan_cfg['ssid'], wlan_cfg)
        
                else:
                    logging.info("Create WLAN[%s] on ZD" % wlan_cfg['ssid'])
                    WLAN.create_wlan(self.zd, wlan_cfg)
                
                if self.conf['uncheck_wlan_in_default_wlan_group']:
                    WGS.uncheck_default_wlan_member(self.zd, wlan_cfg['ssid'])
                
                if self.conf['wg_cfg']:
                    WGS.cfg_wlan_group_members(self.zd, self.conf['wg_cfg']['name'], 
                                               [self.conf['wlan_cfg']['ssid']], True)
            
            if self.grace_period is None:
                self.passmsg = "Disable the grace period successfully."
                
            elif self.grace_period != '' \
            or self.grace_period >= ACTIVE_GP_RANGE[0] \
            or self.grace_period <= ACTIVE_GP_RANGE[1]:
                self.passmsg = "Set the grace period to '%s' successfully" % self.grace_period
            
            else:
                self.errmsg = "Can set the grace period to '%s', wrong behavior" % self.grace_period
            
        except Exception, e:
            msg = "Cannot set the grace period to '%s'. %s" % \
            (self.grace_period, e.message)
#            param_name = self.zd.messages['CF_GracePeriod']
            param_name = ''
            if self.grace_period == '':
                empty_msg = self.zd.messages['E_FailEmpty']
                empty_msg = empty_msg.replace('{1}', param_name)
                if empty_msg in e.message:
                    self.passmsg = msg
                
                else:
                    self.errmsg = msg
                
            elif self.grace_period < ACTIVE_GP_RANGE[0] \
            or self.grace_period > ACTIVE_GP_RANGE[1]:
                range_msg = self.zd.messages['E_FailRange']
                range_msg = range_msg.replace('{1}', param_name)
                range_msg = range_msg.replace('{2}', '%s' % ACTIVE_GP_RANGE[0])
                range_msg = range_msg.replace('{3}', '%s' % ACTIVE_GP_RANGE[1])
                if range_msg in e.message:
                    self.passmsg = msg
                    
                else:
                    self.errmsg = msg
            
            else:
                self.errmsg = msg
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.info("Wait for ZD to push new configuration to the APs")
        time.sleep(self.conf['pause'])
        
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'hotspot_cfg': {},
                     'wlan_cfg': {},
                     'wg_cfg': {},
                     'random': False,
                     'random_range': (1, 144000),
                     'grace_period': None,
                     'uncheck_wlan_in_default_wlan_group': True,
                     'pause': 2.0,
                     }
        self.conf.update(conf)
        
        if not self.conf['wlan_cfg'] and not self.conf['hotspot_cfg']:
            raise Exception('No WLAN and hotspot profile cfg')
        
        if self.conf['random']:
            range = self.conf['random_range']
            self.grace_period = random.randint(range[0], range[1])
        
        else:
            self.grace_period = self.conf['grace_period']
        
        if self.conf['hotspot_cfg']:
            self.conf['hotspot_cfg'].update({'idle_timeout': self.grace_period})
        
        elif self.grace_period is not None:
            self.conf['wlan_cfg'].update({'do_grace_period': True,
                                          'grace_period': self.grace_period})
        else:
            self.conf['wlan_cfg'].update({'do_grace_period': False})
            
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        pass
            
    def _update_carribag(self):
        self.carrierbag['zd_grace_period'] = self.grace_period
