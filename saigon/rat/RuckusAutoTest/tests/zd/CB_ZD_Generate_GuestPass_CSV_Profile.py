'''
'''
import logging
import os
import csv
import string
from random import choice

from RuckusAutoTest.models import Test

class CB_ZD_Generate_GuestPass_CSV_Profile(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()


    def test(self):
        try:
            self._generate_csv_file()
        
        except Exception, e:
            self.errmsg = 'Generate guest pass CSV file failed: %s' % e.message
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = 'GuestPass CSV Profile was generated successfully.'

        self._update_carrier_bag()

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _retrive_carrier_bag(self):
        pass


    def _update_carrier_bag(self):
        if self.carrierbag.has_key('gp_cfg'):
            self.carrierbag['gp_cfg'].update({'profile_file': self.batch_file,
                                              'expected_webui_info': self.expected_webui_info,
                                              'expected_record_info': self.expected_record_info
                                              })

        else:
            self.carrierbag['gp_cfg'] = {'profile_file': self.batch_file,
                                         'expected_webui_info': self.expected_webui_info,
                                         'expected_record_info': self.expected_record_info
                                         }


    def _init_test_params(self, conf):
        self.conf = {'number_profile': 5,
                     'username': 'Guest',
                     'wlan_cfg': {'ssid': 'rat-guest-wlan'},
                     'predefine_guestpass': True
                     }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''


    def _generate_csv_file(self):
        # Delete the file if it exists
        try:
            os.remove('batch_file.csv')

        except:
            pass

        self.batch_file = open('batch_file.csv', 'wb')
        writer = csv.writer(self.batch_file)
        guest_user_info_list = []
        self.expected_webui_info = {}
        self.expected_record_info = {}

        logging.info("Generate a CSV file:")
        if self.conf['predefine_guestpass']:
            logging.info('with predefined username and guestpass')
            
        else:
            logging.info('with predefined username')
            
        for id in range(1, self.conf['number_profile'] + 1):
            guestname = 'AutoGuest-%s' % id
            guestpass = ''
            if self.conf['predefine_guestpass']:
                guestpass = ''.join([choice(string.letters).upper() for i in range(10)])
                
            guest_user_info_list.append([guestname, '', guestpass])
            self.expected_webui_info[guestname] = [self.conf['username'], self.conf['wlan_cfg']['ssid']]
            self.expected_record_info[guestname] = guestpass

        writer.writerows(guest_user_info_list)
        self.batch_file.close()

