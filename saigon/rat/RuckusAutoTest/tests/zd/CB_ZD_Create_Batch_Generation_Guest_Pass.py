'''
Created on 2010-6-9

@author: lab
'''
import time
import logging 
import os
import csv
import string
from random import choice

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class CB_ZD_Create_Batch_Generation_Guest_Pass(Test):
    '''
    '''  
    def config(self, conf):
        required_components = ['RuckusAP', 'ZoneDirector']
        parameter_description = {
                               'wlan_cfg': 'optional, the configuration of guest WLAN',   
                               'auth_server_type': 'local',
                               'auth_server_info': {},                                                           
                               'username': 'testing user use to generate guest pass',
                               'password': 'testing user password',
                               'number_profile': 'the number guest passes profile will be create in csv file to test',
                              }
        self._init_test_params(conf)
            
    
    def test(self):
        passmsg = []
        self._cfg_create_wlan_on_zd()
        server_type = self.conf['auth_server_type']
        if server_type == "local":
            self._create_local_user()
        elif server_type == "radius":
            self._create_radius_user()
        else:
            self._create_no_server_user()
        
        self._generate_csv_file()
        
        self._import_csv()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        passmsg.append(self.passmsg)        
        
        self._verify_guest_pass_info_on_webui()
        
        if self.errmsg:
            return ('FAIL', self.errmsg)
        passmsg.append(self.passmsg)        
        
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.conf = {
                     'wlan_cfg': {},
                     'auth_server_type': 'local',
                     'auth_server_info': {},
                     'username': 'guesttest',
                     'password': 'guesttest',
                     'number_profile': 10}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
                               
    
    def _retrive_carrier_bag(self):
        pass
    
    
    def _update_carrier_bag(self):
        pass
    
    def _cfg_create_wlan_on_zd(self):
        wlan_cfg = {'ssid':'Test_WLAN-%s' % time.strftime("%H%M%S"),
                    'type':'guest'}
        self.conf['wlan_cfg'].update(wlan_cfg)

        logging.info("Create WLAN [%s] as a Guest Access WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs") 
    
    def _create_local_user(self):
        logging.info('Create user "%s" on Zone Director' % self.conf['username'])
        self.zd.create_user(self.conf['username'], self.conf['password'])
        logging.info('Use "Local Database" to generate and authenticate the guest passes')
        self.zd.set_guestpass_policy('Local Database')
    
    def _create_radius_user(self):
        logging.info('Create an Radius server on Zone Director')
        lib.zd.aaa.create_server(self.zd, **self.conf['auth_server_info'])
        logging.info('Use "Radius Server" to generate and authenticate the guest passes')
        self.zd.set_guestpass_policy(self.conf['auth_server_info']['server_name'])
    
    def _create_no_server_user(self):
        raise Exception('Do not support to test with  "%s" authentication server' % self.conf['auth_server_type'].upper())
    
    def _generate_csv_file(self):
        # Delete the file if it's existing
        try:
            os.remove('batch_file.csv')
        except: pass

        self.batch_file = open('batch_file.csv', 'wb')
        writer = csv.writer(self.batch_file)
        guest_user_info_list = []
        self.expected_webui_info = {}
        self.expected_record_info = {}

        logging.info("Generate a CSV file:")        
        logging.info('with predefined username and guestpass')
        for id in range(1, self.conf['number_profile'] + 1):
            guestname = 'AutoGuest-%s' % id
            guestpass = ''.join([choice(string.letters).upper() for i in range(10)])
            guest_user_info_list.append([guestname, '', guestpass])
            self.expected_webui_info[guestname] = [self.conf['username'], self.conf['wlan_cfg']['ssid']]
            self.expected_record_info[guestname] = guestpass

        writer.writerows(guest_user_info_list)
        self.batch_file.close()
    
    def _import_csv(self):
        logging.info("Import the CSV file [%s] to generate guest passed" % self.batch_file.name)
        guestpass_setting = {'type': 'multiple',
                             'wlan': self.conf['wlan_cfg']['ssid'],
                             'profile_file': '\\'.join((os.getcwd(), self.batch_file.name)),
                             'username': self.conf['username'],
                             'password': self.conf['password']}
        try:
            lib.zd.ga.generate_guestpass(self.zd, **guestpass_setting)
            passmsg = 'Guest pass generation by importing the CSV file [%s], %s server successfully'
            self.passmsg = passmsg % (self.batch_file.name, self.conf['auth_server_type'].upper())
            
        except Exception, e:
            self.errmsg = '[Guest pass generation by importing the file failed] %s' % e.message
            
    def _verify_guest_pass_info_on_webui(self):
        logging.info("Verify guest passes information on Zone Director's WebUI")
        all_guestpass_info = lib.zd.ga.get_all_guestpasses(self.zd)
        all_guestpass_info_on_zd = {}

        for guest_full_name in all_guestpass_info.iterkeys():
            all_guestpass_info_on_zd[guest_full_name] = [all_guestpass_info[guest_full_name]['created_by'],
                                                         all_guestpass_info[guest_full_name]['wlan']
                                                         ]

        logging.debug('All guest pass information on Zone Director WebUI are: %s' % all_guestpass_info_on_zd)
        logging.debug('The guest passes information in file "%s" are: %s' % (self.batch_file.name,
                                                                             self.expected_webui_info))
        if all_guestpass_info_on_zd == self.expected_webui_info:
            self.passmsg = 'The guest pass information on WebUI are correctly '
            logging.info(self.passmsg)
            return

        errguest = []
        for guestpass in self.expected_webui_info.keys():
            if self.expected_webui_info[guestpass] != all_guestpass_info_on_zd[guestpass]:
                errguest.append(guestpass)
        if errguest:
            self.errmsg = 'The guest user %s are in the CSV file but be not created' % errguest
            logging.info(self.errmsg)
    
              
        