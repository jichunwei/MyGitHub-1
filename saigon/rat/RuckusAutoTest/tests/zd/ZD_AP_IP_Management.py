# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is use for 4 testcases in AP IP management testsuite of Odessa test plan:
                        - Dynamic AP IP assigned
                        - Manual AP IP assigned through L2LWAPP
                        - Manual AP IP assigned through L3LWAPP
                        - Invalid IP/Subnet/Gateway address

Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector', 'NetgearL3Switch'
   Test parameters: 'test_option': the expect testing process.
                                Ex: 'dynamic': verify AP use 'dhcp' option
                                    'l2_manual': verify manual AP IP assigned through L2LWAPP
                                    'l3_manual': verify manual AP IP assigned through L3LWAPP
                                    'invalid_ip': verify invalid IP/Subnet/Gateway address couldn't be save
                    'active_ap': The expected AP mac address
   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Base on test option, we will configure the active ap:
            + 'dynamic':
                - Connect AP to ZD with static AP
            + 'l2_manual':
                - Set AP use 'Keep AP's Setting' option
            + 'l3_manual':
                - Connect AP to ZD through the L3LWAPP

   2. Test:
       - Base on test option, we will test:
            + Set 'By - DHCP' field of Active AP to appropriate option.
            + Set the test ip value
            + Verify:
                + 'Dynamic': AP should reboot and get an IP address from external DHCP server
                + 'Manual': AP should reboot and reconnect to ZD with the setting IP address
                + 'Invalid IP': Invalid IP value could not be saved
   3. Cleanup:
       - Return the original AP configuration

   How it is tested?

"""
import time
import logging

from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_AP_IP_Management(Test):
    required_components = ['RuckusAP', 'ZoneDirector', 'NetgearL3Switch']
    parameter_description = {'test_option': 'the expect testing process.',
                           'active_ap': 'The expected AP mac address'}

    def config(self, conf):
        # Define test parameters
        self._cfg_init_test_params(conf)
        # Configure the active AP for test
        self._cfg_active_ap()


    def test(self):
        # Test for dynamic ap assigned case
        if self.test_option == 'dynamic':
            self._verify_dynamic_ap_ip_assigned()

        # Test for manual ap assigned through l2lwapp case
        elif self.test_option == 'l2_manual':
            self._verify_manual_ap_ip_assigned('l2')

        # Test for manual ap assigned through l3lwapp case
        elif self.test_option == 'l3_manual':
            self._verify_manual_ap_ip_assigned('l3')

        # Test for invalid ip/net_mask/gateway address
        elif self.test_option == 'invalid_ip':
            self._verify_ap_ip_setting()

        else:
            raise Exception('Invalid test option [%s]!' % self.test_option)

        if self.errmsg:
            logging.debug(self.errmsg)
            return ('FAIL', self.errmsg)

        else:
            return ('PASS', '')


    def cleanup(self):
        # Restore AP to original configuration
        if self.active_ap:
            logging.info('Configure the AP to use DHCP')
            lib.zd.ap.set_ap_ip_config_by_mac_addr(
                self.zd, self.active_ap_mac, "dhcp"
            )
            self.zd.remove_approval_ap(self.active_ap_mac)
            
            #@author: anzuo, @change: change SW port vlan to default 301
            if self.testbed.mac_to_vlan[self.active_ap_mac] != '301':
                logging.info("change AP SW port config back to 301")
                sw = self.testbed.components["L3Switch"]
                sw.remove_interface_from_vlan(self.testbed.mac_to_port[self.active_ap_mac],self.testbed.mac_to_vlan[self.active_ap_mac])
                sw.add_interface_to_vlan(self.testbed.mac_to_port[self.active_ap_mac],'301')
            
            logging.info("wait 120 seconds")
            time.sleep(120)
            self._verify_active_ap_connection()
            if self.errmsg:
                raise Exception(self.errmsg)

            if self.test_mode and self.test_mode != self.active_ap_conn_mode.lower():
                logging.info('Restore the AP connection mode to %s' %
                             self.active_ap_conn_mode)
                self.testbed.configure_ap_connection_mode(
                    self.active_ap_mac, self.active_ap_conn_mode
                )
                logging.info("wait 120 seconds")
                time.sleep(120)
                self._verify_active_ap_connection()
                if self.errmsg:
                    raise Exception(self.errmsg)


    def _cfg_init_test_params(self, conf):
        self.conf = conf
        self.errmsg = ''
        self.test_option = conf['test_option']
        self.test_mode = None
        self.linux_server = None
        self.active_ap = None

        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = tconfig.get_testbed_active_ap(
            self.testbed, self.conf['active_ap']
        )
        self.active_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(
            self.conf['active_ap']
        )
        self.active_ap_ip_conf = lib.zd.ap.get_ap_ip_config_by_mac(
            self.zd, self.active_ap_mac
        )

        self.active_ap_conn_mode = lib.zd.aps.get_ap_detail_info_by_mac_addr(
            self.zd, self.active_ap_mac
        )['tunnel_mode']

        self.check_status_timeout = 180
        self.invalid_ip_list = [
            ' ', 'a.b.c.d', '1.1.1.d',
            '192.168.0. 9', '192.168..9', #@author: Jane.Guo @since: 2013-09 behavior change
            '192.168.0.0', '255.255.255.0', '192.168.0.255',
            '192.168.0.256', '300.300.300.300', '0.0.0.0'
        ]
        self.invalid_net_mask_list = [
            ' ', 'a.b.c.d', '255.255.a.0', '25 5.255.255.0',
            '300.300.300.300', '192.168.255.0'
        ]

    def _cfg_active_ap(self):
        if self.test_option == 'dynamic' or self.test_option == 'keep_ap_setting':
            if self.active_ap_ip_conf['ip_mode'] != 'manual':
                logging.info('Connect Active AP to ZD with static IP')
                lib.zd.ap.set_ap_ip_config_by_mac_addr(
                    self.zd, self.active_ap_mac, "manual", {}
                )
                self._verify_active_ap_connection()

                if self.errmsg:
                    raise Exception(self.errmsg)


        if 'manual' in self.test_option:
            self.test_mode = self.test_option.split('_')[0].lower()
            if self.active_ap_conn_mode.lower() != self.test_mode:
                logging.info('Connect Active AP with ZD through %sLWAPP' %
                             self.test_mode.upper())
                self.testbed.configure_ap_connection_mode(
                    self.active_ap_mac, self.test_mode
                )
                logging.info("wait 120 seconds")
                time.sleep(120)
                self._verify_active_ap_connection()

                if self.errmsg:
                    raise Exception(self.errmsg)


            if self.active_ap_ip_conf['ip_mode'] == 'manual':
                logging.info('Set "By-DHCP" option of AP [%s] to "Keep AP\'s Setting"' %
                             self.active_ap_mac)
                lib.zd.ap.set_ap_ip_config_by_mac_addr(
                    self.zd, self.active_ap_mac, "as_is"
                )


    def _verify_dynamic_ap_ip_assigned(self):
        self.linux_server = self.testbed.components['LinuxServer']
        self.linux_server.delete_dhcp_leases()
        logging.info('Configure Active AP [%s] to use dynamic IP' %
                     self.active_ap_mac)

        lib.zd.ap.set_ap_ip_config_by_mac_addr(
            self.zd, self.active_ap_mac, "dhcp"
        )
        time.sleep(10)
        self._verify_is_active_ap_reboot()

        if self.errmsg:
            return

        time.sleep(5)
        ap_ip_info = self.active_ap.get_ip_info('wan')
        dhcp_leases = self.linux_server.get_dhcp_leases()

        if 'dynamic' not in ap_ip_info['type'].lower():
            self.errmsg = 'AP connection type is "%s" instead of "dynamic"' % ap_ip_info['type']
            return

        if ap_ip_info['ip_addr'] not in repr(dhcp_leases):
            self.errmsg = 'AP IP[%s] information is not recorded on the external DHCP server' % ap_ip_info['ip_addr']
            return

        self.errmsg = ''


    def _verify_manual_ap_ip_assigned(self, mode):
        ip_oct = self.active_ap.get_ip_info('wan')['ip_addr'].split('.')
        ip_oct[3] = '99'
        test_ip = '.'.join(ip_oct)

        # Select 'Manual' option and setting the test IP
        logging.info('Configure Active AP [%s] to use static IP [%s]' %
                     (self.active_ap_mac, test_ip))

        lib.zd.ap.set_ap_ip_config_by_mac_addr(
            self.zd, self.active_ap_mac, "manual", {'ip_addr': test_ip}
        )

        time.sleep(5)
        #@author: lipingping; @bug: ZF-8475; @since: 2014.6.13
        self._verify_is_active_ap_reboot(test_ip = test_ip)
        if self.errmsg:
            return

        # Verify the IP information of the active AP
        start_time = time.time()
        while True:
            ap_info_on_zd = self.zd.get_ap_info_ex(self.active_ap_mac)

            if ap_info_on_zd['info']['status'].lower() == 'connected': break
            if time.time() - start_time > 60:
                raise Exception('The AP lost connection the ZD longer than 60s')


        ap_ip_info = self.active_ap.get_ip_info('wan')

        if 'static' not in ap_ip_info['type'].lower():
            self.errmsg = 'AP connection type is "%s" instead of "static"' % ap_ip_info['type']
            return

        if ap_ip_info['ip_addr'] != test_ip:
            self.errmsg = 'The AP IP is "%s" instead of "%s"' % (ap_ip_info['ip_addr'], test_ip)
            return

        if mode in ap_info_on_zd['info']['tunnel_mode'].lower():
            self.errmsg = self.testbed.verify_ap_connection_mode(self.active_ap_mac)

        else:
            msg = 'The tunnel mode of AP on ZD\'s WebUI is "%s" instead of "%s"'
            self.errmsg = msg % (ap_info_on_zd['info']['tunnel_mode'], mode)


    def _verify_ap_ip_setting(self):
        # Verify all invalid IP couldn't be saved
        for ip in self.invalid_ip_list:
            try:
                lib.zd.ap.set_ap_ip_config_by_mac_addr(
                    self.zd, self.active_ap_mac, "manual", {'ip_addr': ip}
                )
                self.errmsg = 'Invalid IP [%s] is set successfully!' % ip
                break

            except Exception, e:
                msg = 'Setting Failed! [Correct behavior]: [%s]' % e
                self.errmsg = ''
                logging.info(msg)


        # Verify all invalid net_mask couldn't be saved
        for net_mask in self.invalid_net_mask_list:
            try:
                lib.zd.ap.set_ap_ip_config_by_mac_addr(
                    self.zd, self.active_ap_mac, "manual", {'net_mask': net_mask}
                )
                self.errmsg = 'Invalid net_mask [%s] is set successfully!' % net_mask
                break

            except Exception, e:
                msg = 'Setting Failed! [Correct behavior]: [%s]' % e
                self.errmsg = ''
                logging.info(msg)


        # Verify all invalid gateway couldn't be saved
        for gateway in self.invalid_ip_list:
            try:
                lib.zd.ap.set_ap_ip_config_by_mac_addr(
                    self.zd, self.active_ap_mac, "manual", {'gateway': gateway}
                )
                self.errmsg = 'Invalid IP [%s] is set successfully!' % ip
                break

            except Exception, e:
                msg = 'Setting Failed! [Correct behavior]: [%s]' % e
                self.errmsg = ''
                logging.info(msg)


    def _verify_active_ap_connection(self):
        start_time = time.time()
        time_out = time.time() - start_time
        connected = True

        while time_out < self.check_status_timeout:
            time_out = time.time() - start_time

            ap_info = self.zd.get_all_ap_info(self.active_ap_mac)
            if ap_info:
                if ap_info['status'].lower() != 'connected':
                    connected = False
                    time.sleep(10)

                else:
                    connected = True
                    self.active_ap.ip_addr = ap_info['ip_addr']
                    self.active_ap.verify_component()
                    logging.info('Ruckus AP[%s] is connected to Zone Director with IP [%s]'
                                 % (self.active_ap_mac, ap_info['ip_addr']))
                    self.errmsg = ''
                    break

            else:
                connected = False
                time.sleep(10)


        if not connected:
            msg = 'AP [%s] does not connect to ZD system after %s seconds'
            self.errmsg = msg % (self.active_ap_mac, repr(self.check_status_timeout))


    def _verify_is_active_ap_reboot(self, reboot_timeout = 60, test_ip = None): #@author: lipingping;@bug: ZF-8475;@since: 2014.6.13
        start_time = time.time()
        time_out = time.time() - start_time
        rebooted = True
        
        if test_ip:
            logging.info("change active AP ip from %s to %s" % (self.active_ap.ip_addr, test_ip))
            self.active_ap.ip_addr = test_ip

        while time_out < reboot_timeout:
            time_out = time.time() - start_time
            try:
                current_uptime = self.active_ap.get_up_time()
                if current_uptime['days'] is None and \
                 current_uptime['hrs'] is None :
                    run_time = 0
                    if current_uptime['mins']:
                        run_time = int(current_uptime['mins']) * 60

                    run_time = run_time + int(current_uptime['secs'])
                    if run_time < reboot_timeout + 15 :
                        rebooted = True
                        break

                else :
                    rebooted = False

                time.sleep(3)

            except Exception, e:
                rebooted = True
#                logging.info('exception info: %s' % e.message)
                if e.message.__contains__('haven\'t matched the uptime info'):
                    raise e
                logging.info('Active AP is rebooting')
                time.sleep(10)
                break


        if not rebooted:
            msg = 'AP [%s] does not reboot after %s seconds'
            self.errmsg = msg % (self.active_ap.baseMacAddr, repr(reboot_timeout))

        else:
            # Wait until AP reboot successfully
            start_time = time.time()
            time_out = time.time() - start_time
            flag = True
            while time_out < self.check_status_timeout:
                time_out = time.time() - start_time
                ap_info = self.zd.get_all_ap_info(self.active_ap_mac)
                if ap_info['status'].lower() == 'connected':
                    try:
                        #@author: lipingping, @bug: ZF-8475; @since: 2014.6.13
                        if test_ip:
                            if test_ip != ap_info['ip_addr']:
                                continue
                        self.active_ap.ip_addr = ap_info['ip_addr']
                        self.active_ap.verify_component()
                        flag = True
                        break

                    except:
                        flag = False
                        time.sleep(10)

            if not flag:
                msg = 'AP [%s] does not reconnect to ZD affter %s seconds'
                self.errmsg = msg % (self.active_ap_mac, self.check_status_timeout)

            else:
                self.errmsg = ''
                logging.info('AP [%s] rebooted and reconnected to ZD successfully' %
                             self.active_ap_mac)

