# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL/ERROR
   Results:

   Messages:
       If FAIL the test script return a message related to the criteria
       that is not satisfied

   Test procedure:
   1. Config:

   2. Test:

   3. Cleanup:


   How it is tested?

"""

import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class ZD_MultiWlans_GuestAccess_Integration(Test):
    required_components = []
    test_parameters = {}

    def config(self, conf):
        self._initTestParameter(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()


    def test(self):
        # Generate Guest Pass for testing
        self._generate_guestpass()

        # Verify station could access and be authenticated successfully
        # on all wlans
        self._verifyGuestPassWorkOnAllWlans()

        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #self.zd.remove_all_guestpasses()
        #lib.zd.wlan.delete_all_wlans(self.zd)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()

    def _initTestParameter(self, conf):
        self.conf = {'target_station':'',
                     'wlan_config_set':'set_of_32_open_none_wlans',
                     'use_tou': True,
                     'redirect_url': '',
                     'dest_ip':'172.126.0.252',
                     'tested_wlan_list': [],
                     'target_url': "http://172.16.10.252/",
                     'no_auth': False,
                     'expected_data': "It works!",
                     'browser_name': "firefox",
                     'start_browser_tries': 3,
                     'start_browser_timeout': 15,
                 }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.target_station = None
        self.active_ap = None

        self.wlan_conf_list = tconfig.get_wlan_profile(self.conf['wlan_config_set'])
        test_conf = {'type': 'guest'}
        for wlan in self.wlan_conf_list:
            wlan.update(test_conf)

        self.wlan_name_list = [wlan['ssid'] for wlan in self.wlan_conf_list]

        self.check_status_timeout = 180
        self.break_time = 2
        self.test_wlan_number = 6
        self.errmsg = ''
        self.passmsg = ''

        self.use_tou = self.conf['use_tou']
        self.redirect_url = self.conf['redirect_url']

        self.auth_server = 'Local Database'
        self.username = 'testuser'
        self.password = 'testpassword'
        self.guest_name = 'Integration Guest'
        self.dest_ip = self.conf['dest_ip']


    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(
                                  self.conf['target_station'],
                                  self.testbed.components['Station'],
                                  check_status_timeout = self.check_status_timeout,
                                  remove_all_wlan = True)

        if not self.target_station:
            raise Exception("Target station %s not found" % \
                            self.conf['target_station'])


    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #self.zd.remove_all_guestpasses()
        #lib.zd.wlan.delete_all_wlans(self.zd)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        self.zd.unblock_clients('')

        # Create wlans set for testing
#        lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_conf_list)
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 Guest Access improvement
        self.guest_access_conf = {}
        lib.zdcli.guest_access.config_guest_access(self.zdcli, **self.guest_access_conf)
        lib.zdcli.set_wlan.create_multi_wlans(self.zdcli, self.wlan_conf_list)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')

        # Configure the Guest Access policy on Zone Director
        self._cfgGuestPassPolicyOnZD()

        # Create user for authentication
        self.zd.create_user(self.username, self.password)


    def _cfgGuestPassPolicyOnZD(self):
        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.set_guestaccess_policy(use_guestpass_auth = True,
                                       use_tou = self.use_tou,
                                       redirect_url = self.redirect_url,
                                       )

        logging.info("Configure Guest Password policy on the Zone Director")
        self.zd.set_guestpass_policy(auth_serv = self.auth_server)


    def _generate_guestpass(self):
        '''
        '''
        gp_cfg = {'username': self.username,
                  'password': self.password,
                  'guest_fullname': '',
                  'wlan': '',
                  'duration': '5',
                  'duration_unit': 'Days',
                  }

        self.guestpasses = {}

        for wlan_name in self.wlan_name_list:
            gp_cfg.update({'wlan': wlan_name,
                           'guest_fullname': wlan_name,
                           })

            logging.info("Generate a Guest Pass for wlan %s" % wlan_name)

            try:
                lib.zd.ga.generate_guestpass(self.zd, **gp_cfg)

            except Exception, e:
                msg = "Unable to to generate Guest Pass. %s" % e.message
                raise Exception(msg)

            guest_pass = lib.zd.ga.guestpass_info['single_gp']['guest_pass']
            expired_time = lib.zd.ga.guestpass_info['single_gp']['expired_time']

            self.guestpasses.update(
                {wlan_name: {'guest_pass': guest_pass,
                             'expired_time': expired_time,
                             'user': gp_cfg['guest_fullname'],
                             }
                }
            )


    def _verifyStationAssociation(self, wlan_conf_list):
        error_at_wlan = []
                    
                    
        self._start_browser_before_auth()
        if self.errmsg:
            logging.info(self.errmsg)
            error_at_wlan.append('start_brower_fail')
            return error_at_wlan
            
        for wlan in wlan_conf_list:
            self.target_station.remove_all_wlan()
            time.sleep(1)
            tmethod.assoc_station_with_ssid(self.target_station, wlan,
                                            self.check_status_timeout,
                                            self.break_time)

            val, val1, val2 = tmethod.renew_wifi_ip_address(
                                  self.target_station,
                                  self.check_status_timeout,
                                  self.break_time)

            if not val:
                raise Exception(val2)

            sta_wifi_ip_addr = val1
            sta_wifi_mac_addr = val2

            errmsg, client_info = tmethod.verify_zd_client_is_unauthorized(
                                      self.zd, sta_wifi_ip_addr,
                                      sta_wifi_mac_addr,
                                      self.check_status_timeout)

            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue

            errmsg = tmethod.client_ping_dest_not_allowed(
                         self.target_station,
                         self.dest_ip)

            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue

            logging.info("Perform Guest Pass authentication on the target station %s using guest pass '%s'" % \
                     (self.conf['target_station'], self.guestpasses[wlan['ssid']]['guest_pass']))

            arg = tconfig.get_guest_auth_params(
                      self.zd, self.guestpasses[wlan['ssid']]['guest_pass'],
                      self.use_tou, self.redirect_url)

            #self.target_station.perform_guest_auth(arg)
            if self.conf.get('target_url'):
                arg['target_url'] = self.conf['target_url']
    
            if self.conf.get('expected_data'):
                arg['expected_data'] = self.conf['expected_data']
    
            arg['no_auth'] = bool(self.conf.get('no_auth'))
            messages = self.target_station.perform_guest_auth_using_browser(self.browser_id, arg)
            messages = eval(messages)
            
            errmsg_auth = ''
            passmsg_auth = ''
            for m in messages.iterkeys():
                if messages[m]['status'] == False:
                    errmsg_auth += messages[m]['message'] + " "
    
                else:
                    passmsg_auth += messages[m]['message'] + " "
    
            if errmsg_auth:
                logging.info(errmsg_auth)
                error_at_wlan.append(wlan['ssid'])
                continue
            logging.info(passmsg_auth)
 
            time.sleep(3)

            errmsg, client_info = tmethod.verify_zd_client_is_authorized(
                                      self.zd, self.guestpasses[wlan['ssid']]['user'],
                                      sta_wifi_mac_addr,
                                      self.check_status_timeout)
            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue

            errmsg = tmethod.client_ping_dest_is_allowed(
                         self.target_station,
                         self.dest_ip)

            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan['ssid'])
                continue
            

        self._close_browser_after_auth()
        if self.errmsg:
            logging.info(self.errmsg)
            error_at_wlan.append('close_brower_fail')
            return error_at_wlan
            
        return error_at_wlan


    def _verifyGuestPassWorkOnAllWlans(self):

        error_at_wlan = []
        # Remove all wlan members out of Default group
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default',
                                          self.wlan_name_list, False)

        last_asigned_wlans = []
        logging.info('Verify on wlans %s' % self.conf['tested_wlan_list'])
        verify_wlan_conf_list = []
        for i in self.conf['tested_wlan_list']:                
            verify_wlan_conf_list.append(self.wlan_conf_list[i])

        # Remove all assigned wlans out of Default group
        if last_asigned_wlans:
            lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default',
                                              last_asigned_wlans, False)

        # Apply the selected wlans to Default group for testing
        verify_wlan_name_list = [wlan['ssid'] for wlan in verify_wlan_conf_list]

        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default',
                                          verify_wlan_name_list, True)
        last_asigned_wlans = verify_wlan_name_list

        # Verify on each of wlans
        val = self._verifyStationAssociation(verify_wlan_conf_list)
        error_at_wlan.extend(val)

        if error_at_wlan:
            self.errmsg = 'The Guest Pass did not work on wlans %s' % \
                          str(error_at_wlan)

        else:
            self.passmsg = 'The Guest Access policy worked well on %d wlans' % \
                           len(self.wlan_conf_list)
                           
    def _start_browser_before_auth(self):
        '''
        Start browser in station.
        '''
        try:
            logging.info("Try to start a %s browser on station" % (self.conf['browser_name']))
            self.browser_id = self.target_station.init_and_start_browser(self.conf['browser_name'],
                                                                         self.conf['start_browser_tries'], 
                                                                         self.conf['start_browser_timeout'])
        except Exception, ex:
            self.errmsg = ex.message
            
    def _close_browser_after_auth(self):
        try:
            logging.info("Try to close the browser on station")
            self.target_station.close_browser(self.browser_id)
            
        except Exception, ex:
            self.errmsg = ex.message
            

