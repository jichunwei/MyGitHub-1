'''
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Enable_Shared_Guest_Pass(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

        # A configuration passed through config() is HIGHER priority
        # than that in carrier bag
        self.gp_cfg = self.gp_cfg_bag
        self.gp_cfg.update(self.gp_cfg_init)


    def test(self):
        lib.zd.ga.generate_guestpass(self.zd, **self.gp_cfg)

        self.passmsg = 'Enable guest pass shared automatically successfully.'

        self._update_carrier_bag()

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _retrive_carrier_bag(self):
        self.gp_cfg_bag = {}
        if self.carrierbag.has_key('gp_cfg'):
            self.gp_cfg_bag = self.carrierbag['gp_cfg']


    def _update_carrier_bag(self):
        self.carrierbag['existed_gp_cfg'] = self.conf


    def _init_test_params(self, conf):
        self.conf = {'type':'multiple',
                     'guest_fullname':'',
                     'duration': '1',
                     'duration_unit': 'Days',
                     'wlan': 'wlan-guestpass',
                     'remarks': '',
                     'key': '',
                     'is_shared': 'Yes',
                     'number_profile': '5',
                     'repeat_cnt': 10,
                     'max_gp_allowable': 10000,
                     'profile_file': '',
                     'auth_ser': '',
                     'username': 'rat_guest_pass',
                     'password': 'rat_guest_pass',
                     }

        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.gp_cfg_init = self._get_default_gp_cfg()
        self.gp_cfg_init.update(self.conf)

        dlg_cfg = self._get_default_glg_cfg()
        self.gp_cfg_init.update(dlg_cfg)

        self.errmsg = ''
        self.passmsg = ''


    def _get_default_gp_cfg(self):
        gp_cfg = {'username': 'rat_guest_pass',
                  'password': 'rat_guest_pass',
                  'wlan': 'wlan_guestpass',
                  'duration': '1',
                  'duration_unit': 'Days',
                  'type': 'multiple',
                  }
        return gp_cfg


    def _get_default_glg_cfg(self):
        zd_url = self.zd.selenium_mgr.to_url(self.zd.ip_addr, self.zd.https)
        dlg_cfg = {'dlg_title': "The page at %s says:" % zd_url,
                   'dlg_text_maxgp': "The total number of guest and user accounts reaches maximum allowable size %d" %
                   (self.conf['max_gp_allowable']),
                   'dlg_text_dupgp': 'The key %s already exists. Please enter a different key.',
                   }
        return dlg_cfg

