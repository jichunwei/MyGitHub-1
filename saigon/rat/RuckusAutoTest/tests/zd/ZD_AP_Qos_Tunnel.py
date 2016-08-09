# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

'''
Description: Verify the downlink traffic go to the right media queue

Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
   'active_ap' : Mac address of the active AP
   'target_sta' : target station IP address
   'tos' : ToS of the packets that will be sent
   'num_of_pkts' : Number of packet will be sent out
   'expect_queue' : The appropriate media queue with the ToS classify on AP

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If the packet go to the wrong queue
   PASS:
   - All packet go to the right queue

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Create the associate between the ZD system with the target station via active AP
         2. Test procedure:
            - Send out traffic downlink with ToS
            - On AP check the traffic go to right queue or not.
         3. Cleanup:
            - Remove all configuration
            - Note: When cleanup test environment the active AP might be reboot by bug 1915, so we
            will reboot AP affter finish testing to make sure the next script will not be hang.
    How it was tested:
'''

import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import configure_ip
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zd import system_zd as sys
from RuckusAutoTest.common.Ratutils import ping
#@ZJ 20150205 ZF-11987
import copy
import random
from RuckusAutoTest.components.lib.zdcli import configure_ap

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_AP_Qos_Tunnel(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station': 'ip address of target station',
                           'active_ap': 'mac address (NN:NN:NN:NN:NN:NN) of target ap which client will associate to',
                           'wlan_list': 'list of dictionary of encryption parameters'}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        #@ZJ 20150205 ZF-11987
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.old_vlan_id = None
        if conf.has_key('timeout'):
            self.timeout = conf['timeout']
        else:
            self.timeout = 180

        if conf.has_key('expect_result'):
            self.expect_result = conf['expect_result']
        else:
            self.expect_result = 95

        self.ap_cfg = None
        self.ap = None
        self.mac_addr = None
        self.target_station = None
        self.expect_queue = conf['expect_queue']
        self.expect_column = 'enq'
        self.num_of_pkts = conf['num_of_pkts']
        self.tos = conf['tos'].lower()
        self.run_time = conf['run_time'] if conf.get('run_time') else 30
        self.server = None

        # Starting the zing server
        # re-use components['LinuxServer'] instead of creating a new one
        self.server = self.testbed.components['LinuxServer']
        self.server.re_init()
        self.host = self.server.ip_addr
        self.filter_value = conf['filter_value'] if 'filter_value' in conf else ''
        self.add_rules = conf['add_rules'] if 'add_rules' in conf else ''
        self.expect_queue = conf['expect_queue'] if 'expect_queue' in conf else ''
        self.layer = conf['layer'] if 'layer' in conf else ''
        self.protocol = conf['protocol'] if 'protocol' in conf else ''
        self.set_mgmt = conf['set_mgmt'] if 'set_mgmt' in conf else ''

        logging.info('Telnet to the server at IP address %s successfully' %
                     self.server.ip_addr)
        self.server.kill_zing()
        if 'filter_value' in conf:
            self.server.start_zing_server(tos = self.tos
                                ,port = conf['filter_value'] if self.layer == '4' else ''
                                ,udp = self.protocol if self.protocol == 'udp' else ''
                                ,tcp = self.protocol if self.protocol == 'tcp' else ''
                                )
        else:
            self.server.start_zing_server(tos = self.tos)

        self.test_wlan = dict(ssid = 'qos_test', auth = 'open', wpa_ver = '', encryption = 'none',
                   sta_auth = 'open', sta_wpa_ver = '', sta_encryption = 'none',
                   key_index = '' , key_string = '', username = '', password = '',
                   ras_addr = '', ras_port = '', ras_secret = '', use_radius = False,
                   do_tunnel = conf['do_tunnel'] if 'do_tunnel' in conf else False,
                   vlan_id = conf['vlan_id'] if 'vlan_id' in conf else '',
                   dvlan = conf['dvlan'] if 'dvlan' in conf else False,
                   )

        self.zd.remove_all_wlan()
        time.sleep(5)

        self.zd.cfg_wlan(self.test_wlan)
        logging.info('Create wlan \'%s\' for associate successfully' % self.test_wlan['ssid'])

        self._cfgActiveAP(conf)

        self._cfgTargetStation(conf)

        #@author: Jane.Guo @since: 2013-08-15 fix bug ZF-4218, adapt to different version
        #@zj ZF-9668 : expect_queue_exc is expect_queue has been exchange by map_media_queue_info
        self.expect_queue_exc = lib.apcli.radiogrp.map_media_queue_info(self.ap,self.expect_queue)
#        self.expect_queue = lib.apcli.radiogrp.map_media_queue_info(self.ap,self.expect_queue)

    def test(self):
        # Check if we could ping from target station to server.
        if self.target_station.get_current_status() != 'connected':
            return 'FAIL', 'There no association between target station and ZD system'

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.target_station.renew_wifi_ip_address()

        logging.info('Get IP and MAC addresses of the wireless adapter on the target station %s' %
                     self.target_station.get_ip_addr())

        result, msg = None, None
        if self.add_rules:
            for rule_item in self.add_rules:
                if self.filter_value:
                    self.ap.add_port_matching_rule(self.wlan_name,
                            self.protocol,#@zj_20140814 ZF-9669 if 'protocol' in rule_item else None,
                            rule_item['action'], self.filter_value,
                            rule_item['dest_port'], self.expect_queue,
                            self.layer)
                    result, msg = self._traffic('PASS' \
                                       if rule_item['action'] != 'drop' else 'FAIL')
                    #@author: chen.tao 2014-01-08 to fix ZF-6494
                    ####delete rule after test#################################
                    #@zj 20140814 fix ZF-9669

                    layer_map = {'2':'mac','3':'ip','4':'port'}
                    filter_value = ''
                    if self.layer == '3':
                        filter_value = self.filter_value + r'/255.255.255.255'  
                    else: filter_value = self.filter_value
                    logging.info('Deleting rule after test')
                    cmd_dest_port = ''
                    if rule_item['dest_port']:
                        cmd_dest_port = 'dest'
                    else :
                        cmd_dest_port = 'src'
                    cmd = "set qos %s %s delete ucast %s %s %s"%(self.wlan_name,layer_map[self.layer],self.protocol,cmd_dest_port,filter_value)
                    res = self.ap.cmd(cmd)[-1]
                    if (res != "OK"):
                        logging.info(res)
                        raise Exception("Deleting rule failed.")
                    ####delete rule after test#################################
                    #@author: chen.tao 2014-01-08 to fix ZF-6494
                    if 'FAIL' in result:
                        return (result, msg)
                    #@zj201400912 ZF-9927 optimization
 
                '''   self.old_zd_ip_cfg :   
                 {'gateway': u'192.168.128.253',
                  'ip_addr': u'192.168.128.2',
                  'ip_alloc': 'manual',
                  'netmask': u'255.255.255.0',
                  'pri_dns': u'192.168.0.252',
                  'sec_dns': u'',
                  'vlan': u'328'}
                    '''
        else:
            if self.set_mgmt:
                if self.set_mgmt.has_key('vlan_id'):
                    self.old_zd_ip_cfg = sys.get_device_ip_settings(self.zd, const.IPV4)
                    self.old_vlan_id = self.old_zd_ip_cfg['vlan']
                    self.old_ip_addr = self.old_zd_ip_cfg['ip_addr']
                    ipconfig = {'type':'dhcp', 'access_vlan':self.set_mgmt['vlan_id']}
                    configure_ip.set_zd_ip_setting(self.zd, ipconfig)                    
                    #zj 20140208 fix  ZF-7167 
                    self.zd.ip_addr = "20.0.2.2"
                    self._wait_zd_restart_after_set_ip(self.zd,self.old_ip_addr)
                    self.zd.url = "https://20.0.2.2"                    
                    self.zd.s.open(self.zd.url)
                    self.zd.login()  
#                lib.zd.mvlan.set_zd_mgmt_vlan_info(self.zd, self.set_mgmt)
                    ##@anzuo 201402 fix ZF-7167
                    #wait all ap connect to zd
                    count = 0
                    while True:
                        all_connect = True
                        if count >= 3:
                            raise Exception("not all ap connect to zd")
                        
                        ap_info = self.zd.get_all_ap_info()
                        for ap in ap_info:
                            if not ap['status'].lower().startswith("connected"):
                                time.sleep(10)
                                count = count + 1
                                all_connect = False
                                break
                        if all_connect:
                            break
                    ##@anzuo 201402 fix ZF-7167
            
            result, msg = self._traffic('PASS')

        return (result, msg)


    def _traffic(self, expect_test):
        # Send downlink traffic (use Zing)
        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != '0.0.0.0':
                break

            time.sleep(1)

        logging.debug('Wifi IP: %s ---- Wifi MAC: %s' % (sta_wifi_ip_addr, sta_wifi_mac_addr))
        if not sta_wifi_mac_addr:
            raise Exception('Unable to get MAC address of the wireless adapter of the target station %s' %
                            self.target_station.get_ip_addr())

        elif not sta_wifi_ip_addr:
            raise Exception('Unable to get IP address of the wireless adapter of the target station %s' %
                            self.target_station.get_ip_addr())

        elif sta_wifi_ip_addr == '0.0.0.0' or sta_wifi_ip_addr.startswith('169.254'):
            raise Exception('The target station %s could not get IP address from DHCP server' %
                            self.target_station.get_ip_addr())

        logging.info("Verify information of the target station shown on the Zone Director")
        timed_out = False
        start_time = time.time()
        while True:
            all_good = True
            client_info_on_zd = None
            for client_info in self.zd.get_active_client_list():
                logging.debug("Found info of a station: %s" % client_info)
                if client_info['mac'].upper() == sta_wifi_mac_addr.upper():
                    client_info_on_zd = client_info
                    if client_info['status'] != 'Authorized':
                        if timed_out:
                            msg = "The station status shown on ZD was %s instead of 'Authorized'" % \
                                  client_info['status']
                            return ("FAIL", msg)

                        all_good = False
                        break

                    if client_info['ip'] != sta_wifi_ip_addr:
                        if timed_out:
                            msg = "The station wifi IP address shown on ZD was %s instead of %s" % \
                                  (client_info['ip'], sta_wifi_ip_addr)
                            return ("FAIL", msg)

                        all_good = False
                        break

            # End of for
            # Quit the loop if everything is good
            if client_info_on_zd and all_good: break
            # Otherwise, sleep
            time.sleep(1)
            timed_out = time.time() - start_time > self.timeout
            # And report error if the info is not available
            if not client_info_on_zd and timed_out:
                msg = "Zone Director didn't show any info about the target station while it had been associated"
                return ("FAIL", msg)

            # Or give it another try
        # End of while

        logging.info('Verify information of the target station shown on the AP %s' % self.ap.get_base_mac())
        start_time = time.time()
        station_list_on_ap = None
        while time.time() - start_time < self.timeout:
            station_list_on_ap = self.ap.get_station_list(self.wlan_name)
            if station_list_on_ap: break
            time.sleep(1)

        if not station_list_on_ap:
            return ('FAIL', 'AP %s didn\'t have any info about the stations' % self.ap.get_base_mac())

        found = False
        for sta_info in station_list_on_ap:
            if sta_info[0].upper() == sta_wifi_mac_addr.upper():
                if sta_info[1] == 0:
                    return ('FAIL', 'Target station\'s AID status is zero on the AP %s' % self.ap.get_base_mac())

                if sta_info[2] != client_info_on_zd['channel'] and sta_info[3] != client_info_on_zd['channel']:
                    return ('FAIL', 'Target station\'s channel info on AP (%s) is not %s as shown on ZD' %
                            (sta_info[2], client_info_on_zd['channel']))

                found = True
                break

        if not found:
            return ('FAIL', 'Not found station %s on the AP %s' % (sta_wifi_mac_addr, self.ap.get_base_mac()))


        self.ap.clear_mqstats(self.wlan_name)
        logging.info('Clear the mqstats on interface %s of the active AP successfully' % self.wlan_name)
        logging.debug('MQSTATS Info: %s' % self.ap.get_media_queue_stats(self.wlan_name))

        logging.debug('Target station IP: %s' % self.target_station)

        traffic_result = self.target_station.send_zing(host = self.host, num_of_pkts = self.num_of_pkts,
                                                      tos = self.tos, sending_time = self.run_time)
        media_queue_info = self.ap.get_media_queue_stats(self.wlan_name)
        logging.info('Sent traffic from target station successfully')
        logging.info('media_queue_info   %s' % media_queue_info)

        total_pkts_send_out = int(traffic_result['Batches']) * int(traffic_result['Batch Size'])
        logging.info('%s packets with %s tos bit set are send out' % (total_pkts_send_out, self.tos))


        logging.debug('MQSTATS Info: %s' % media_queue_info)
        #@zj 20140814 ZF-9668
        num_of_pkts_go_to_media_queue = media_queue_info['%s_%s_%s' % (sta_wifi_mac_addr.lower(), self.expect_queue_exc, self.expect_column)]
        pass_percent = float(int(num_of_pkts_go_to_media_queue) * 100) / float(total_pkts_send_out)
        logging.info('Number of packets go to the %s queue is %d'
                     % (self.expect_queue_exc.upper(), int(num_of_pkts_go_to_media_queue)))

        if ((pass_percent < self.expect_result) and (expect_test == 'PASS')) \
            or ((pass_percent >= self.expect_result) and (expect_test == 'FAIL')):
            msg = '[%s TOS Classification] There are %d [%0.2f %%] packets go to the %s queue'
            msg = msg % (self.expect_queue_exc.upper(), int(num_of_pkts_go_to_media_queue),
                         pass_percent, self.expect_queue_exc.upper())
            logging.info(msg)
            return ('FAIL', msg)

        else:
            msg = '[%s TOS Classification] There are %d [%0.2f %%] packets go to the %s queue'
            msg = msg % (self.expect_queue_exc.upper(), int(num_of_pkts_go_to_media_queue),
                         pass_percent, self.expect_queue_exc.upper())
            logging.info(msg)
            return ('PASS', msg)
        #@zj 20140814 ZF-9668

    def cleanup(self):
        logging.info('Clean up environment')
        if self.server:
            self.server.close()

        if self.target_station:
            self.target_station.remove_all_wlan()
            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            current_time = start_time
            while current_time - start_time <= self.timeout:
                res = self.target_station.get_current_status()
                if res == "disconnected":
                    break

                time.sleep(5)
                current_time = time.time()

            if current_time - start_time > self.timeout:
                raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                self.timeout)

        logging.info("Remove all the WLANs on the Zone Director")
        self.zd.remove_all_wlan()
        if self.mac_addr:
            self.zd.remove_approval_ap(self.mac_addr)

        # Reboot the active AP after remove all wlan. ( Working around to avoid bug 1915)
        if self.ap:
            self.ap.reboot()
            while True:
                try:
                    for ap_comp in self.testbed.components['AP']:
                        ap_comp.login()
                        logging.debug('%s' % ap_comp.get_base_mac())
                    break

                except:
                    time.sleep(10)

        # Verify if the APs is still connected on ZD
        start_time = time.time()
        timeout = 150
        while True:
            connected = 0
            aps_info = self.zd.get_all_ap_info()
            for ap in aps_info:
                if ap['status'].lower().startswith("connected"):
                    connected += 1

            if connected == len(self.testbed.components['AP']):
                break

            if time.time() - start_time > timeout:
                raise Exception("There are %d APs disconnecting from the ZD"
                                % (len(self.testbed.components['AP']) - connected))

            time.sleep(1)
            
        if self.old_vlan_id: 
        #zj 2014-0208 fix ZF-7167 
        #   ipconfig = {'type':'dhcp', 'access_vlan':self.old_vlan_id}
            ipconfig = {'type':self.old_zd_ip_cfg["ip_alloc"],'gateway':self.old_zd_ip_cfg["gateway"], 'access_vlan':self.old_vlan_id,"ip_addr":self.old_ip_addr}
            configure_ip.set_zd_ip_setting(self.zd, ipconfig)
            self.zd.ip_addr = self.old_ip_addr
        #ZF-7167 fix self._wait_zd_restart_after_set_ip(self.zd,self.old_ip_addr)   self.zd.url
            self._wait_zd_restart_after_set_ip(self.zd,"20.0.2.2")
            self.zd.url = "https://"+self.zd.ip_addr
            self.zd.s.open(self.zd.url)
            self.zd.login()
            
        #@ZJ  20150205 ZF-11987 restore the configure of wlan-service    
        radio_list = ['radio_ng','radio_na']
        for radio_x in radio_list:
            zdcli_ap_cfg = {'mac_addr': self.mac_addr, 
                            radio_x: {'wlan_service':'Yes',},}
            res, msg = configure_ap.configure_ap(self.zdcli, zdcli_ap_cfg)
            logging.info(msg)
        #
        if self.ap_cfg:
            lib.zd.ap.set_ap_config_by_mac(self.zd, self.mac_addr, **self.ap_cfg)
        

    def _wait_zd_restart_after_set_ip(self,zd,ip_before):
        logging.info('waitting zd restart')
        time_out = 1200
        start_time = time.time()
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(ip_before)
            if res.find("Timeout") != -1:
                break

            time.sleep(2)

        logging.info("The Zone Director is being restarted. Please wait...")
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(zd.ip_addr)
            if res.find("Timeout") == -1:
                time.sleep(2)
                break

            time.sleep(2)
        logging.info("The Zone Director restart successfully.")

    def _cfgActiveAP(self, conf):
        self.ap = tconfig.get_testbed_active_ap(self.testbed, conf['active_ap'], "Active AP")
        self.mac_addr = self.ap.get_base_mac().lower()
        self.ap_cfg = lib.zd.ap.get_ap_config_by_mac(self.zd, self.mac_addr)
        
        #@ZJ 20150205 ZF-11987 : active ap , just retain one radio, disable other wlan service on ZDCLI.
        if 'na' in self.ap_cfg['radio_config']:
            radio_list = ['radio_bg','radio_ng','radio_na']
            radio_x = random.choice(radio_list)
            zdcli_ap_cfg = {'mac_addr': self.mac_addr, 
                            radio_x: {'wlan_service':'No',},}
            res, msg = configure_ap.configure_ap(self.zdcli, zdcli_ap_cfg)
            logging.info(msg)
        #
        
        self.wlan_name = self.ap.ssid_to_wlan_if(self.test_wlan['ssid'])
        for ap in self.testbed.components['AP']:
            if ap.get_base_mac().lower() != self.mac_addr:
                ap.remove_all_wlan()
                logging.info('Turn off all WLAN interfaces on the non-active AP (%s)' % ap.ip_addr)

    def _cfgTargetStation(self, conf):
        # Find the target station object and remove all Wlan profiles
        for station in self.testbed.components['Station']:
            if station.get_ip_addr() == conf['target_station']:
                # Found the target station
                self.target_station = station
                break

        if not self.target_station:
            raise Exception('Target station %s not found' % conf['target_station'])

        self.target_station.cfg_wlan(self.test_wlan)
        basetime = time.time()
        while True:
            if self.target_station.get_current_status() == 'connected':
                break

            if time.time() - basetime > 180:
                raise Exception("The station didn't associate to the system")

            time.sleep(5)

        logging.info('The station associated to the system successfully')

