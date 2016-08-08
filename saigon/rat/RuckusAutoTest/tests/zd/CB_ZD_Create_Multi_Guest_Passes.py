'''
Description:
    config:

    test:

    cleanup:

Created on 2010-6-10
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_Multi_Guest_Passes(Test):
    '''
    repeat create guest pass.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        passmsg = []
        repeat_cnt = self.repeat_cnt
        while repeat_cnt:
            self._generate_multiple_guestpass(**self.gp_cfg)
            repeat_cnt = repeat_cnt - 1
        
        if not self.zd.is_logged_in():
            self.zd.login(force = True)
            
        nums = int(self.conf['number_profile'])
        total = nums * self.repeat_cnt

        pass_msg = 'Create %d guest passes automatically successfully. '
        pass_msg = pass_msg % (total)

        passmsg.append(pass_msg)

        self._update_carrier_bag()

        return ["PASS", passmsg]

    def cleanup(self):
        pass

    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existed_username'):
            self.conf['username'] = self.carrierbag['existed_username']
            self.gp_cfg['username'] = self.carrierbag['existed_username']

        if self.carrierbag.has_key('existed_password'):
            self.conf['password'] = self.carrierbag['existed_password']
            self.gp_cfg['password'] = self.carrierbag['existed_password']

        if self.carrierbag.has_key('wlan-guestpass'):
            self.wlan_cfg = self.carrierbag['wlan-guestpass']
            self.gp_cfg['wlan'] = self.wlan_cfg['ssid']

    def _update_carrier_bag(self):
        self.carrierbag['existed_gp_cfg'] = self.gp_cfg

    def _init_test_params(self, conf):
        self.conf = {'type':'multiple',
                     'guest_fullname':'',
                     'duration': '100',
                     'duration_unit': 'Days',
                     'wlan': 'wlan-guestpass',
                     'remarks': '',
                     'key': '',
                     'number_profile': '100',
                     'repeat_cnt': 10,
                     'max_gp_allowable': 10000,
#                     'profile_file': '',
                     'username': 'rat_guest_pass',
                     'password': 'rat_guest_pass',
                     'auth_ser': ''
                     }

        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.gp_cfg = self._get_default_gp_cfg()
        self.gp_cfg.update(self.conf)
        dlg_cfg = self._get_default_glg_cfg()
        self.gp_cfg.update(dlg_cfg)
        self.repeat_cnt = self.conf['repeat_cnt']        
        self.errmsg = ''
        self.passmsg = ''


    def _get_default_gp_cfg(self):
        gp_cfg = {'username': 'rat_guest_pass',
                  'password': 'rat_guest_pass',
                  'wlan': 'wlan_guestpass',
                  'duration': '100',
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

    def _generate_multiple_guestpass(self, **kwarg):

        gen_msg = "Try to generate %s guest passes automatically." % kwarg['number_profile']
        pass_msg = 'Create %s guest passes automatically successfully. '
        pass_msg = pass_msg % (kwarg['number_profile'])
#        err_msg = 'Create %s guest passes failed' % self.conf['number_profile']

        logging.info(gen_msg)

        lib.zd.ga.generate_guestpass(self.zd, **kwarg)
#        self.passmsg = self.passmsg + pass_msg
        logging.info(pass_msg)

