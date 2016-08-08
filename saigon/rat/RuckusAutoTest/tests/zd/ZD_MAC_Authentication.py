# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
    This script use to test the MAC authentication functionality, includes:
        Valid/Invalid user/pass, test with different WLAN configuration,
        with Isolation, with IAS (Radius server on Win 2K3),
        with freeRadius server, blocking invalid user.

Author: An Nguyen
Email: nnan@s3solutions.com.vn

Prerequisite (Assumptions about the state of the testbed/DUT):
1. Build under test is loaded on the AP and Zone Director

Required components: 'RuckusAP', 'ZoneDirector'
Test parameters:
    'testcase':
        define the testcase will be test, ex: with-isolation.
    'auth_server_info':
        the dictionary of radius server configuration.
    'wlan_conf':
        the dictionary of wlan configuration will be test.
    'authorized_station':
        the IP address of the client that be authenticated by server.
    'unauthorized_station':
        the IP address of the client that is not authenticated by server.

Result type: PASS/FAIL/ERROR
Results:

Messages:
    If FAIL the test script return a message related to the criteria that
    is not satisfied

Test procedure:
1. Config:
    - Create the radius server for MAC authentication on Zone Director base on
      the 'auth_server_info'.
    - Create the WLAN base on the 'wlan_conf' parameter that use the
      server above for authentication.
2. Test:
    - Do the test process base on 'testcase' parameter:
        + Valid/Invalid user/pass:
            - Try to access both valid and invalid station to the network.
            - The valid station could access to the network and be authenticated.
            - The invalid station could not access to the network
        + With different encryption/with IAS/with freeRadius:
            - Verify the valid could access to the network successfully
              (The 'auth_server_info' and 'wlan_conf' parameters will decide
               the test case)
        + With Isolation:
            - Verify valid station could access and be authenticated
            successfully.
            - Station ping to the server is allowed.
            - Update WLAN to enable the 'Wireless Clients Isolation' option.
            - Verify the Isolation function is worked well; it's mean
              the station could not ping to server which is in the same subnet.
3. Cleanup:
    - Restore all non-default setting on Zone Director

How it is tested?

"""

import time
import logging
from copy import deepcopy
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class ZD_MAC_Authentication(Test):
    required_components = []
    test_parameters = {'testcase':'',
                       'auth_server_info':'{}',
                       'wlan_conf':'{}',
                       'authorized_station':'',
                       'unauthorized_station':''}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cleanupZoneDirectorSetting()
        self._cfgActiveAP()

    def test(self):
        self._cfgTheAuthenServerOnZD()
        self._cfgWLAN()
        self._remove_all_wlanOnNonActiveAPs()

        self.test_function[self.conf['testcase']]()
        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg_dict[self.conf['testcase']])

    def cleanup(self):
        self._cleanupZoneDirectorSetting()

    def _initTestParameters(self, conf):
        self.conf = {'testcase':'',
                     'auth_server_info':{},
                     'wlan_conf':{'auth':'mac', 'encryption':'none'},
                     'authorized_station':'',
                     'unauthorized_station':'',
                     'check_status_timeout':180
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = None

        self.authorized_station, authorized_sta_wifi_mac_addr = \
            self._cfgStation(self.conf['authorized_station']) \
            if self.conf['authorized_station'] else (None, '')

        self.unauthorized_station, self.unauthorized_sta_wifi_mac_addr = \
            self._cfgStation(self.conf['unauthorized_station']) \
            if self.conf['unauthorized_station'] else (None, '')

        self.errmsg = ''

        self.test_function = {
            'with-valid-and-invalid-client':
                self._testMACAuthentication,
            'with-encryption-type':
                self._testMACAuthentication,
            'with-IAS':
                self._testMACAuthentication,
            'with-free-radius':
                self._testMACAuthentication,
            'with-blocking-the-invalid-client':
                self._testBlockingTheUnauthorizedClient,
            'with-isolation':
                self._testIsolationFunctionality
        }

        self.passmsg_dict = {
            'with-valid-and-invalid-client':
                'The valid client is authenticated successfully and the '\
                'invalid client is not authorized',
            'with-encryption-type':
                'The MAC Authentication with Encryption [%s] worked well' % \
                self.conf['wlan_conf'],
            'with-IAS':
                'The MAC Authentication IOP with IAS (Win2003) worked well',
            'with-free-radius':
                'The MAC Authentication IOP with FreeRadius worked well',
            'with-blocking-the-invalid-client':
                'The invalid client is blocked correct with the behavior',
            'with-isolation':
                'The Isolation option worked well on MAC Authentication WLAN'
        }


    def _cleanupZoneDirectorSetting(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)
        #lib.zd.aaa.remove_all_servers(self.zd)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        


    def _cfgActiveAP(self):
        if self.conf.get('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(
                                 self.testbed,
                                 self.conf['active_ap'])

            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" %
                                self.conf['active_ap'])

            self.active_ap_mac = self.active_ap.base_mac_addr.lower()


    def _remove_all_wlanOnNonActiveAPs(self):
        if self.active_ap:
            for ap in self.testbed.components['AP']:
                if ap is not self.active_ap:
                    logging.info("Remove all WLAN on non-active AP %s" %
                                 ap.ip_addr)
                    ap.remove_all_wlan()

            logging.info("Verify WLAN status on the active AP %s" %
                         self.active_ap.ip_addr)

            if not self.active_ap.verify_wlan():
                raise Exception('Not all WLAN are up on active AP %s' %
                                self.active_ap.ip_addr)

    def _cfgStation(self, station_ip_addr):
        station = tconfig.get_target_station(
                      station_ip_addr,
                      self.testbed.components['Station'],
                      check_status_timeout = self.conf['check_status_timeout'],
                      remove_all_wlan = True)

        if not station:
            raise Exception("Target station %s not found" % station_ip_addr)

        # Get MAC address of wireless adapter on the target station.
        # This address is used as the restricted MAC address in an ACL rule
        try:
            sta_wifi_ip_addr, sta_wifi_mac_addr = station.get_wifi_addresses()

        except:
            raise Exception("Unable to get MAC address of the wireless adapter "
                            "of the target station %s" % station_ip_addr)

        return (station, sta_wifi_mac_addr)


    def _cfgTheAuthenServerOnZD(self):
        logging.info('Configure the external server on Zone Director')
        lib.zd.aaa.create_server(self.zd, **self.conf['auth_server_info'])


    def _cfgWLAN(self):
        self.wlan_conf = {'auth':'mac', 'encryption':'none'}
        self.wlan_conf.update(self.conf['wlan_conf'])
        self.wlan_conf.update({'ssid':'WLAN for MAC Auth - %s' % time.strftime("%H%M%S"),
                               'auth_svr':self.conf['auth_server_info']['server_name']})

        if self.wlan_conf['auth'] != 'mac':
            raise Exception('The authentication method is "%s" instead of '
                            'MAC Address' % self.wlan_conf['auth'])

        lib.zd.wlan.create_wlan(self.zd, self.wlan_conf)


    def _verifyClientAssocciation(self, station, wlan_conf, allow_access = True):
        errmsg = ''
        fail_connected = tmethod.assoc_station_with_ssid(
                             station, wlan_conf,
                             self.conf['check_status_timeout'])

        if allow_access and fail_connected:
            errmsg = '[Incorrect behavior] The access is allowed and %s' % \
                     fail_connected.lower()

        elif allow_access and not fail_connected :
            logging.info('[Correct behavior] Client access to the network [%s] '
                         'successfully' % wlan_conf['ssid'])

        elif not allow_access and fail_connected:
            logging.info('[Correct behavior] The access is not allowed and %s' %
                         fail_connected.lower())

        elif not allow_access and not fail_connected:
            errmsg = '[Incorrect behavior] The access is not allowed but '\
                     'the client still could access to the network [%s]'
            errmsg = errmsg % wlan_conf['ssid']

        if errmsg:
            logging.info(errmsg)
            self.errmsg = errmsg

    def _verifyJoiningEventOnZD(self, sta_wifi_mac, wlan_name, join_success = True):

        s_time = time.time()
        while time.time() - s_time < 150:
            events_on_zd = self.zd.get_events()
            logging.debug('VerifyJoiningEventOnZD------events: %s' % events_on_zd)
            expected = ''
            if join_success:
                expected = 'User[%s] joins WLAN[%s] from AP'
                # MSG_client_join={user} joins {wlan} from {ap}
                expected = self.zd.messages['MSG_client_join']            
                expected = expected.replace('{user}', 'User[%s]' % sta_wifi_mac.lower())
                expected = expected.replace('{wlan}', 'WLAN[%s]' % wlan_name)
                expected = expected.replace('{ap}', '')
                
            else:
    #           expected = 'User[%s] repeatedly fails authentication when joining WLAN[%s] at AP'
                expected = 'User[%s] fails authentication too many times in a row when joining WLAN[%s]' % (sta_wifi_mac.lower(), wlan_name)        
                # MSG_client_auth_fail_block={user} fails authentication too many times in a row when joining {wlan} at {ap}.\ 
                #{user} is temporarily blocked from the system for {block}.
                # MSG_client_repeat_auth_fail={user} repeatedly fails authentication when joining {wlan} at {ap}.
                #Update@20120619 by Zoe, for behavior change when do authenticate.
                expected = self.zd.messages['MSG_client_auth_fail_block']
                expected = expected.split('{ap}')[0]
                expected = expected.replace('{user}', 'User[%s]' % sta_wifi_mac.lower())
                expected = expected.replace('{wlan}', 'WLAN[%s]' % wlan_name)
            
    
            for event in events_on_zd:
                if expected in event[3]:
                    return
            
            time.sleep(10)
        
        if join_success:
            self.errmsg = 'The joining event of client [%s] to WLAN [%s] '\
                          'is not recorded when client joins.' % (sta_wifi_mac, wlan_name)
        else:
            self.errmsg = 'The joining event of client [%s] to WLAN [%s] '\
                          'is not recorded when client do fail authentication.' % (sta_wifi_mac, wlan_name)
                          
        logging.info(self.errmsg)


    def _verifyBlockingEventOnZD(self, sta_wifi_mac, wlan_name):
        s_time = time.time()
        while time.time() - s_time < 150:
            events_on_zd = self.zd.get_events()
            logging.debug('VerifyBlockingEventOnZD------events: %s' % events_on_zd)
            expect_event = 'User[%s] is temporarily blocked from the system for'
            # MSG_client_auth_fail_block={user} fails authentication too many times \
            # in a row when joining {wlan} at {ap}. {user} is temporarily blocked \
            # from the system for {block}.
            expect_event = self.zd.messages['MSG_client_auth_fail_block']
    
            event_list = expect_event.split('.')
            for s in event_list:
                if s.find('{block}') >= 0:
                    expect_event = s
    
            expect_event = expect_event.replace(' {user}', 'User[%s]' % sta_wifi_mac.lower())
            expect_event = expect_event.replace('{block}', '')
    
    
            for event in events_on_zd:
                if expect_event in event[3]:
                    return
            time.sleep(10)

        self.errmsg = 'The blocking event of client [%s] is not recorded' % \
                      (sta_wifi_mac)
        logging.info(self.errmsg)


    def _testMACAuthentication(self):
        self.zd.clear_all_events()
        if not self.authorized_station:
            raise Exception('There is not any authorized station for testing')
        
        # Verify the valid client could access to the network and \
        # be authorized successfully
        self.errmsg = self._verifyClientAssocciation(
                          self.authorized_station, self.wlan_conf,
                          allow_access = True)

        if self.errmsg:
            return

        val, val1, val2 = tmethod.renew_wifi_ip_address(
                              self.authorized_station,
                              self.conf['check_status_timeout'])
        if not val:
            raise Exception(val2)

        authorized_sta_wifi_ip_addr = val1.lower()
        authorized_sta_wifi_mac_addr = val2.lower()

        # Verify if the client is authorized with the user name is its wifi MAC
        self.errmsg, client_info = tmethod.verify_zd_client_is_authorized(
                                       self.zd, authorized_sta_wifi_ip_addr,
                                       authorized_sta_wifi_mac_addr,
                                       self.conf['check_status_timeout'])
        if self.errmsg:#chen.tao 2014-2-24, to fix ZF-7570
            tmp_mac_addr1 = deepcopy(authorized_sta_wifi_mac_addr)
            self.errmsg, client_info = tmethod.verify_zd_client_is_authorized(
                                           self.zd,''.join(tmp_mac_addr1.split(':')).lower(),
                                           authorized_sta_wifi_mac_addr,
                                           self.conf['check_status_timeout'])
        if self.errmsg:
            return

        # Verify if the client could ping to the radius server successfully \
        # if the access is allowed
        self.errmsg = tmethod.client_ping_dest_is_allowed(
                          self.authorized_station,
                          self.conf['auth_server_info']['server_addr'])

        if self.errmsg:
            return

        # Verify if there are the event about client joining in Zone Director
        self._verifyJoiningEventOnZD(authorized_sta_wifi_mac_addr,
                                     self.wlan_conf['ssid'],
                                     join_success = True)
        if self.errmsg:
            self.authorized_station.remove_all_wlan()
            tmethod.assoc_station_with_ssid(self.authorized_station, self.wlan_conf, self.conf['check_status_timeout'])
            self._verifyJoiningEventOnZD(authorized_sta_wifi_mac_addr,
                                         self.wlan_conf['ssid'],
                                         join_success = True)
        
        if self.errmsg:#chen.tao 2014-2-24, to fix ZF-7570
            self.errmsg = ''
            tmp_mac_addr2 = deepcopy(authorized_sta_wifi_mac_addr)
            self._verifyJoiningEventOnZD(''.join(tmp_mac_addr2.split(':')).lower(),
                                     self.wlan_conf['ssid'],
                                     join_success = True)
        if self.errmsg:
            return

        # Verify the invalid client could not access to the network
        if not self.unauthorized_station:
            if self.conf['testcase'] == 'with-valid-and-invalid-client':
                raise Exception('There is not any unauthorized station for testing')

            return

        self._verifyClientAssocciation(self.unauthorized_station,
                                       self.wlan_conf,
                                       allow_access = False)

        if self.errmsg:
            return

        # Verify the client be blocked
        self._verifyJoiningEventOnZD(self.unauthorized_sta_wifi_mac_addr,
                                     self.wlan_conf['ssid'],
                                     join_success = False)
        if self.errmsg:
            return


    def _testBlockingTheUnauthorizedClient(self):
        self.zd.clear_all_events()
        # Verify the invalid client could not access to the network
        if not self.unauthorized_station:
            if self.conf['testcase'] == 'with-valid-and-invalid-client':
                raise Exception('There is not any unauthorized station for testing')

        self._verifyClientAssocciation(self.unauthorized_station,
                                       self.wlan_conf,
                                       allow_access = False)
        if self.errmsg:
            return

        # Verify the client be blocked
        self._verifyJoiningEventOnZD(self.unauthorized_sta_wifi_mac_addr,
                                     self.wlan_conf['ssid'],
                                     join_success = False)
        if self.errmsg:
            return

        # Verify if the blocking event is recorded on Zone Director
        self._verifyBlockingEventOnZD(self.unauthorized_sta_wifi_mac_addr,
                                      self.wlan_conf['ssid'])

        if self.errmsg:
            return

    def _testIsolationFunctionality(self):
        self._testMACAuthentication()
        if self.errmsg: return

        logging.info('Enable "Wireless Client Isolation" option on the WLAN')
        lib.zd.wlan.edit_wlan(self.zd, self.wlan_conf['ssid'], {'do_isolation':True})
        time.sleep(5)

        logging.info('Verify if target station could ping to an IP in same subnet')
        errmsg = tmethod.client_ping_dest_not_allowed(
                     self.authorized_station,
                     self.conf['auth_server_info']['server_addr'])

        if errmsg:
            msg = '[Incorrect Behavior] %s while Wireless Client Isolation '\
                  'is enabled on wlan "%s"'
            #@author: chen.tao 2013-12-19, to fix bug ZF-6514
            #msg = msg % (errmsg, self.test_wlan_conf['ssid'])
            msg = msg % (errmsg, self.wlan_conf['ssid'])
            #@author: chen.tao 2013-12-19, to fix bug ZF-6514
            self.errmsg = msg
            logging.info(self.errmsg)
            return

        else:
            msg = '[Correct Behavior]: Target station could not ping "%s"'
            msg = msg % self.conf['auth_server_info']['server_addr']
            logging.info(msg)

