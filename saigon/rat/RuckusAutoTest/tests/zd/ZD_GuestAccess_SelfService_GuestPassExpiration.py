# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_GuestPass Expiration Test class tests the usage of guest pass when it's expired.
The guest pass will expire in amount of specified time after it's first used or after it's issued

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and ZD

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station_ip': 'ip address of target station',
                    'is_pass_expired_after_used': 'This is the bool value used to decide guest pass will be expired
                                                   even if it is first use or not. If it is False, the guest pass will
                                                   be expired even if it's not used. Otherwise, the guest pass will be
                                                   expired after it's first used'

   Result type: PASS/FAIL/ERROR
   Results: PASS: If 'is_pass_expired_after_used' is True, the guest pass must be used to authenticate client successfully
                   first. The client is in the 'Authorized' status. After the valid time of this guest pass is over, the client still
                   associates to the wlan, but its status now is "Unauthorized"
                   If 'is_pass_expired_after_used' is False, the client using the expired guest pass to authenticate can associate to the
                   wireless network, but its status is always "Unauthorized".
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configurations about WLANs, users, authentication servers, and active clients on the ZD
       - Remove all guest passes if existed
   2. Test:
       - Configure a WLAN on the ZD with open security setting
       - Configure Guest Access policy and configure a user which will be used to generate guest pass
       - Open another browser, browse to the Guest Pass Generation page and generate a guest pass
       - If 'is_pass_expired_after_used' is True:
           + Configure the target station with given security setting
           + Wait until it gets associated and get IP and MAC addresses of the wireless adapter
           + Do Guest authentication from the station
           + Verify if the ZD shows correct information about the connected station, and the station's status now is
           "Authorized"
       - Increase PC time so that it is later than the valid time of guest pass. Perform synchronizing between ZD
        system time and PC time. The guest pass is expired now.
       - If 'is_pass_expired_after_used' is True, verify that the station still asscociates to the wireless network,
       but its status now is "Unauthorized"
       - If 'is_pass_expired_after_used' is False:
           + Configure the target station with given security setting
           + Wait until it gets associated and get IP and MAC addresses of the wireless adapter
           + Do Guest authentication from the station
           + Verify the station's status now is "Unauthorized"
   3. Cleanup:
       - Remove all wlan configuration and generated guest passes on ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completely disconnected after removing the wireless profile

   How it is tested?
       - While the test is running, right after the guest pass is generated, change PC time so that it's sooner than
       the valid time of guest pass. Synchronize it with ZD system time. The test script should report FAIL because
       the guest pass is not expired and station's status shown on the ZD is "Authorized"
"""

import os
import logging
import time
import datetime

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd.ZD_GuestAccess_Common import ZD_GuestAccess_Common
from urllib2 import URLError

import libZD_TestConfig as tconfig
import libZD_TestConfig as tconfig


UNIT_TO_HOURS = {"Days": 24,
                 "Hours": 1,
                 "Weeks": 7 * 24,
                }
class ZD_GuestAccess_SelfService_GuestPassExpiration(Test):
    required_components = ['Station', 'ZoneDirector']
    parameter_description = {'is_pass_expired_after_used': 'This is the bool value used to decide guest pass will be expired \
                                                            even if it is used or not',
                             'target_station_ip': 'ip address of target station'}

    def config(self, conf):
        
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
     

    def test(self):
     
        if self.conf['start_browser_before_auth']:
            self._start_browser_before_auth()
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
            
        self._testGuestPassExpiration()
        
        if self.conf['close_browser_after_auth']:
            time.sleep(5)
            self._close_browser_after_auth()
        
        if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)

        return ("PASS", self.passmsg.strip())

    def cleanup(self):
    
        pass
    
    
    def _init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_ins':"",
            'sta_tag': "",
            'browser_id':"",
            'browser_tag': "browser",
            'start_browser_before_auth': True,
            'browser_name': "firefox",
            'close_browser_after_auth': True,
            'check_status_timeout': 100,
            'start_browser_tries': 3,
            'start_browser_timeout': 15,           
            'redirect_url': "",
            'target_url': "http://172.16.10.252/",
            'guest_pass': "",
            'use_tou': False,#Terms of Use
            'use_tac':False,#Terms and Conditions
            'no_auth': False,
            'expected_data': "It works!",
            'user_register_infor':{'username':'test.user','email':'test.user@163.com','countrycode':'','mobile':''},
       
            'duration': 1,
            'duration_unit': 'Days',
            'check_access_duration':False,
            'is_pass_expired_after_used':True,
            'first_use':False,
            'sta_mac':None,
            'wlan_cfg':{}
            
        }
        
        self.conf.update(conf)

        self.wlan_cfg= conf['wlan_cfg']
        self.sta_tag = self.conf['sta_tag']
        self.username = self.conf['user_register_infor']['username']
        self.zd = self.testbed.components['ZoneDirector']
        
        self.sta_wifi_mac_addr = None
        self.sta_wifi_ip_addr = None
      
        self.errmsg = ""
        self.passmsg = "sta perform authorize successfully"

    def _retrive_carrier_bag(self):
        '''
        '''
        self.sta = self.conf.get('sta_ins')
        if not self.sta and self.sta_tag:
            sta_dict = self.carrierbag.get(self.sta_tag)
            self.sta = sta_dict.get('sta_ins')
            self.sta_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']

        if not self.sta:
            raise Exception("No station provided.")
        
        self.guest_pass = self.conf.get('guest_pass')
        if not self.guest_pass:
            self.guest_pass = self.carrierbag.get('guest_pass') 
            if not self.guest_pass:
                self.errmsg = "sorry,your guest pass is null,please provide guest pass"
            
        self.conf.update({'guest_pass':self.guest_pass})

        if not self.conf['start_browser_before_auth']:
            self.browser_id = self.conf.get('browser_id')
            if not self.browser_id:
                browser_dict = self.carrierbag.get(self.conf['browser_tag'])
                self.browser_id = browser_dict.get('browser_id')
    
            if not self.browser_id:
                raise Exception("No Browser provided.")


    def _start_browser_before_auth(self):
        '''
        Start browser in station.
        '''
        try:
            logging.info("Try to start a %s browser on station[%s]" \
                        % (self.conf['browser_name'], self.sta_tag))
            self.browser_id = self.sta.init_and_start_browser(self.conf['browser_name'],
                                                              self.conf['start_browser_tries'], 
                                                              self.conf['start_browser_timeout'])
            self.browser_id = int(self.browser_id)
            self.passmsg += "The %s browser on station '%s' was started successfully with ID[%s]" \
                              % (self.conf['browser_name'], self.sta_tag, self.browser_id)            

        except Exception, ex:
            self.errmsg += ex.message
    
    
    def _close_browser_after_auth(self):
        try:
            logging.info("Try to close the browser with ID[%s] on station[%s]" \
                         % (self.browser_id, self.sta_tag))
            self.sta.close_browser(self.browser_id)
            self.passmsg += 'Close browser with ID[%s] on station[%s] successfully.' \
                            % (self.browser_id, self.sta_tag)
        
        except Exception, ex:
            self.errmsg += ex.message

    def _cfgRemoveAllWlanProfilesOnStation(self):
        for station in self.station:
            if station.get_ip_addr() == self.conf['target_station_ip']:
                # Found the target station
                self.target_station = station
                self._cfgRemoveStationWlanProfiles()
                break

        if not self.target_station:
            errmsg = "Target station % s not found. " % self.conf['target_station']
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise Exception(errmsg)


    def _cfgRemoveStationWlanProfiles(self):
        logging.info("Remove all WLAN profiles on the remote station")
        self.target_station.remove_all_wlan()

        logging.info("Make sure the target station %s disconnects from wireless network" %
                     self.target_station.get_ip_addr())

        errorMsg = "The station did not disconnect from wireless network within %d seconds"

        return self._checkConnectionStatus("disconnected", self.conf['check_status_timeout'], errorMsg)


    def _checkConnectionStatus(self, status, timeout, errorMsg):
        start_time = time.time()
        while True:
            if self.sta.get_current_status() == status:
                return True

            time.sleep(1)
            if time.time() - start_time > timeout:
                errmsg = errorMsg % timeout
                self.errmsg = self.errmsg + errmsg
                raise Exception(errmsg)
                return False

    # no use
    def _checkValidGuestPassExpiration(self, guestpass_info):
        # If GuestPass is expired in the amount of time after it's first used,
        # the maximum valid time of this GuestPass is the current time on ZD plus the valid days
        # which configured in the GuestPass expiration policy
        max_expired_time = self.zd.get_current_time()
        max_expired_time = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(max_expired_time, "%A, %B %d, %Y %H:%M:%S %p")) # %p
        max_expired_time = time.mktime(time.strptime(max_expired_time.split()[0], "%Y/%m/%d")) + self.conf['expired_duration'] * 24 * 3600
        guestpass_time = guestpass_info['expire_time']
        guestpass_time = time.mktime(time.strptime(guestpass_time.split()[0], "%Y/%m/%d"))

        if guestpass_time != max_expired_time:
            logging.info("The configured expired time for Guest Pass is: %s" % guestpass_time)
            logging.info("The right expired time for Guest Pass is: %s" % max_expired_time)
            errmsg = "The expired time for the Guest Pass %s is not right. " % self.guest_pass
            self.errmsg = self.errmsg + errmsg
            logging.debug(errmsg)


    def _checkExpirityStatus(self):
        # Make sure that target station is in the "Unauthorized" status after doing guest auth with expired guest pass
        time.sleep(2)
        logging.info("Verify information of the target station shown on the ZD")
        client_info_on_zd = None
        start_time = time.time()

        contd = True
        while contd:
            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    if self.conf.get('first_use'):
                        if client['status'] == 'Unauthorized':
                            logging.debug("Active Client: %s" % str(client))
                            errmsg = "The status of station is %s instead of 'Authorized'"
                            errmsg += "after doing Guest authentication with first use Guest Pass. " % client['status']
                            self.errmsg = self.errmsg + errmsg
                            logging.debug(errmsg)
                            return
                    else:
                        if client['status'] == 'Authorized':
                            logging.debug("Active Client: %s" % str(client))
                            errmsg = "The status of station is %s instead of 'Unauthorized'"
                            errmsg += "after doing Guest authentication with expired Guest Pass. " % client['status']
                            self.errmsg = self.errmsg + errmsg
                            logging.debug(errmsg)
                            return

                    client_info_on_zd = client
                    contd = False

                    break #the for loop

            if not contd or time.time() - start_time > self.conf['check_status_timeout']:
                logging.debug("Active Client: %s" % str(client_info_on_zd))
                logging.info("The status of station is %s now" % client_info_on_zd['status'])

                break #the while loop

        if not client_info_on_zd:
            logging.debug("Active Client List: %s" % str(active_client_list))
            errmsg = "ZD didn't show any info about the target station (with MAC %s). " % self.sta_wifi_mac_addr
            self.errmsg = self.errmsg + errmsg
            logging.debug(errmsg)


    def _associateClient(self):
        logging.info("Configure a WLAN with SSID %s on the target station %s" %
                        (self.wlan_cfg['ssid'], self.sta.get_ip_addr()))
        self.sta.cfg_wlan(self.wlan_cfg)

        logging.info("Make sure the station associates to the WLAN")

        errorMsg = "The station didn't associate to the wireless network after %d seconds"

        self._checkConnectionStatus("connected", self.conf['check_status_timeout'], errorMsg)

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.sta.renew_wifi_ip_address()

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % \
                     self.sta.get_ip_addr())

        start_time = time.time()

        while time.time() - start_time < self.conf['check_status_timeout']:
            self.sta_wifi_ip_addr, self.sta_wifi_mac_addr = self.sta.get_wifi_addresses()
            if self.sta_wifi_mac_addr and self.sta_wifi_ip_addr and self.sta_wifi_ip_addr != "0.0.0.0" and \
               not self.sta_wifi_ip_addr.startswith("169.254"):
                break

            time.sleep(1)



    def _perform_selfguest_auth(self):
        '''
        '''
        logging.info("Perform Guest Auth on the station %s" % self.sta_tag)

        try:
            messages = self.sta.perform_self_service_guest_auth_using_browser(self.browser_id, self.conf)
            messages = eval(messages)
            
            for m in messages.iterkeys():
                if messages[m]['status'] == False:   
                    self.errmsg += messages[m]['message'] + " "
                else:
                    self.passmsg += messages[m]['message'] + " "
                    
            if self.errmsg:
                return
            

            self.passmsg = "Perform Guest Auth successfully on station [%s]." % self.sta_tag
            logging.info(self.passmsg)

        except Exception, e:
            self.errmsg += e.message
            logging.info(self.errmsg)


    


    def _testGuestPassExpiration(self):


        if self.conf['is_pass_expired_after_used']:
            self._associateClient()
            self._perform_selfguest_auth()

        #sysnc zd time with your pc
        self.zd.get_current_time(True)
        
        
        # Get guest pass information in the Generated Guest Passes table
        guest_passes_info_dict = lib.zd.ga.get_all_selfguestpasses(self.zd)
        expire_time = guest_passes_info_dict.get(self.username).get('expire_time')
        guest_pass = guest_passes_info_dict.get(self.username).get('key')
        logging.info("The Guest Pass %s is valid until %s" %(guest_pass, expire_time))
             
                     
        # change pc time so that the guestpass are expired
        logging.info("Change ZD time so that all the generated guest passes are expired")
        duration_hours = self.conf['duration'] * UNIT_TO_HOURS[self.conf['duration_unit']]
        tmptime = datetime.datetime.now() + datetime.timedelta(hours = duration_hours)
        os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
        time.sleep(5)
        
        #sysnc zd time with your pc
        self.zd.get_current_time(True)
        
        try:
            if self.conf['is_pass_expired_after_used']:
                self.zd.remove_all_active_clients()
            else:
                self._associateClient()
                self._perform_selfguest_auth()
                if self.errmsg in ['Invalid Guest Pass '] and not self.conf.get('first_use'):
                    self.errmsg = ""
                    self.passmsg = "success,the guest pass had expired."

        except:
            raise

        finally:
            self._restore_zd_time()

        if self.conf.has_key('is_pass_expired_after_used') and self.conf['is_pass_expired_after_used']:
            msg = 'Effective from first use'
        else:
            msg = 'Effective from the creation time'

        self.passmsg = "Guest pass is expired correctly when option %s is selected. " % msg
        
        
    def _restore_zd_time(self):
        logging.debug("Restore the previous system time of ZD")
        
        duration_hours = self.conf['duration'] * UNIT_TO_HOURS[self.conf['duration_unit']]
        tmptime = datetime.datetime.now() - datetime.timedelta(hours = duration_hours)
        
        os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
        time.sleep(5)
        self.zd.get_current_time(True)




