# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
ZD_Stations Testbed consists of the following components:

1) Zone Director
2) One or more remote stations

This testbed understands the following config parameters:
config['STA']: a sub-dictionary contains all the config for the station
config['ZD']: a sub-dictionary contains all the config for the Zone Director
"""
import logging
import time
import re
import os
import sys
import telnetlib
import ConfigParser
import cPickle as pi
from pprint import pformat
from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.components.NetgearL3Switch import NetgearL3Switch
from RuckusAutoTest.components.HuaweiL3Switch import HuaweiL3Switch
from contrib.download import multi_threads_downloader as di
from contrib.download import image_helper as ih

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_station_by_ip_addr,
    create_server_by_ip_addr,
    create_ruckus_ap_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd import (
    access_points_zd as AP,
    reset_factory_zd as RESET,
    aps as APS
)
from RatLogger import RatLogger

server_url_map = ih.BuildURLBuilder
#server_url_map = ih.server_url_map

class ZD_Stations(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo, config)
        self.testbed_info = testbedinfo

        #Jacky.Luh update by 2012-06-26
        #get the image share folder from 'rat_img.ini
        self.img_share_folder_name = 'rat_img.ini'
        if os.path.isfile(self.img_share_folder_name):
            self.get_img_share_folder_path_params()

        # Initialize the Linux server component
        if config.has_key('server') and config['server'] is not None:
            self.components['LinuxServer'] = create_server_by_ip_addr(
                ip_addr = config['server']['ip_addr'],
                username = config['server']['user'],
                password = config['server']['password'],
                root_password = config['server']['root_password'])

        else:
            self.components['LinuxServer'] = None
            logging.info("Testbed '%s' does not have LinuxServer configured." % \
                         testbedinfo.name)

        #Jacky.Luh updated by 2012-06-25
        #confirm the logic testbed enabled mesh or not.
        config['mesh_enabled'] = self.is_mesh_enabled_in_testbed()

        # Install AP symbolic dictionary
        if config.has_key('ap_sym_dict'):
            ap_sym_dict = config['ap_sym_dict']

        else:
            ap_sym_dict = None
        if config.has_key('ap_mac_list'):
            self.ap_mac_list = config['ap_mac_list']
        else:
            self.ap_mac_list = []
        self.init_aps_sym_dict(ap_sym_dict)

        # Initialize station components
        self.components['Station'] = []
        ip_list = self.config['sta_ip_list']
        for i in range(len(ip_list)):
            sta_dict = config['sta_conf'].copy()
            sta_dict['sta_ip_addr'] = ip_list[i]

            station = create_station_by_ip_addr(ip_addr = sta_dict.pop('sta_ip_addr'))
            self.components['Station'].append(station)

        # Initialize ZD CLI
        self.zd_ipaddr = config['ZD']['ip_addr']
        self.zd_username = config['ZD']['username']
        self.zd_password = config['ZD']['password']
        self.zd_shell_key = config['ZD']['shell_key']
        
        self.zd_cli = create_zd_cli_by_ip_addr(
            config['ZD']['ip_addr'],
            config['ZD']['username'],
            config['ZD']['password'],
            config['ZD']['shell_key']
        )
        self.components['ZoneDirectorCLI'] = self.zd_cli

        
        # Initialize the DUT component
        cnt = 3
        while cnt:
            try:
                # Initialize the DUT component
                self.zd = create_zd_by_ip_addr(
                    ip_addr = config['ZD']['ip_addr'],
                    username = config['ZD']['username'],
                    password = config['ZD']['password']
                )
                break;
            except Exception, e:
                cnt = cnt-1
                if cnt == 0:
                    raise e
                else:
                    logging.debug(e.message)

        self.zd.init_messages_bundled(self.zd_cli)
        self.components['ZoneDirector'] = self.zd
        self.dut = self.zd
        self.get_ap_object_dict(testbedinfo, config)
        self.set_route_vlan(testbedinfo, config)
        self.set_ap_conn_mode(testbedinfo, config)
        self.set_Mesh_layout(testbedinfo, config)
        #@author: Liang Aihua,@since: 2015-1-13,@change: zf-10762
        #let the mesh ap's switch port is still disable
        if config['mesh_enabled']:
            if os.path.isfile(self.mac_to_switch_port_record_file):
                logging.info("Disable all mesh aps's switch port, and let the mesh aps join in ZD")
                for mesh_ap_port in self.config['mesh_ap_mac_to_port']:
                    self.components['L3Switch'].disable_interface(mesh_ap_port['port'])
        self.set_radio_tx_power(testbedinfo, config)
            
        
    #Jacky.Luh update by 2012-06-26    
    def get_img_share_folder_path_params(self):
        #file option
        self.IMG_SETION  = 'img'
        self.ZD5K_Share_Folder_Path = 'ZD5000_img_share_folder_path'
        self.ZD3K_Share_Folder_Path = 'ZD3000_img_share_folder_path'
        self.ZD1100_Share_Folder_Path = 'ZD1100_img_share_folder_path'
        self.ZD1K_Share_Folder_Path = 'ZD1000_img_share_folder_path'
        
        #create the instance of share folder file
        self.img_share_folder_obj = ConfigParser.ConfigParser()
        self.img_share_folder_obj.read(self.img_share_folder_name)
        
        #get the params of image share folder path
        server_url_map.SAVE_REPOSITORY['ZD5000']['share_folder_path'] = \
        self.img_share_folder_obj.get(self.IMG_SETION, self.ZD5K_Share_Folder_Path)
        
        server_url_map.SAVE_REPOSITORY['ZD3000']['share_folder_path'] = \
        self.img_share_folder_obj.get(self.IMG_SETION, self.ZD3K_Share_Folder_Path)
        
        server_url_map.SAVE_REPOSITORY['ZD1100']['share_folder_path'] = \
        self.img_share_folder_obj.get(self.IMG_SETION, self.ZD1100_Share_Folder_Path)
        
        server_url_map.SAVE_REPOSITORY['ZD1000']['share_folder_path'] = \
        self.img_share_folder_obj.get(self.IMG_SETION, self.ZD1K_Share_Folder_Path)
        
        
    def get_ap_object_dict(self, testbedinfo, config):
        # Install AP symbolic dictionary
        if config.has_key('ap_sym_dict'):
            ap_sym_dict = config['ap_sym_dict']

        else:
            ap_sym_dict = None

        self.init_aps_sym_dict(ap_sym_dict)

        # Initialize AP components
        # This dictionary maps the MAC address of the AP to its corresponding IP address
        self.mac_to_ip = {}
        # This dictionary holds the references to the AP objects using their MAC address as key
        self.mac_to_ap = {}
        # This dictionary holds the list of MAC addresses of the APs of models using model name as key
        self.model_to_mac_list = {}

        ap_conf = {'username': self.zd.username,
                   'password': self.zd.password}

        logging.info('Get the list of the current connected APs on the ZD')
        tm0 = time.time()
        all_aps_info = self.zd.get_all_ap_info()

        tm1 = time.time()
        self.aps_info_list = [time.asctime(time.localtime(tm0)), tm0, int(tm1 - tm0),
                              all_aps_info]

        self.components['AP'] = []
        for ap_info in all_aps_info:
            for ap_mac in self.get_aps_mac_list(config['ap_mac_list']):
                if ap_info['mac'].lower() == ap_mac.lower():
                    ap_conf['ip_addr'] = ap_info['ip_addr']

                    log_path = RatLogger.log_conf['runlog_dir']
                    log_file = RatLogger.get_logfile("log_" + testbedinfo.name + "_" + \
                                                     ap_mac.replace(':', '_') + "_" + \
                                                     RatLogger.get_logger_timestr())
                    log_file = os.path.join(log_path, log_file)
                    ap_conf['log_file'] = file(log_file, 'w')

                    ap = create_ruckus_ap_by_ip_addr(ip_addr = ap_conf['ip_addr'],
                                                     username = ap_conf['username'],
                                                     password = ap_conf['password'])
                    self.components['AP'].append(ap)

                    # Fill in the MAC to ap mapping table
                    self.mac_to_ap[ap_mac.lower()] = ap

                    # Fill in the model to MAC list mapping table
                    model = ap.get_device_type().lower()
                    if self.model_to_mac_list.has_key(model):
                        self.model_to_mac_list[model].append(ap_mac.lower())

                    else:
                        self.model_to_mac_list[model] = [ap_mac.lower()]

    #Jacky.Luh update by 2012-06-26
    def set_route_vlan(self, testbedinfo, config):
        # Initialize L3 switch component if its configuration is given
        # And also build the tables to map MAC address to Interface on the switch
        # and to map MAC address to VLAN on the switch
        #Jacky.Lu updated by 07-04-2012
        self.mac_to_switch_port_record_file = 'rat_mac_port_rec.ini'
        
        if config.has_key('RoutingVLANs') and config['RoutingVLANs']:
            self.zd_vlan = str(config['RoutingVLANs'][0])
            self.remote_vlan = str(config['RoutingVLANs'][1])

        else:
            self.zd_vlan = "301"
            self.remote_vlan = ""

        self.mac_to_port = {}
        self.mac_to_vlan = {}
        self.config['ap_mac_to_port'] = {}
        
        if config.has_key('L3Switch') and config['L3Switch']:
            #detect the device branch to support huawei switch
            #An Nguyen, an.nguyen@ruckuswireless.com @since: May 2012            
            telnet_to_device = telnetlib.Telnet(config['L3Switch']['ip_addr'])
            ix, mobj, rx = telnet_to_device.expect(['<Quidway>', 'FSM.*'])
            if not ix:
                self.components['L3Switch'] = HuaweiL3Switch(config['L3Switch'])
            else: 
                self.components['L3Switch'] = NetgearL3Switch(config['L3Switch'])
                
            l3switch = self.components['L3Switch']
                
            if not os.path.isfile(self.mac_to_switch_port_record_file) and \
               self.config['mesh_enabled']:
                logging.info("Enable all aps's switch port, and get the port number of the aps")
                l3switch.clear_mac_table()
                if l3switch.branch == 'netgear':
                    ap_switch_port = '1/0/1-1/0/12'
                elif l3switch.branch == 'huawei':
                    ap_switch_port = ['ethernet0/0/1', 'ethernet0/0/2', 'ethernet0/0/3', 'ethernet0/0/4',
                                      'ethernet0/0/5', 'ethernet0/0/6', 'ethernet0/0/7', 'ethernet0/0/8',
                                      'ethernet0/0/9', 'ethernet0/0/10', 'ethernet0/0/11','ethernet0/0/12']
                l3switch.enable_range_interface(ap_switch_port)
                time.sleep(2)

            logging.info("Detect the switch ports connect to the APs")
            mac_table = self.components['L3Switch'].get_mac_table()
            
            for mac_entry in mac_table:
                if mac_entry['status'] == "Learned":
                    self.mac_to_port[mac_entry['mac'].lower()] = mac_entry['inf']
                    self.mac_to_vlan[mac_entry['mac'].lower()] = mac_entry['vlan']
            for ap_mac in self.mac_to_ap.keys():
                if not self.mac_to_port.has_key(ap_mac):
                    raise Exception("Unable to detect the port connected to \
                                    the device %s" % ap_mac)

            if os.path.isfile(self.mac_to_switch_port_record_file):
                self.config['ap_mac_to_port'] = pi.load(file(self.mac_to_switch_port_record_file,'r'))
            else:
                ap_mac_list = self.config['ap_mac_list']
                for apmac in ap_mac_list:
                    if self.mac_to_port.has_key(apmac):
                        self.config['ap_mac_to_port'].update({apmac:self.mac_to_port[str(apmac)]})

                fl=file(self.mac_to_switch_port_record_file, "w")
                pi.dump(self.config['ap_mac_to_port'], fl)
                fl.close()
                

            if self.config['mesh_enabled']:
                self.config['root_ap_mac_to_port'] = []
                for rootap in self.config['ap_sym_dict'].keys():
                    if re.match(r'\b.+\(Root.+\b', self.config['ap_sym_dict'][rootap]['status']):
                        self.config['root_ap_mac_to_port'].append({'mac': str(self.config['ap_sym_dict'][rootap]['mac']),
                                                                   'port': self.config['ap_mac_to_port'][str(self.config['ap_sym_dict'][rootap]['mac'])],
                                                                   'model': str(self.config['ap_sym_dict'][rootap]['model']),
                                                                   'status': str(self.config['ap_sym_dict'][rootap]['status'])})
                        
                self.config['mesh_ap_mac_to_port'] = []
                for meshap in self.config['ap_sym_dict'].keys():
                    if re.match(r'\b.+\(Mesh.+\b', self.config['ap_sym_dict'][meshap]['status']):
                        self.config['mesh_ap_mac_to_port'].append({'mac': str(self.config['ap_sym_dict'][meshap]['mac']),
                                                                   'port': self.config['ap_mac_to_port'][str(self.config['ap_sym_dict'][meshap]['mac'])],
                                                                   'model': str(self.config['ap_sym_dict'][meshap]['model']),
                                                                   'status': str(self.config['ap_sym_dict'][meshap]['status'])})
                
                #@author: Liang Aihua,@since: 2015-1-13,@change: zf-10762    
                #let the mesh ap's switch port is still disable.
                #if os.path.isfile(self.mac_to_switch_port_record_file):
	            #    logging.info("Disable all mesh aps's switch port, and let the mesh aps join in ZD")
	            #     for mesh_ap_port in self.config['mesh_ap_mac_to_port']:
	            #        l3switch.disable_interface(mesh_ap_port['port'])
        else:
            # There is no managed switch in the testbed
            # This assumes that all APs stay in default VLAN
            for mac in self.mac_to_ap.keys():
                self.mac_to_vlan[mac] = self.zd_vlan

    
    def set_ap_conn_mode(self, testbedinfo, config):
        # Set up the APs to a particular connection mode if requested
        if config.has_key("APConnMode"):
            logging.info("Configure all the AP in the testbed to '%s'" % \
                         config["APConnMode"])

            mode = config["APConnMode"].lower()
            for ap_mac in self.get_aps_sym_dict_as_mac_addr_list():
                self.configure_ap_connection_mode(ap_mac, mode)

            for ap_mac in self.get_aps_sym_dict_as_mac_addr_list():
                start_time = time.time()
                while True:
                    msg = self.verify_ap_connection_mode(ap_mac)
                    if msg:
                        if time.time() - start_time > 120:
                            raise Exception(msg)

                        time.sleep(5)

                    else:
                        break

    def set_Mesh_layout(self, testbedinfo, config):
        # Set up a mesh testbed based on the given layout
        if config.has_key('Mesh'):
            if config['Mesh']['enable']:
                self.enable_mesh()

            if config['Mesh']['enable'] and config['Mesh']['layout']:
                # Convert info stored in config['Mesh']['layout'] to the structures
                # that are used by the form_mesh() function
                rap_list = []
                map_list = []
                for ap_info in config['Mesh']['layout']:
                    if len(ap_info) == 1:
                        # This entry describes a root AP
                        rap_list.append(self.get_ap_mac_addr_by_sym_name(ap_info[0]))

                    elif len(ap_info) == 2:
                        # This entry describes a map AP
                        map_mac = self.get_ap_mac_addr_by_sym_name(ap_info[0])
                        uplink_macs = []
                        for ap_tag in ap_info[1]:
                            uplink_macs.append(self.get_ap_mac_addr_by_sym_name(ap_tag))

                        map_list.append((map_mac, uplink_macs,))

                    else:
                        raise Exception("Invalid layout structure: %s" % str(ap_info))

                self.form_mesh(rap_list, map_list)


    def set_radio_tx_power(self, testbedinfo, config):
        # confiure global txpower to minimus
        if os.path.exists('RAT_TXPOWER_MIN'):
            logging.info('Configure global txpower to minimus')
            txpwr = {'2.4G':'Min', '5G':'Min'}
            AP.cfg_global_tx_power(self.zd, txpwr)


    def verify_testbed(self, upgrade_id = False):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        #Jacky Luh updated by 2012-06-04
        from RuckusAutoTest.components import create_zd_cli_by_ip_addr, create_station_by_ip_addr
        logging.info("Testbed %s Verifying component" % (self.testbed_info.name))
        if self.components.has_key('ZoneDirectorCLI') and self.components['ZoneDirectorCLI'] and upgrade_id:
                self.components['ZoneDirectorCLI'].close()
                del(self.zd_cli)
                self.zd_cli = create_zd_cli_by_ip_addr(self.zd_ipaddr,
                                                       self.zd_username,
                                                       self.zd_password,
                                                       self.zd_shell_key
                                                       )
                self.components['ZoneDirectorCLI'] = self.zd_cli
        
        self.zd.verify_component()
        
        self.zd.init_messages_bundled(self.zd_cli)
        
        # Initialize station components
        if upgrade_id:
            self.components['Station'] = []
            ip_list = self.config['sta_ip_list']
            for i in range(len(ip_list)):
                sta_dict = self.config['sta_conf'].copy()
                sta_dict['sta_ip_addr'] = ip_list[i]

                station = create_station_by_ip_addr(ip_addr = sta_dict.pop('sta_ip_addr'))
                self.components['Station'].append(station)
            
            self.get_ap_object_dict(self.testbed_info, self.config)
            self.set_ap_conn_mode(self.testbed_info, self.config)
            self.set_Mesh_layout(self.testbed_info, self.config)
            self.set_radio_tx_power(self.testbed_info, self.config)
            
        if self.components.has_key('L3Switch') and self.components['L3Switch']:
            self.components['L3Switch'].verify_component()

        if self.components.has_key('Station'):
            for station in self.components['Station']:
                station.verify_component()
        

    def verify_mesh_env(self):
        ap1_status = ''
        for ap_status in self.config['ap_sym_dict']:
            ap1_status = self.config['ap_sym_dict'][ap_status]['status']
            break
        if re.match(r'\b.+(Root|Mesh).+\b', ap1_status):
            return True
        return False

    def enable_mesh(self, mesh_name = "", mesh_psk = ""):
        """ Enable mesh on the ZD and verify the status of all connected AP """
        # Verify the existence of a managed switch
        if not self.components.has_key('L3Switch') or not self.components['L3Switch']:
            msg = "There wasn't any managed switch in the testbed."
            msg += " It was unable to execute mesh specific test cases"
            raise Exception(msg)

        logging.info("Get current mesh configuration on the ZD")
        mesh_conf = self.zd.get_mesh_cfg()
        if mesh_conf['mesh_enable']:
            logging.info("Mesh has been enabled")
            # Quit the function if mesh name/psk are not required to change
            if not mesh_name and not mesh_psk:
                logging.debug("Exit the function because there was nothing to do")
                return

        logging.info("Testbed is to configure mesh on the ZD \
                     [mesh_name %s] [mesh_psk %s]" % \
                     (mesh_name, mesh_psk))

        # Set mesh name/passphrase. It is expected that all the APs will reboot
        # assumption is wrong for new mesh algorithms (7.4)
        self.zd.enable_mesh(mesh_name, mesh_psk)
        if not mesh_conf['mesh_enable']:
            # Mesh has just been enabled, the APs need to be rebooted to do provision
            # If they didn't reboot in the previous command, try to reboot them over telnet
            for mac, ap in self.mac_to_ap.iteritems():
                logging.info("Try to reboot the AP %s" % mac)
                try:
                    ap.reboot()

                except:
                    # Ignore exception. The AP has already been rebooted
                    pass

                # TAK@20090507 close the telnet session to AP
                logging.info("Close telnet session of AP [%s %s]" % (mac, ap.ip_addr))
                ap.close()

            time.sleep(120)

        logging.info("Make sure that all APs are connected with mesh enabled")
        # should get encryption to make sure it is correctly push to AP's
        start_time = time.time()
        timeout = 900
        while True:
            all_done = True
            all_aps_info = self.zd.get_all_ap_info()
            if len(all_aps_info) != len(self.mac_to_ap):
                all_done = False

            else:
                for ap_info in all_aps_info:
                    logging.debug("AP info : %s" % pformat(ap_info, indent = 4))
                    if re.match("Connected \(Mesh AP, [0-9]+ hops?\)", ap_info['status']):
                        continue

                    elif ap_info['status'] == "Connected (Root AP)":
                        continue

                    else:
                        all_done = False
                        break

            if all_done:
                break

            if time.time() - start_time > timeout:
                raise Exception("The APs didn't show up on the ZD as 'Connected' \
                                after %s seconds" % timeout)

            time.sleep(10)

        logging.info("Try to recover the connection to the APs in case the mesh links \
                     were disconnected")
        start_time = time.time()
        for ap_mac, ap in self.mac_to_ap.iteritems():
            while True:
                logging.info("Try to recover the connection to the AP %s" % ap_mac)
                if time.time() - start_time > timeout:
                    msg = "Unable to reconnect to the AP %s after %d seconds" % \
                          (ap_mac, timeout)
                    raise Exception(msg)

                try:
                    ap.verify_component()
                    break

                except:
                    time.sleep(10)

        # Verify the connections one more time after that
        # Sometimes, the links are broken after a while
        time.sleep(10)
        for ap_mac, ap in self.mac_to_ap.iteritems():
            while True:
                logging.info("Try to recover the connection to the AP [%s %s] \
                             one more time." % (ap_mac, ap.ip_addr))

                if time.time() - start_time > timeout:
                    msg = "Unable to reconnect to the AP %s after %d seconds" % \
                          (ap_mac, timeout)
                    raise Exception(msg)

                try:
                    ap.verify_component()
                    break

                except:
                    time.sleep(10)

    def disable_mesh(self):
        """ Disable mesh on the ZD and verify that status of all connected AP """
        # Verify the existence of a managed switch
        if not self.components.has_key('L3Switch') or not self.components['L3Switch']:
            msg = "There wasn't any managed switch in the testbed."
            msg += " It was unable to execute mesh specific test cases"
            raise Exception(msg)
        self.zd.login()

        # Record current channel an txpower of the APs
        all_aps_config = {}
        for mac in self.mac_to_ap.keys():
            logging.info("Record current channel and txpower of the \
                         AP %s on the ZD" % mac)
            all_aps_config[mac] = self.zd.get_ap_cfg(mac)
            all_aps_config[mac]['mesh_uplink_aps'] = []

        # Set configuration on the APs to factory default
        for mac, ap in self.mac_to_ap.iteritems():
            try:
                logging.info("Set configuration on the \
                             AP %s to factory default" % mac)
                ap.set_factory(login=False)
            except:
                pass


        # Enable the switch ports if they were disabled
        logging.info("Turn on the switch ports if any of them have been disabled before")
        for port in self.mac_to_port.values():
            self.components['L3Switch'].enable_interface(port)

        # Reset factory and run the setup wizard
        logging.info("Set configuration of the ZD to factory default")
        mesh_config = {'new_mesh_conf':{'mesh_psk': u'', 'mesh_enable': False, 'mesh_name': ''}}
        self.factory_default_zd(**mesh_config)
        # self.zd.setup_wizard_cfg()
        logging.info("Completed factory_default ZD, sleep 120 seconds.")
        time.sleep(120)

        logging.info("Make sure that all APs connect back to the ZD")
        start_time = time.time()
        timeout = 600
        while True:
            all_done = True
            all_aps_info = self.zd.get_all_ap_info()
            if len(all_aps_info) != len(self.mac_to_ap):
                all_done = False

            else:
                for ap_info in all_aps_info:
                    logging.debug("AP info:\n%s" % pformat(ap_info, indent = 4))
                    if ap_info['status'] != "Connected":
                        all_done = False
                        break

            if all_done:
                break

            if time.time() - start_time > timeout:
                raise Exception("The APs couldn't connect to the ZD after %s \
                                seconds" % timeout)

            time.sleep(15)

        # Reconnect to the APs
        for mac, ap in self.mac_to_ap.iteritems():
            logging.info("Try to reconnect to the AP %s" % mac)
            start_time = time.time()
            while True:
                try:
                    ap.verify_component()
                    break

                except:
                    if time.time() - start_time > timeout:
                        raise Exception("Unable to reconnect to the AP %s" % mac)

                    time.sleep(5)

        # Restore channel and txpower of the APs on the ZD
        for mac, ap_cfg in all_aps_config.iteritems():
            logging.info("Restore channel and txpower of the AP %s on the ZD" % mac)
            self.zd.set_ap_cfg(ap_cfg)


    def factory_default_zd(self, **kwargs):
        zd_reset = RESET.ZD_ResetFactory(self.zd, {}, self, **kwargs)
        (mgmt_vlan, meshcfg) = zd_reset.factory_default()
        zd_reset = None


    def generate_ap_lists(self, topology, model):
        """
        Return the list of root APs and mesh APs satisfy the given model and topology
        @param topology: The expected topology in the format of 'root-mesh-...'
        @param model: The model of the APs that are under test
        @return a tuple of the lists of the root APs and mesh APs
        """
        rap_list = []
        map_list = []

        if model:
            # If model is given, only the APs of that model are verified
            model_set = [model]
        else:
            # Otherwise, all the APs are verified
            model_set = self.model_to_mac_list.keys()

        if not topology:
            topology = "root"
        if not re.match("^root(-mesh)*$", topology.lower()):
            raise Exception("Unknown topology '%s'" % topology)
        roles = topology.lower().split("-")

        for model_name in model_set:
            ap_macs = self.model_to_mac_list[model_name.lower()]
            if len(ap_macs) < len(roles):
                msg = "Not enough AP of model '%s' to build the topology '%s'" % \
                      (model_name, topology)
                raise Exception(msg)

            rap_list.append(ap_macs[0])
            idx = 1
            while idx < len(roles):
                map_list.append((ap_macs[idx], [ap_macs[idx - 1]]))
                idx += 1

        return (rap_list, map_list)

    def form_mesh(self, root_aps, mesh_aps, timeout = 600):
        """
        Configure the ZD and L3Switch to form a mesh
        @param root_aps:
            list of MAC address of root APs [root_ap1, root_ap2, ...]
        @param mesh_aps:
            list of tupple of MAC address of mesh AP and its uplinks APs
            (mesh_ap, [up1, up2, ...])
        """
        # Verify the existence of a managed switch
        if not self.components.has_key('L3Switch') or not self.components['L3Switch']:
            msg = "There wasn't any managed switch in the testbed."
            msg += " It was unable to execute mesh specific test cases"
            raise Exception(msg)

        self._setup_root_aps(root_aps, timeout)
        self._setup_mesh_aps(mesh_aps, timeout)

    def init_aps_sym_dict(self, ap_sym_dict):
        self.ap_sym_dict = ap_sym_dict

    def get_ap_mac_addr_by_sym_name(self, ap_sym_name):
        if re.match(r'^[0-9A-Fa-f:]+$', ap_sym_name):
            return ap_sym_name

        if self.ap_sym_dict and self.ap_sym_dict.has_key(ap_sym_name):
            return self.ap_sym_dict[ap_sym_name]['mac']

        raise "AP symbolic name '%s' does not defined at testbed's attr \
              'ap_sym_dict'" % ap_sym_name

    def get_aps_mac_list(self, ap_mac_list=''):
        if len(ap_mac_list) > 0:
            return ap_mac_list

        return self.get_aps_sym_dict_as_mac_addr_list()


    def get_aps_sym_dict_as_mac_addr_list(self):
        if not self.ap_sym_dict:
            return []

        mac_list = []
        for ap in self.ap_sym_dict.itervalues():
            mac_list.append(ap['mac'])

        return mac_list


    def _setup_root_aps(self, root_aps, timeout):
        """
        A helper function to be called by form_mesh() function to set up a mesh network
        This function verify the root AP candidates and connect them to Ethernet switch
        if they have not been connected.
        @param root_aps: list of MAC address of root APs [root_ap1, root_ap2, ...]
        @param timeout: total time given to spend on setting up the root APs
        """
        # Get current info of all connected APs
        all_aps_info = self.zd.get_all_ap_info()

        # Process the root AP candidates
        while True:
            start_time = time.time()

            # Find an AP in the list which is a MeshAP and make it become Root
            # The farthest MeshAP will be touched first to ensure the connectivity to
            # other MeshAPs is not broken
            target_ap_info = None
            for ap_mac in root_aps:
                ap_info = None
                for x in all_aps_info:
                    if x['mac'].lower() == ap_mac.lower():
                        ap_info = x
                        break

                if not ap_info:
                    raise Exception("AP with MAC %s was not shown on ZD" % ap_mac)

                if ap_info['status'] == "Connected (Root AP)":
                    # It has already been a RootAP
                    continue

                elif re.match("Connected \(Mesh AP, [0-9]+ hops?\)", ap_info['status']):
                    if not target_ap_info:
                        target_ap_info = ap_info

                    elif target_ap_info['status'] < ap_info['status']:
                        target_ap_info = ap_info

                else:
                    # Not either RootAP or MeshAP
                    # It is probably an isolated AP. Give it a try to recover
                    target_ap_info = ap_info
                    break

            if not target_ap_info:
                # All APs have been processed
                break

            logging.info("Found the candidate AP %s" % target_ap_info['mac'])
            root_ap_mac = target_ap_info['mac']

            # This root AP candidate has not become root yet
            logging.info("Enable the switch port %s connected to the AP" % \
                         self.mac_to_port[root_ap_mac.lower()])

            self.components['L3Switch'].enable_interface(self.mac_to_port[root_ap_mac.lower()])

            # Verify the connection to the AP
            while True:
                try:
                    self.mac_to_ap[root_ap_mac.lower()].verify_component()
                    break

                except:
                    time.sleep(5)

                if time.time() - start_time > 120:
                    logging.info("Unable to reconnect to the AP %s" % root_ap_mac)
                    break


            # Verify the currently managed APs on the ZD to make sure that the AP has become Root
            # Get information of the AP shown on the ZD
            while True:
                # Update the list of all connected APs on the ZD
                all_aps_info = self.zd.get_all_ap_info()
                target_ap_info = None
                for ap_info in all_aps_info:
                    if ap_info['mac'].upper() == root_ap_mac.upper():
                        target_ap_info = ap_info
                        break

                if not target_ap_info:
                    raise Exception("AP with MAC %s was not shown on ZD" % root_ap_mac)

                if ap_info['status'] == "Connected (Root AP)":
                    break

                if time.time() - start_time > timeout:
                    msg = "The root AP candidate's status was '%s' instead of \
                          'Connected (Root AP)' after %d seconds" % (ap_info['status'], timeout)

                    raise Exception(msg)

                time.sleep(5)

            logging.info("The AP has become Root AP")

            # Connect to the AP component
            try:
                self.mac_to_ap[root_ap_mac.lower()].verify_component()

            except:
                pass

            # Move on processing the next AP
        # End of for statement

    def _setup_mesh_aps(self, mesh_aps, timeout):
        """
        A helper function to be called by form_mesh() function to set up a mesh network
        This function verify the mesh AP candidates and remove them from the Ethernet switch
        if they have been connected.
        @param mesh_aps:
            list of tupple of MAC address of mesh AP and its uplinks APs
            (mesh_ap, [up1, up2, ...])
        @param timeout:
            total time given to spend on setting up the mesh APs
        """
        # Get current info of all connected APs
        all_aps_info = self.zd.get_all_ap_info()

        # Process the mesh AP candidates
        processed_mesh_ap_list = []
        for mesh_ap_info in mesh_aps:
            start_time = time.time()

            mesh_ap_mac, ul_ap_list = mesh_ap_info
            logging.info("Work on mesh AP candidate %s" % mesh_ap_mac)
            # Search for the target AP in the list of connected APs
            target_ap_info = None
            for ap_info in all_aps_info:
                if ap_info['mac'].upper() == mesh_ap_mac.upper():
                    target_ap_info = ap_info
                    break

            if not target_ap_info:
                raise Exception("AP with MAC %s was not shown on ZD" % mesh_ap_mac)

            # Check to see if it is necessary to reboot the AP
            if re.match("Connected \(Mesh AP, [0-9]+ hops?\)", target_ap_info['status']):
                # No need, it has already become Mesh AP
                # Move to processing the next root candidate
                logging.info("AP [%s %s] is a MeshAP; no reboot required." % \
                             (ap_info['mac'], ap_info['ip_addr']))
                continue

            # This mesh AP candidate has not become mesh AP yet
            logging.info("Configure the uplink APs for the Mesh AP")
            ap_conf = {'mac_addr':mesh_ap_mac, 'channelization':'', 'channel':'',
                       'txpower':'', 'mesh_uplink_aps':ul_ap_list}

            self.zd.set_ap_cfg(ap_conf)
            logging.info("Configure the uplink APs for Mesh AP [%s %s]; with config:\n%s" \
                        % (ap_info['mac'], ap_info['ip_addr'], pformat(ap_conf, indent = 4)))

            time.sleep(3)

            # It is not necessary to reboot the APs in Odessa
            # logging.info("Reboot the AP without logging to the AP")
            # self.mac_to_ap[mesh_ap_mac.lower()].reboot()

            # TAK@Tikona_7.4; for some reason unkown: when AP mgmt_vlan is enabled,
            # and telnet connection to AP exist;
            # if the AP is deattached from the netgear switch; the AP might not
            # be able to join back.
            processed_mesh_ap_list.append((ap_info['mac'], ap_info['ip_addr']))
            logging.info("Close connection to AP [%s %s] before disabling its switch port."
                        % (ap_info['mac'], ap_info['ip_addr']))

            self.mac_to_ap[mesh_ap_mac.lower()].close()

            logging.info("Disable the switch port %s connected to the AP [%s %s]" \
                        % (self.mac_to_port[mesh_ap_mac.lower()], ap_info['mac'], ap_info['ip_addr']))

            logging.info("Disable the switch port %s connected to the AP" % \
                         self.mac_to_port[mesh_ap_mac.lower()])

            self.components['L3Switch'].disable_interface(self.mac_to_port[mesh_ap_mac.lower()])
            time.sleep(10)

            logging.info("Try to login to AP [%s %s]" % (ap_info['mac'], ap_info['ip_addr']))
            timeout = 600
            while True:
                if time.time() - start_time > timeout:
                    raise Exception("Unable to connect to the AP via SSH/telnet after \
                                    disabling the switch port")
                try:
                    self.mac_to_ap[mesh_ap_mac.lower()].login()
                    logging.info("Login to the AP successfully. [MeshAP.Assoc.Time %d]" % \
                                 int(time.time() - start_time))
                    break

                except:
                    time.sleep(30)

            # Verify the currently managed APs on the ZD to make sure that the AP has become Mesh
            # Get information of the AP shown on the ZD
            while True:
                # Update the list of all connected APs on the ZD
                all_aps_info = self.zd.get_all_ap_info()
                target_ap_info = None
                for ap_info in all_aps_info:
                    if ap_info['mac'].upper() == mesh_ap_mac.upper():
                        target_ap_info = ap_info
                        break

                if not target_ap_info:
                    raise Exception("AP with MAC %s was not shown on ZD" % mesh_ap_mac)

                if re.match("Connected \(Mesh AP, [0-9]+ hops?\)", ap_info['status']):
                    break

                if time.time() - start_time > timeout:
                    msg = "The mesh AP candidate's status was still '%s' instead of \
                          'Connected (Mesh AP, n hop)' after %d seconds" % \
                          (ap_info['status'], timeout)

                    raise Exception(msg)

                time.sleep(5)

            logging.info("The AP has become Mesh AP")

        logging.info("Completed setup mesh APs: %s" % str(processed_mesh_ap_list))
        time.sleep(5)


    def verify_root_aps(self, root_aps, mesh_name = "", mesh_psk = ""):
        """ Verify the mesh related information shown on the APs
        @param root_aps: list of MAC address of root APs [root_ap1, root_ap2, ...]
        @param mesh_name: verify mesh name if it is not null
        @param mesh_psk: verify mesh pass-phrase if it is not null
        """
        for root_ap_mac in root_aps:
            logging.info("Work on root AP %s" % root_ap_mac)
            logging.info("Verify the WLANs shown on the AP")
            for (wlan_id, wlan) in self.mac_to_ap[root_ap_mac.lower()].get_wlan_info_dict().iteritems():
                msg = "Information of %s interface was shown incorrectly on the AP %s: %s" % \
                       (wlan['name'], root_ap_mac, wlan)

                if (wlan['name'] == "meshd" and (wlan['status'] != "up" or wlan['type'] != "AP")):
                    return ("FAIL", msg)

                elif (wlan['name'] == "meshu" and (wlan['status'] != "down" or  wlan['type'] != "STA")):
                    return ("FAIL", msg)

            logging.info("Verify the mesh links shown on the AP")
            root_ap_link_info = None
            for (mac, link_info) in self.mac_to_ap[root_ap_mac.lower()].get_mesh_info_dict().iteritems():
                # The root AP itself
                if link_info['Management-MAC'].upper() == root_ap_mac.upper():
                    root_ap_link_info = link_info
                    break

            if not root_ap_link_info:
                raise Exception("Not found link information of the Root AP shown on AP %s" % root_ap_mac)

            if root_ap_link_info['S'] != "R" or root_ap_link_info['D'] != "1":
                msg = "Information of the root AP was shown incorrectly on the AP %s: %s" % \
                      (root_ap_mac, root_ap_link_info)

                return ("FAIL", msg)

            # Verify the mesh name and pass-phrase if required
            if mesh_name or mesh_psk:
                ul_encryption = self.mac_to_ap[root_ap_mac.lower()].get_encryption(wlan_if = "meshu", use_id = False)
                dl_encryption = self.mac_to_ap[root_ap_mac.lower()].get_encryption(wlan_if = "meshd", use_id = False)
                if mesh_name:
                    logging.info("Verify the mesh name shown on the AP")
                    if ul_encryption['ssid'] != mesh_name:
                        msg = "SSID of the 'meshu' interface was shown incorrectly: '%s'" % ul_encryption['ssid']
                        return ("FAIL", msg)

                    if dl_encryption['ssid'] != mesh_name:
                        msg = "SSID of the 'meshd' interface was shown incorrectly: '%s'" % dl_encryption['ssid']
                        return ("FAIL", msg)

                if mesh_psk:
                    logging.info("Verify the mesh passphrase shown on the AP")
                    if ul_encryption['WPA PassPhrase'] != mesh_psk:
                        msg = "WPA pass-phrase of the 'meshu' interface was shown incorrectly: '%s'" % \
                              ul_encryption['WPA PassPhrase']
                        return ("FAIL", msg)

                    if dl_encryption['WPA PassPhrase'] != mesh_psk:
                        msg = "WPA pass-phrase of the 'meshd' interface was shown incorrectly: '%s'" % \
                              dl_encryption['WPA PassPhrase']
                        return ("FAIL", msg)

        return ("PASS", "")


    def verify_mesh_aps(self, mesh_aps, mesh_name = "", mesh_psk = ""):
        """ Verify the mesh related information shown on the APs
        @param mesh_aps: list of tuple of MAC address of mesh AP and its uplinks APs (mesh_ap, [up1, up2, ...])
        @param mesh_name: verify mesh name if it is not null
        @param mesh_psk: verify mesh pass-phrase if it is not null
        """
        for mesh_ap_info in mesh_aps:
            mesh_ap_mac, ul_ap_list = mesh_ap_info
            logging.info("Work on mesh AP %s" % mesh_ap_mac)

            logging.info("Verify the WLANs shown on the AP")
            for (wlan_id, wlan) in self.mac_to_ap[mesh_ap_mac.lower()].get_wlan_info_dict().iteritems():
                msg = "Information of %s interface was shown incorrectly on the AP %s: %s" % \
                       (wlan['name'], mesh_ap_mac, wlan)

                if (wlan['name'] == "meshd" and (wlan['status'] != "up" or wlan['type'] != "AP")):
                    return ("FAIL", msg)

                elif (wlan['name'] == "meshu" and (wlan['status'] != "up" or  wlan['type'] != "STA")):
                    return ("FAIL", msg)

            logging.info("Verify the mesh links shown on the AP")
            mesh_ap_link_info = None
            ul_ap_link_info = None
            for (mac, link_info) in self.mac_to_ap[mesh_ap_mac.lower()].get_mesh_info_dict().iteritems():
                # The mesh AP itself
                if link_info['Management-MAC'].upper() == mesh_ap_mac.upper():
                    mesh_ap_link_info = link_info

                else:
                    for ul_ap_mac in ul_ap_list:
                        if link_info['Management-MAC'].upper() == ul_ap_mac.upper():
                            ul_ap_link_info = link_info

            if not mesh_ap_link_info:
                raise Exception("Not found link information of the Mesh AP shown on AP %s" % mesh_ap_mac)

            if not ul_ap_link_info:
                raise Exception("Not found link information of the uplink AP shown on AP %s" % mesh_ap_mac)

            if mesh_ap_link_info['S'] != "M" or mesh_ap_link_info['D'] != "2":
                msg = "Information of the mesh AP was shown incorrectly on the AP %s: %s" % \
                      (mesh_ap_mac, mesh_ap_link_info)

                return ("FAIL", msg)

            if ul_ap_link_info['S'] != "U" or ul_ap_link_info['D'] != "1":
                msg = "Information of the uplink AP was shown incorrectly on the AP %s: %s" % \
                      (mesh_ap_mac, ul_ap_link_info)

                return ("FAIL", msg)

            # Verify the mesh name and pass-phrase if required
            if mesh_name or mesh_psk:
                ul_encryption = self.mac_to_ap[mesh_ap_mac.lower()].get_encryption(wlan_if = "meshu", use_id = False)
                dl_encryption = self.mac_to_ap[mesh_ap_mac.lower()].get_encryption(wlan_if = "meshd", use_id = False)
                if mesh_name:
                    logging.info("Verify the mesh name shown on the AP")
                    if ul_encryption['ssid'] != mesh_name:
                        msg = "SSID of the 'meshu' interface was shown incorrectly: '%s'" % ul_encryption['ssid']
                        return ("FAIL", msg)

                    if dl_encryption['ssid'] != mesh_name:
                        msg = "SSID of the 'meshd' interface was shown incorrectly: '%s'" % dl_encryption['ssid']
                        return ("FAIL", msg)

                if mesh_psk:
                    logging.info("Verify the mesh passphrase shown on the AP")
                    if ul_encryption['WPA PassPhrase'] != mesh_psk:
                        msg = "WPA pass-phrase of the 'meshu' interface was shown incorrectly: '%s'" % \
                              ul_encryption['WPA PassPhrase']

                        return ("FAIL", msg)

                    if dl_encryption['WPA PassPhrase'] != mesh_psk:
                        msg = "WPA pass-phrase of the 'meshd' interface was shown incorrectly: '%s'" % \
                              dl_encryption['WPA PassPhrase']

                        return ("FAIL", msg)

        return ("PASS", "")


    def cleanup_mesh_test_script(self):
        logging.info("Clean up the testbed")
        # If the APs were disconnected or dead, try to recover them
        dead_ap = []
        for mac, ap in self.mac_to_ap.iteritems():
            try:
                logging.info("Verify apmgrinfo of the AP %s" % mac)
                info = ap.get_ap_mgr_info()
                if info['State'] != "RUN":
                    logging.info("The AP's apmgrinfo state was '%s' instead of 'RUN'. Try to recover it." % info['State'])
                    dead_ap.append(mac)

                else:
                    logging.info("The AP's apmgrinfo state was 'RUN'")

            except:
                logging.info("The AP %s was dead or unreachable" % mac)
                dead_ap.append(mac)

        if dead_ap:
            # Try to make the dead APs become root APs
            logging.info("Configure the APs %s to become RootAPs" % str(dead_ap))
            self.form_mesh(dead_ap, [])

    def _detect_ap_dynamic_addresses(self, ap_mac_list):
        """
        Obtain the contain of the dhcpd.leases file stored on the Linux DHCP server and parse to get
        the IP addresses assigned to the AP based on their MAC addresses
        """
        lease_data = self.components['LinuxServer'].get_dhcp_leases()
        map = {}
        ip = mac = start_time = None
        for line in lease_data:
            l = line.split()
            if l[0] == "lease":
                ip = l[1]

            elif l[0] == "hardware":
                mac = l[2].strip(";")

            elif l[0] == "starts":
                start_time_str = " ".join(l[2:]).strip(";")
                start_time = time.mktime(time.strptime(start_time_str, "%Y/%m/%d %H:%M:%S"))

            if ip and mac and start_time:
                if map.has_key(mac):
                    if map[mac][0] < start_time:
                        map[mac] = (start_time, ip)

                else:
                    map[mac] = (start_time, ip)

                ip = mac = start_time = None

        for ap_mac in ap_mac_list:
            if map.has_key(ap_mac.lower()):
                self.mac_to_ip[ap_mac.lower()] = map[ap_mac.lower()][1]

            else:
                raise Exception("IP entry of the MAC %s was not found in the \
                                dhcpd.leases file" % ap_mac.lower())
    #jluh added by 2013-10-11 (undo_reboot)
    def configure_ap_connection_mode(self, ap_mac, mode, discovery_method = "", undo_reboot = False):
        """
        Configure the connection mode of the AP with given MAC address.
        This can be done by specifying the IP address of the ZD or moving the AP
        to/from the VLAN of the ZD

        @param ap_mac:
            MAC address of the AP object
        @param mode:
            new connection mode to be configured for the AP
        @param discovery_method:
            the method used by the AP to discover the ZD after changing to new mode
        """
        if not self.components.has_key("L3Switch"):
            raise Exception("There was not any managed switch present in the testbed")

        logging.debug("The AP '%s' VLAN: %s" % (ap_mac, self.mac_to_vlan[ap_mac]))
        logging.debug("The ZD VLAN: %s" % self.zd_vlan)
        logging.debug("Expected connection mode: %s" % mode.upper())

        ap_obj = self.mac_to_ap[ap_mac]
        rebooted = False
        mode = mode.lower()
        discovery_method = discovery_method.lower()
        logging.info("New connection mode: '%s' - discovery method: '%s'" % \
                     (mode, discovery_method))

        if discovery_method in ["fixed-pri", "fixed-sec"]:
            if discovery_method == "fixed-pri":
                ip1 = self.zd.ip_addr
                ip2 = ""

            else:
                ip1 = "1.1.1.1"
                ip2 = self.zd.ip_addr

            logging.info("Configure director info on the AP '%s' to '%s' and '%s'" % \
                         (ap_mac, ip1, ip2))

            ap_obj.set_director_info(ip1, ip2)
            logging.info("Reboot the AP to make the new change take effect")
            ap_obj.reboot(login=False)
            rebooted = True

        else:
            logging.info("Get current director information on the AP")
            zd_cfg_on_ap = ap_obj.get_director_cfg()

            if discovery_method in ["dns", "dhcp"]:
                logging.info("Reset AP's configuration to factory default in order to \
                             clear the ZD record")

                # Modified by Serena Tan.2010.11.12.
                # To correct the argument.
#                ap_obj.set_factory(reboot=False)
                ap_obj.set_factory(login=False)
                rebooted = True

            if zd_cfg_on_ap["pri_zd_ip"] or zd_cfg_on_ap["sec_zd_ip"]:
                logging.info("Clear director information on the AP")
                ap_obj.set_director_info(ip1 = "", ip2 = "")
                ap_obj.reboot(login=False)
                rebooted = True

            if discovery_method and not rebooted:
                logging.info("Reboot the AP")
                ap_obj.reboot(login=False)
                rebooted = True

        if mode == "l3" and self.mac_to_vlan[ap_mac] == self.zd_vlan:
            if not undo_reboot and not rebooted:
                logging.info("Reboot the AP")
                ap_obj.set_factory(login=False)
                # JLIN@08102010 no need to reboot since set_factory already included reboot procedure
                #ap_obj.reboot(login=False)
                rebooted = True

            logging.info("Move the AP from VLAN %s to VLAN %s" % \
                         (self.mac_to_vlan[ap_mac], self.remote_vlan))

            self.components["L3Switch"].remove_interface_from_vlan(
                self.mac_to_port[ap_mac],
                self.mac_to_vlan[ap_mac])

            self.components["L3Switch"].add_interface_to_vlan(
                self.mac_to_port[ap_mac],
                self.remote_vlan)

            self.mac_to_vlan[ap_mac] = self.remote_vlan

        elif mode == 'l2':
            if self.mac_to_vlan[ap_mac] != self.zd_vlan:
                if not undo_reboot and not rebooted:
                    logging.info("Reboot the AP")
                    ap_obj.set_factory(login=False)
                    # JLIN@08102010 no need to reboot since set_factory already included reboot procedure
                    #ap_obj.reboot(login=False)
                    rebooted = True

                logging.info("Move the AP from VLAN %s to VLAN %s" % \
                             (self.mac_to_vlan[ap_mac], self.zd_vlan))

                self.components["L3Switch"].remove_interface_from_vlan(
                    self.mac_to_port[ap_mac],
                    self.mac_to_vlan[ap_mac])

                self.components["L3Switch"].add_interface_to_vlan(
                    self.mac_to_port[ap_mac],
                    self.zd_vlan)

                self.mac_to_vlan[ap_mac] = self.zd_vlan

            else:
                rebooted = self.reboot_ap_if_not_l2_mode(ap_mac)

        if not undo_reboot and rebooted:
            logging.info("Try to reconnect to the AP after it is rebooted")

            base_time = time.time()
            while True:
                try:
                    # JLIN@08102010
                    # fixed ap ssh error while ap is not boot up for sshd running
                    # if ap from l2 change to l3, ap is rebooted by script
                    # if ap already keep on l3 status, ap isn't rebooted by script
                    logging.debug("Waiting AP reboot for 240 seconds")
                    time.sleep(240) #
                    logging.info("Detect the new IP leased of the AP at new VLAN")
                    self._detect_ap_dynamic_addresses([ap_mac])

                    logging.debug("MAC to IP table: %s" % self.mac_to_ip)

                    ap_obj.ip_addr = self.mac_to_ip[ap_mac]
                    logging.info("Try to connect to the AP at new IP %s" % \
                                  self.mac_to_ip[ap_mac])
                    
                    ap_obj.verify_component()
                    break

                except:
                    if time.time() - base_time > 360:
                        msg = "Unable to reconnect to the AP '%s' after making it \
                              become %s AP" % (ap_mac, mode)
                        raise Exception(msg)

                    time.sleep(10)
                    logging.info("Fail. Give it another try")

    def _map_apmgrinfo_keys(self, info):
        '''
        '''
        known_keys = {
            'ZoneDir found thru': '',
            'Discover Director By': '',
            'ZoneDir found by': '',
        }
        value = None
        for key in known_keys.iterkeys():
            if info.has_key(key):
                value = info[key]
                break

        for key in known_keys.iterkeys():
            info.update({key: value})

        return info


    def reboot_ap_if_not_l2_mode(self, ap_mac):
        ap_obj = self.mac_to_ap[ap_mac]
        apmgrinfo = ap_obj.get_ap_mgr_info()
        apmgrinfo = self._map_apmgrinfo_keys(apmgrinfo)

        if (re.search('^l2', apmgrinfo['Tunnel/Sec Mode'], re.I) and
            re.search('^l2', apmgrinfo['ZoneDir found thru'], re.I)):
                return False
        logging.info("[AP %s] [mode '%s'] not in L2. Reboot it." % \
                     (ap_mac, apmgrinfo['Tunnel/Sec Mode']))
        ap_obj.reboot(login=False)
        time.sleep(60)
        return True

    def verify_ap_connection_mode(self, ap_mac, discovery_method = ""):
        """
        Verify the information shown by apmgrinfo in AP's Linux shell and on ZD's webui
        The VLAN location of the APs are also considerred
        """
        ap_obj = self.mac_to_ap[ap_mac]

        logging.info("Get apmgrinfo of the AP %s" % ap_mac)
        start_time = time.time()
        while True:
            apmgrinfo = ap_obj.get_ap_mgr_info()
            apmgrinfo = self._map_apmgrinfo_keys(apmgrinfo)

            if apmgrinfo and apmgrinfo["State"] == "RUN":
                break

            time.sleep(2)
            if time.time() - start_time > 120:
                raise Exception("AP '%s' was not in RUN state" % ap_mac)

        logging.debug("Obtained info: %s" % apmgrinfo)

        logging.info("Get detailed information in ZD's webui about the AP %s" % ap_mac)
        ap_info = APS.get_ap_detail_info_by_mac_addr(self.zd, ap_mac)
        logging.debug("Obtained infor: %s" % ap_info)

        # Verify if the connection mode shown on AP's CLI and ZD are the same and correct
        conn_mode_in_zd = ap_info['tunnel_mode'].lower()
        # Use only first two characters (L2 or L3)
        conn_mode_in_zd = conn_mode_in_zd[:2]

        conn_mode_in_ap = apmgrinfo['Tunnel/Sec Mode'].split("/")[0].strip().lower()
        conn_mode_in_ap = conn_mode_in_ap[:2]

        if conn_mode_in_ap != conn_mode_in_zd:
            msg = "The connection mode shown on AP's CLI was '%s'" % conn_mode_in_ap
            msg += ", which was different from the mode shown on ZD's webui '%s'" % \
                   conn_mode_in_zd
            return msg

        discovery_reason = {"fixed-pri": "Preferred Primary",
                            "fixed-sec": "Preferred Secondary",
                            "dns": "DNS", "dhcp": "DHCP",
                            "record": "Last ZoneDir Joined", "l2": "L2 Discovery"}

        if discovery_method in ["fixed-pri", "fixed-sec", "dns", "dhcp"]:
            if conn_mode_in_ap != "l3":
                msg = ("The connection mode was %s instead of L3 [AP %s] [dmode %s]" %
                      (conn_mode_in_ap.upper(), ap_mac, discovery_method))
                return msg

            if apmgrinfo['Discover Director By'] != discovery_reason[discovery_method]:
                msg = "The discover method showed on AP's CLI was '%s'" % \
                      apmgrinfo['Discover Director By']
                msg += ", it should have been '%s'" % discovery_reason[discovery_method]
                return msg

        elif discovery_method == "record":
            if apmgrinfo['Discover Director By'] != discovery_reason[discovery_method]:
                msg = "The discover method showed on AP's CLI was '%s'" % \
                      apmgrinfo['Discover Director By']
                msg += ", it should have been '%s'" % discovery_reason[discovery_method]
                return msg

        else:
            if self.mac_to_vlan[ap_mac] == self.zd_vlan:
                if conn_mode_in_ap != "l2":
                    msg = ("The connection mode was %s instead of L2 [AP %s] [dmode %s]" %
                          (conn_mode_in_ap.upper(), ap_mac, discovery_method))
                    return msg

                if apmgrinfo['Discover Director By'] not in discovery_reason["l2"]:
                    msg = "The discover method showed on AP's CLI was '%s'" % \
                          apmgrinfo['Discover Director By']
                    msg += ", it should have been '%s'" % discovery_reason["l2"]
                    return msg

            else:
                if conn_mode_in_ap != "l3":
                    msg = ("The connection mode was %s instead of L3 [AP %s] [dmode %s]" %
                          (conn_mode_in_ap.upper(), ap_mac, discovery_method))
                    return msg

        return ""


    def verify_station_mac_in_tunnel_mode(self, active_ap_mac, sta_mac, tunnel_enabled):
        if not self.components.has_key("L3Switch"):
            logging.info("There was no L3Switch in the testbed. Unable to verify \
                         station MAC address")
            return ""

        zd_mac = self.zd_cli.sysinfo['MAC Address'].lower()
        #Add by liang aihua for nat test environment 2015-7-2
        if self.config.has_key('router'):
            router_mac = self.config['router']['mac']
            zd_mac = router_mac

        mac_table = self.components["L3Switch"].get_mac_table()
        time.sleep(2)
        logging.debug("MAC address table: %s" % mac_table)
        logging.debug("AP MAC: %s - ZD MAC: %s - STA MAC: %s" % \
                      (active_ap_mac, zd_mac, sta_mac))

        zd_port = ''
        ap_port = ''
        sta_port = ''
            
        for mac_entry in mac_table:
            if mac_entry["mac"].lower() == zd_mac: zd_port = mac_entry["inf"]
            elif mac_entry["mac"].lower() == active_ap_mac: ap_port = mac_entry["inf"]
            elif mac_entry["mac"].lower() == sta_mac: sta_port = mac_entry["inf"]
        if not zd_port:
            raise Exception("Not found MAC address of the ZD '%s' on the L3 switch" % \
                            zd_mac)
        if not ap_port:
            raise Exception("Not found MAC address of the active AP '%s' on the L3 switch" % \
                            active_ap_mac)
        if not sta_port:
            raise Exception("Not found MAC address of the station '%s' on the L3 switch" % \
                            sta_mac)

        logging.debug("AP port: %s - ZD port: %s - STA port: %s" % \
                      (ap_port, zd_port, sta_port))
        
        if tunnel_enabled:
            logging.info("Verify MAC address of the wireless client when tunnel is enabled")
            if sta_port != zd_port:
                msg = "The port of the station on the managed switch was '%s'"
                msg += ", which is different to the ZD's port '%s', while tunnel was enabled"
                return msg % (sta_port, zd_port)

            if sta_port == ap_port:
                msg = "The port of the station on the managed switch was '%s'"
                msg += ", which is the same as the AP's port '%s', while tunnel was enabled"
                return msg % (sta_port, ap_port)

        else:
            logging.info("Verify MAC address of the wireless client when tunnel is disabled")
            if sta_port == zd_port:
                msg = "The port of the station on the managed switch was '%s'"
                msg += ", which is the same as the ZD's port '%s', while tunnel was disabled"
                return msg % (sta_port, zd_port)

            if sta_port != ap_port:
                msg = "The port of the station on the managed switch was '%s'"
                msg += ", which is different to the AP's port '%s', while tunnel was disabled"
                return msg % (sta_port, ap_port)


    def get_ap_role_info(self, ap_status_str, ap_info = {}):
        p_ap_status = r"Connected\s+\((Root|Mesh|Link)\s+AP(|,\s+([0-9]+)\s+hops?)\)"
        m = re.match(p_ap_status, ap_status_str, re.I)
        if m:
            aprole = m.group(1)
            aphops = m.group(3) if m.group(3) else 0
            if aprole == 'Root' or (re.match('Mesh|Link', aprole) and aphops > 0):
                ok = True

            else:
                # '(Mesh AP, 0 hops)' is a transit state; make it not a Valid status
                ok = False

            if not ap_info:
                ap_info.update({'ok':ok, 'role':aprole, 'hops':aphops})

            return (ok, aprole, aphops)

        return (False, '', 0)


    def get_mesh_info_by_ap_mac(self, ap_mac):
        ap_mac = ap_mac.lower()
        mesh_dict = self.mac_to_ap[ap_mac].get_mesh_info_dict()
        try:
            return mesh_dict[ap_mac]

        except:
            return None


    def get_mesh_and_its_uplink_info(self, mesh_ap_mac, uplink_ap_mac_list):
        ap_mac = mesh_ap_mac.lower()
        mesh_dict = self.mac_to_ap[ap_mac].get_mesh_info_dict()
        if not mesh_dict.has_key(ap_mac):
            return (None, None)

        mesh_ap_info = mesh_dict[ap_mac]
        # a meshAP can only have one uplinkAP; find one then exit
        for ap_mac in uplink_ap_mac_list:
            ap_mac = ap_mac.lower()
            if mesh_dict.has_key(ap_mac):
                return (mesh_ap_info, mesh_dict[ap_mac])

        return (None, None)


    def enable_ap_switch_ports(self, **kwargs):
        if self._wait_for_aps_become_root():
            return

        # AP ports are defined from 1 to 12 by default; should be configurable.
        # It, in worst case, tooks around 15 minutes for AP to become ROOT
        fcfg = dict(timeout = 1000, pause = 30, portrange = '1/0/1-1/0/12')
        fcfg.update(kwargs)
        from RuckusAutoTest.components import NetgearSwitchRouter
        if self.components.has_key('L3Switch'):
            l3s = self.components['L3Switch'].conf
            ng2cfg = dict(ip_addr = l3s['ip_addr'],
                          username = l3s['username'],
                          password = l3s['password'])

            ng2 = NetgearSwitchRouter.NetgearSwitchRouter(ng2cfg)
            cmdblock = "interface range %s\nno shutdown" % (fcfg['portrange'])
            logging.info("[Enable APSwitchPort] [ports %s] [Wait for APs become root]" % \
                         (fcfg['portrange']))
            ng2.do_cfg(cmdblock)
            del(ng2)
            time.sleep(30)
            self.wait_for_aps_become_root(**fcfg)


    def wait_for_aps_become_root(self, **kwargs):
        fcfg = dict(timeout = 1000, pause = 30)
        fcfg.update(kwargs)
        start_time = time.time()
        while True:
            if self._wait_for_aps_become_root():
                return

            logging.info("[Waiting APs become root] [for another %s]" % \
                         (str(fcfg['pause'])))
            time.sleep(int(fcfg['pause']))


    def _wait_for_aps_become_root(self):
        all_aps_info = self.zd.get_all_ap_info()

        for ap_info in all_aps_info:
            if ap_info['status'].find("Connected (Root") < 0:
                return False

        return True

    #Jacky.Luh update by 2012-06-26
    def UpgradeDUT(self, build):
        """
        Upgrade the primary testbed DUT to the specified software build.
        This relies on the DUT class upgrade function to only return after
        the upgrade has successfully completed.
        """
        elapsed = None
        factory_id = False
        upgrade_id = True
        list_of_connected_aps = list()
        build_stream = build.build_stream.name
        build_version = str(build_stream.split("_")[1])
        bno = build.number
        zd_model_num = build_stream.split("_")[0]
        base_build_project_num = build_stream.split("_")[1]
        mesh_enabled = self.is_mesh_enabled_in_testbed()
        ap_upgrade_timeout = 1500
        
        build_url = build.URL
        byte = None
        mb = None
        tb_config = self.config
        
        #get the switch component object
        if 'L3Switch' in self.components.keys():
            l3switch = self.components['L3Switch']
        
        #because upgrade to the base build, waiting time too long, 
        #the station sockect connection break, so quit the station at first,
        #after the upgrage zd, recreate the station object:
        for station in self.components['Station']:
            station.__del__()
        del(self.components['Station'])
        
        #set the image file name.
        if server_url_map.SAVE_REPOSITORY.has_key(zd_model_num):
            filename = zd_model_num + "_" + base_build_project_num + "." + str(bno) + ".tar.gz"
            if os.path.isdir(server_url_map.SAVE_REPOSITORY[zd_model_num]['share_folder_path']):
                full_fname = os.path.join(server_url_map.SAVE_REPOSITORY[zd_model_num]['share_folder_path'], filename)
            else:
                full_fname = os.path.join(server_url_map.SAVE_REPOSITORY[zd_model_num]['local_path'], filename)
        
        #if no the image file in the target folder,
        #the script will be downloaded it from the build server
        #if the image file is in the target folder,
        #the script will upgrade zd to the base build which is used the image.    
        if os.path.isfile(full_fname):
            pass
        elif os.path.isdir(full_fname):
            logging.info("Please remove the folder of %s" % filename)
            raise Exception("This is a folder, instead of a file.")
        else:
            build_url = ih.get_build_url(build_stream, bno)
            if 'http' in build_url:
                if '.img' in build_url:
                    filename = re.findall(r'^.*ZD\d+\w+/*(.*)', build_url)[0]
                    if os.path.isdir(server_url_map.SAVE_REPOSITORY[zd_model_num]['share_folder_path']):
                        full_fname = os.path.join(server_url_map.SAVE_REPOSITORY[zd_model_num]['share_folder_path'], filename)
                    else:
                        full_fname = os.path.join(server_url_map.SAVE_REPOSITORY[zd_model_num]['local_path'], filename)
                fin = ih.download_build_v2(build_url, full_fname)
                if fin:
                    pass
                else:
                    raise Exception("downloaded is not successufully.")
            else:
                full_fname = build_url
                
        logging.info("Waiting all aps join in zd...")
        if not self.dut.wait_aps_join_in_zd_with_the_expect_status(self.config['ap_mac_list'], self.config['ap_sym_dict']):
            logging.info("ap rejoin in zd failed, enable all aps's switch ports")
            for ap_mac in self.config['ap_mac_to_port'].keys():
                l3switch.enable_interface(self.config['ap_mac_to_port'][ap_mac])
                
        (elapsed, factory_id) = self.dut.upgrade_sw(full_fname, False, True, build_version, False, mesh_enabled)
        
        if factory_id:
            logging.info("ZD be setted factory default, so enable all switch ports of the aps.")
            for ap_mac in self.config['ap_mac_to_port'].keys():
                l3switch.enable_interface(self.config['ap_mac_to_port'][ap_mac])
        
        logging.info("Waiting 2 minutes, let ZD all service module enabled.")
        time.sleep(120)

        logging.info("Waiting for APs to be upgraded and reconnect. This process takes some minutes. Please wait... ")
        ap_upgrade_start_time = time.time()
        list_of_connected_aps = list()
        for associated_ap in self.config['ap_mac_list']:
            while True:
                if (time.time() - ap_upgrade_start_time) > ap_upgrade_timeout:
                    raise Exception("Error: AP upgrading failed. Timeout")
                
                si_ap_info = self.dut._get_ap_info(associated_ap)
                status = si_ap_info['status']
                logging.info('ap %s status is %s'%(associated_ap, status))
                if status.lower().startswith("connected"):
                    list_of_connected_aps.append(si_ap_info)
                    break
               
        return upgrade_id, factory_id, list_of_connected_aps
    
    #Jacky.Luh update by 2012-06-26
    def is_mesh_enabled_in_testbed(self):
        for sym_ap in self.config['ap_sym_dict'].keys():
            status = self.config['ap_sym_dict'][sym_ap]['status']
            if re.match(r'\b.+(Root|Mesh).+\b', status):
                return True
        
        return False
    def get_aps_sym_dict(self):
        return self.ap_sym_dict
