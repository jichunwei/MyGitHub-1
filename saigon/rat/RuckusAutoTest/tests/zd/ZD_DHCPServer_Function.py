# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is use for 5 testcases in DHCP Server testsuites of Odessa test plan
Limitation: This script work well for testbed that all AP connected to ZD in L2 mode otherwise may be return error.

Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'test_option': the expected options will be tested.
                                Ex.'dhcp server', 'lease time', 'enable/disable', 'valid ip' or 'view ip assignments'
                    'target_station': the target station that be under test
   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Define all parameters for testing
       - Clear all wlan of Zone Director
       - Clear all wifi configuration on the target station
   2. Test:
       - Base on test option, we will test:
            + 'dhcp server': DHCP server works only with static IP
              1. Verify that we couldn't configure DHCP server with dynamic IP
              2. Verify that we could configure DHCP server with static IP
                a. Disable the out side DHCP server
                b. Configure the DHCP server
                c. Create an wlan and an association with station
                d. Verify that station get IP from Zd dhcp server correctly (ip, dhcp server info, lease time)
            + 'lease time':
              1. Verify that we could configure DHCP server with static IP
              2. Verify if the ZD time passed the leasetime of station, that entry will be remove
            + 'enable/diasble', 'valid ip', 'view ip assignments':
              - Verify if DHCP server webUI fields work correctly. Invalid valid is not allowed.
   3. Cleanup:
       - Restore the ZD configuration
       - Restore the server configuration

   How it is tested?
       -
"""

import os
import time
import re
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI
from datetime import datetime,timedelta

zd_datetime_format = '%A, %B %d, %Y %I:%M:%S %p'
linux_time_format = '%m%d%H%M%y.%S'
zd_leasetime_format = '%Y/%m/%d  %H:%M:%S'
sta_leasetime_format = '%A, %B %d, %Y %I:%M:%S %p'
reg_zd_leasetime ="(\d*)d (\d*)h (\d*)m"

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_DHCPServer_Function(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        """
        """
        self._initTestParameters(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()

        logging.info("Record current IP configuration of the ZD")
        self.ip_info_backup = self.zd.get_ip_cfg()

        logging.info("Record current DHCP server configuration of the ZD")
        self.zd_dhcp_srv_cfg = self.zd.get_dhcp_server_info()

    def test(self):
        """
        """
        # The ZD DHCP server only works with static IP
        if self.test_option == 'dhcp server':
            self._testDHCPSerWithDynamicIP()
            if self.errmsg:
                return ('FAIL', self.errmsg)
        
            self._testDHCPSerWithStaticIP()
            if self.errmsg:
                return ('FAIL', self.errmsg)

        # Verify that station got the correct lease time info,
        # and that entry will be remove when the leasetime pass
        elif self.test_option == 'lease time':
            self._testLeaseTime()
            if self.errmsg:
                return ('FAIL', self.errmsg)

        # Verify for DHCP server WebUI fields
        else:
            self._testDHCPServerFields()
            if self.errmsg:
                return ('FAIL', self.errmsg)

        return ('PASS', '')

    def cleanup(self):
        """
        """
        logging.info('Clean up the testing environment')
        # Set the date time on NTP server base on the current time on the test engine
        if self.linux_server:
            self._cfgTimeOnLinuxServer(time.strftime('%m%d%H%M%y', time.localtime(time.time())))
            self.linux_server.start_dhcp_server()

        # Return the config on the ZD (DUT)
        if self.ntp_conf_bkup:
            self.zd.cfg_ntp(self.ntp_conf_bkup)
        self.zd.get_current_time(True)
        logging.info('Restore NTP config on ZD successfully')

        logging.info('Remove all configuration on the Zone Director')
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']  
        try:
            self.zd.goto_login_page()
        except:
            time.sleep(10)
            self.zd.goto_login_page()
              
#        import lib_clean_up as cls
#        cls.remove_all_cfg(self.zd, self.zdcli)
        self.zd.remove_all_wlan()      


        self.zd.set_dhcp_server({})
        self.zd.set_ip_cfg_status('dhcp')
        return
        
        #@author: lipingping @bug: ZF-8904 @since: 2014.7.17
#        if self.zd_dhcp_srv_cfg:
#            logging.info('Restore default DHCP server configuration of the ZD')
#            self.zd.set_dhcp_server(self.zd_dhcp_srv_cfg)
#
#        if self.ip_info_backup:
#            logging.info('Restore the original IP configuration of Zone Director')
#            self.zd.set_ip_cfg(self.ip_info_backup)
#
#            logging.info('Restart all APs to make sure they get IP from external DHCP server')
#            self._restartAllAPs()

    def _testDHCPSerWithDynamicIP(self):
        """
        """
        # Verify if the 'DHCP Server' is invisible in case ZD get dynamic IP
        self.zd.set_ip_cfg_status('dhcp')
        if not self.zd.get_dhcp_server_info():
            self.errmsg = ''
        else:
            self.errmsg = 'The DCHP Server field is visible while Zone Director is using dynamic IP'
            logging.info(self.errmsg)

    def _testDHCPSerWithStaticIP(self):
        """
        """
        # Stop the outside DHCP server if it exists
        self.linux_server = self.testbed.components['LinuxServer']
        self.linux_server.stop_dhcp_server()
        # Setting Zone Director to use static IP
        self.zd.set_ip_cfg(self.valid_ip_conf)
        if self.errmsg: return

        # Verify if 'DHCP Server' is visible and could be configured successfully
        self._verifyDHCPSerConfig(self.testing_dhcpser_conf)
        if self.errmsg: return

        # Config a wlan
        self.zd.cfg_wlan(self.wlan_cfg)
        if self.errmsg: return
        
        # Verify if station could get IP from the ZD DHCP Server
        self._verifyStationConnection()
        if self.errmsg: return

        # Verify the DHCP server information on the station
        self._verifyDHCPSerInfo()

    def _testDHCPServerFields(self):
        """
        """
        # Setting Zone Director to use static IP
        self.zd.set_ip_cfg(self.valid_ip_conf)
        if self.errmsg: return
        # Verify if we could enable/disable DHCP server on Zone Director
        if self.test_option == 'enable/disable':
            # Check to enable DHCP server
            self._verifyDHCPSerConfig(self.testing_dhcpser_conf)
            if self.errmsg: return
            else: logging.info('Enable and configure DHCP Server on Zone Director successfully')
            # Check to disable DHCP server
            self._verifyDHCPSerConfig({})
            if self.errmsg: return
            else: logging.info('Disable DHCP Server on Zone Director successfully')

        # Verify IP setting fields
        elif self.test_option == 'valid ip':
            # Verify IP Start field
            # Invalid IP setting should be prevented
            logging.info('Verify starting IP field with invalid IP')
            for ip in self.invalid_starting_ip_list:
                self._verifyDHCPSerConfig({'start_ip':ip, 'number_ip':1, 'enable': True}, False)
                if self.errmsg:
                    return

            # Verify IP Number (IP Range) field
            # Invalid ip range should be prevented
            logging.info('Verify IP range field with same subnet')
            for range in self.invalid_ip_range_in_same_subnet:
                self._verifyDHCPSerConfig({'start_ip':'192.168.0.9', 'number_ip':range, 'enable': True}, False)
                if self.errmsg:
                    return
            # Valid IP start and IP range would be setting successfully
            for range in self.valid_ip_range_in_same_subnet:
                self._verifyDHCPSerConfig({'start_ip':'192.168.0.9', 'number_ip':range, 'enable': True}, True)
                if self.errmsg:
                    return

            # Verify IP Number field to use different subnets
            # Invalid ip range should be prevented
            logging.info('Verify IP range field with different subnets')
            self.valid_ip_conf['net_mask'] = '255.255.252.0'
            self.zd.set_ip_cfg(self.valid_ip_conf)
            for range in self.invalid_ip_range_in_diff_subnet:
                self._verifyDHCPSerConfig({'start_ip':'192.168.0.9', 'number_ip':range, 'enable': True}, False)
                if self.errmsg:
                    return

            # Valid IP start and IP range would be setting successfully
            for range in self.valid_ip_range_in_diff_subnet:
                self._verifyDHCPSerConfig({'start_ip':'192.168.0.9', 'number_ip':range, 'enable': True}, True)
                if self.errmsg:
                    return

        # Verify if the assigned IP table could be show
        elif self.test_option == 'view ip assignments':
            try:
                assigned_info_on_gui = self.zd.get_assigned_ip_info()
            except Exception, e:
                if e == 'The assigned IP table could not be showed':
                    self.errmsg = e
                    return
                else:
                    raise Exception(e)
        else:
            raise Exception('Invalid testing option [%s]!' % self.test_option)

    def _testLeaseTime(self):
        """
        """
        if self.conf.has_key('leasetime'):
            self.testing_dhcpser_conf['leasetime'] = self.conf['leasetime']
        # Config a DHCP server to test
        # Verify the station could get IP from ZD DHCP server correctly
        self._testDHCPSerWithStaticIP()
        if self.errmsg: return

        # Change time for ZD system pass the station lease time to verify
        # if the ZD DHCP server remove the station entry
        sta_wifi_ip_info = self.target_station.get_ip_config()
        sta_ip_info_on_zd = self.zd.get_assigned_ip_info(sta_wifi_ip_info['ip_addr'])[0]

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 behavior change
        time_now = datetime.now()
        get_time = re.match(reg_zd_leasetime, sta_ip_info_on_zd['leasetime'])
        time_delta = timedelta(days =int(get_time.group(1)),hours=int(get_time.group(2)),minutes=int(get_time.group(3)))
        expire_time = time_now+time_delta
        conf_time = expire_time.strftime(linux_time_format)
        #conf_time = time.strftime(linux_time_format, time.strptime(sta_ip_info_on_zd['leasetime'], zd_leasetime_format))
        self._cfgTimeOnLinuxServer(conf_time)
        self._syncZDTimeWithNTPSrv()
        self.zd.set_dhcp_server({'enable': True})
        sta_assigned_ip_info_on_zd = self.zd.get_assigned_ip_info(sta_ip_info_on_zd['leasetime'])
        if sta_assigned_ip_info_on_zd:
            msg = 'The record of station [%s] still exists but the ZD time passed over the leasetime'
            self.errmsg = msg % sta_assigned_ip_info_on_zd
            return
        logging.info('ZD DHCP server removed the assigned entry when the system time passed the lease time')

    def _verifyDHCPSerConfig(self, dhcp_ser_conf, expected = True):
        """
        """
        logging.info('Verify the DHCP Server configuration')
        try:
            self.zd.set_dhcp_server(dhcp_ser_conf)
        except Exception, e:
            if expected:
                logging.info('Configuration Failed! [Incorrect behavior]')
                self.errmsg = e
            else:
                logging.info('Configuration Failed! [Correct behavior]: [%s]' % e)
                self.errmsg = ''
            return
        self.errmsg = ''
        logging.info('Configuration successfully! [%s]' % str(dhcp_ser_conf))

    def _verifyStationConnection(self):
        """
        """
        logging.info("Configure a WLAN with SSID %s on the target station %s" % (self.wlan_cfg['ssid'],
                                                                                 self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)

        logging.info("Make sure the station associates to the WLAN")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                msg = "The station did not associate to the wireless network within %d seconds" % \
                      self.check_status_timeout
                raise Exception(msg)

        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not res:
            raise Exception(val2)

    def _verifyDHCPSerInfo(self):
        """
        """
        logging.info('Verify DHCP server information of station')
        zd_dhcp_ser_conf = self.zd.get_dhcp_server_info()
        sta_wifi_ip_info = self.target_station.get_ip_config()
        if not sta_wifi_ip_info['ip_addr']:
            self.errmsg = 'Station cannot get the IP address from server'
            return
        if sta_wifi_ip_info['dhcp_server'] != self.zd.ip_addr:
            msg = 'Station get IP address from server [%s] instead of [%s]'
            self.errmsg = msg % (sta_wifi_ip_info['dhcp_server'], self.zd.ip_addr)
            return
        msg = 'Station get IP[%s] from ZD DHCP server[%s] successfully'
        logging.info(msg % (sta_wifi_ip_info['ip_addr'], sta_wifi_ip_info['dhcp_server']))

        logging.info('Compare IP information of station with assigned information on Zone Director')
        sta_assigned_ip_info_on_zd = self.zd.get_assigned_ip_info(sta_wifi_ip_info['ip_addr'])
        if not sta_assigned_ip_info_on_zd:
            msg = 'The entry of IP[%s] did not exist on the Assigned IP table'
            self.errmsg = msg % sta_wifi_ip_info['ip_addr']
            return
        sta_ip_info_on_zd = sta_assigned_ip_info_on_zd[0]

        # Verify if the mac address id correct
        if sta_wifi_ip_info['mac_addr'].lower() != sta_ip_info_on_zd['mac'].lower():
            msg = 'IP[%s] is assigned for [%s] instead of [%s]'
            self.errmsg = msg % (sta_wifi_ip_info['ip_addr'], sta_ip_info_on_zd['mac'], sta_wifi_ip_info['mac_addr'])
            return
        logging.info('The station mac address [%s] is correct' % sta_wifi_ip_info['mac_addr'])

        # Verify if the lease time is correct
        leaseobtained_on_sta = time.mktime(time.strptime(sta_wifi_ip_info['lease_obtained'], sta_leasetime_format))
        leasetime_on_sta = time.mktime(time.strptime(sta_wifi_ip_info['lease_expires'], sta_leasetime_format))
        leasetime_in_secs = leasetime_on_sta - leaseobtained_on_sta
        zd_leasetime_in_secs = self.leasetime_option[zd_dhcp_ser_conf['leasetime']]

        if  abs(leasetime_in_secs - zd_leasetime_in_secs) > 10:
            msg = 'The lease time recorded on station is "%s" seconds instead of "%s" seconds'
            self.errmsg = msg % (str(leasetime_in_secs), str(zd_leasetime_in_secs))
            return
        logging.info('The lease time [%s] is correct' % sta_wifi_ip_info['lease_expires'])

    def _initTestParameters(self, conf):
        """
        """
        self.conf = conf
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']

        self.linux_server = None
        self.target_station = None
        self.ntp_conf_bkup = None
        self.ip_info_backup = None
        self.zd_dhcp_srv_cfg = None

        self.valid_ip_conf = {'ip_addr':'192.168.0.2', 'net_mask':'255.255.255.0',
                              'gateway':'192.168.0.253', 'pri_dns':'', 'sec_dns':''}
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '',
                         'ad_domain': '', 'ad_port': '', 'key_string': '',
                         'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': ''}
        self.wlan_cfg['ssid'] = 'DHCP Server testing - %s' % time.strftime("%H%M%S")

        if conf.has_key('dhcpser_conf'):
            self.testing_dhcpser_conf = conf['dhcpser_conf']
        else:
            self.testing_dhcpser_conf = {'start_ip':'192.168.0.9', 'number_ip':99, 'enable': True}

        self.valid_ip_range_in_same_subnet = [1, 32, 64, 128, 192, 240]
        self.valid_ip_range_in_diff_subnet = [1, 32, 64, 128, 192, 256, 320, 512]

        self.invalid_starting_ip_list = [' ', 'a.b.c.d', '1.1.1.d', '   192.168.0.9', '192.168..9',
                                         '192.168.0.257', '172.16.15.1']
        self.invalid_ip_range_in_same_subnet = ['0', '256', '513']
        self.invalid_ip_range_in_diff_subnet = ['0', '513']

        self.test_option = conf['test_option']
        self.check_status_timeout = 420
        self.leasetime_option = {'Six hours':21600, 'Twelve hours':43200, 'One day':86400, 'Two days':172800,
                                 'One week':604800, 'Two weeks':1209600}

        self._checkAPsMode()

    def _cfgTimeOnLinuxServer(self, time):
        try:
            self.linux_server.set_date_time(time)
            time_config = self.linux_server.get_system_time()
            logging.info('Setting the date time on Linux server to %s successfully' % time_config)
        except Exception, e:
            raise Exception('Setting Server Datetime Error: %s' % e)

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
#        cls.remove_all_cfg(self.zd, self.zdcli)   

    def _cfgTargetStation(self):
        if not self.conf.has_key('target_station'):
            return
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.check_status_timeout
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _syncZDTimeWithNTPSrv(self):
        self.ntp_conf_bkup = self.zd.get_ntp_cfg()
        self.zd.cfg_ntp(self.linux_server.ip_addr)
        logging.info('Configure the  NTP server info on ZD to %s successfully' % self.linux_server.ip_addr)
        logging.info('Synchronize date time on the ZoneDirector: %s' % self.zd.get_current_time())

    def _restartAllAPs(self):
        # Restart all APs in system.
        self.zd.restart_aps()
        start_time = time.time()
        time_out = time.time() - start_time
        all_connected = True
        time.sleep(120)

        while time_out < self.check_status_timeout:
            time_out = time.time() - start_time
            #self.zd.do_login()
            all_aps_info = self.zd.get_all_ap_info()
            for ap_info in all_aps_info:
                if ap_info['status'].lower() != 'connected':
                    all_connected = False
                    time.sleep(30)
                    break
                all_connected = True

            if all_connected:
                break

        if not all_connected:
            raise Exception('Not all aps connected to ZD system after %s seconds' % repr(self.check_status_timeout))

        for ap_obj in self.testbed.components["AP"]:
            ap_obj.verify_component()

    def _checkAPsMode(self):
        # Logging the alarm if there is any L3 AP in the testbed
        l3_ap_list = []
        for ap in self.testbed.components['AP']:
            apmgrinfo = ap.get_ap_mgr_info()
            conn_mode_in_ap = apmgrinfo['Tunnel/Sec Mode'].split("/")[0].strip().lower()
            if conn_mode_in_ap == 'l3':
                l3_ap_list.append(ap.ip_addr)
        if l3_ap_list:
            msg = 'This test may be broken! There is/are %d AP(s) [%s] that connecting to Zone Director under L3 mode.'
            msg = msg % (len(l3_ap_list), repr(l3_ap_list))
            logging.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            logging.info(msg)
            logging.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

