"""
ZD_Stations Testbed consists of the following components:

1) Zone Director
2) One or more remote stations

This testbed understands the following config parameters:
config['STA']: a sub-dictionary contains all the config for the station
config['ZD']: a sub-dictionary contains all the config for the Zone Director
"""
import logging
import re
import os
import time
import telnetlib
from RuckusAutoTest.components.HuaweiL3Switch import HuaweiL3Switch
from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.components.NetgearL3Switch import NetgearL3Switch

from RatLogger import RatLogger

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_station_by_ip_addr,
    create_server_by_ip_addr,
    create_linux_station_by_ip_addr,
    create_ruckus_ap_by_ip_addr
)

class ZD_Port_Base_Vlan(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo, config)
        self.testbed_info = testbedinfo
        # Initialize the Linux server component
        if config.has_key('server') and config['server'] is not None:
            self.components['LinuxServer'] = create_server_by_ip_addr(
                ip_addr = config['server'].pop('ip_addr'),
                username = config['server'].pop('user'),
                password = config['server'].pop('password'),
                root_password = config['server'].pop('root_password'))

        else:
            self.components['LinuxServer'] = None
            logging.info("Testbed '%s' does not have LinuxServer configured." % \
                         testbedinfo.name)

        # Install AP symbolic dictionary
        if config.has_key('ap_sym_dict'):
            ap_sym_dict = config['ap_sym_dict']

        else:
            ap_sym_dict = None
        
        self.init_aps_sym_dict(ap_sym_dict)
        
        if config.has_key('ap_mac_list'):
            self.ap_mac_list = config['ap_mac_list']
        
        # Initialize station components
        self.components['Station'] = []
        ip_list = self.config['sta_ip_list']
        for i in range(len(ip_list)):
            sta_dict = config['sta_conf'].copy()
            sta_dict['sta_ip_addr'] = ip_list[i]

            station = create_station_by_ip_addr(ip_addr = sta_dict.pop('sta_ip_addr'))
            self.components['Station'].append(station)

        self.shell_key = config['ZD'].pop('shell_key')
        # Initialize ZD CLI
        self.zd_cli = create_zd_cli_by_ip_addr(config['ZD']['ip_addr'],
                                               config['ZD']['username'],
                                               config['ZD']['password'],
                                               self.shell_key)
        self.components['ZoneDirectorCLI'] = self.zd_cli

        # Initialize the DUT component
        self.zd = create_zd_by_ip_addr(ip_addr = config['ZD'].pop('ip_addr'),
                                       username = config['ZD'].pop('username'),
                                       password = config['ZD'].pop('password'))
        self.zd.init_messages_bundled(self.zd_cli)
        self.components['ZoneDirector'] = self.zd
        self.dut = self.zd
        
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
            for ap_mac in self.get_aps_mac_list():
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

        # Initialize L3 switch component if its configuration is given
        # And also build the tables to map MAC address to Interface on the switch
        # and to map MAC address to VLAN on the switch
        if config.has_key('RoutingVLANs') and config['RoutingVLANs']:
            self.zd_vlan = str(config['RoutingVLANs'][0])
            self.remote_vlan = str(config['RoutingVLANs'][1])

        else:
            self.zd_vlan = "301"
            self.remote_vlan = ""

        self.mac_to_port = {}
        self.mac_to_vlan = {}                
#        if config.has_key('L3Switch') and config['L3Switch']:
#            self.components['L3Switch'] = NetgearL3Switch(config['L3Switch'])
        if config.has_key('L3Switch') and config['L3Switch']:
            #detect the device branch to support huawei switch
            #An Nguyen, an.nguyen@ruckuswireless.com @since: May 2012            
            telnet_to_device = telnetlib.Telnet(config['L3Switch']['ip_addr'])
            ix, mobj, rx = telnet_to_device.expect(['<Quidway>', 'FSM.*'])
            if not ix:
                self.components['L3Switch'] = HuaweiL3Switch(config['L3Switch'])
            else: 
                self.components['L3Switch'] = NetgearL3Switch(config['L3Switch'])
                
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

        else:
            # There is no managed switch in the testbed
            # This assumes that all APs stay in default VLAN
            for mac in self.mac_to_ap.keys():
                self.mac_to_vlan[mac] = self.zd_vlan

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
                        for mac in ap_info[1]:
                            uplink_macs.append(self.get_ap_mac_addr_by_sym_name(mac))

                        map_list.append((map_mac, uplink_macs,))

                    else:
                        raise Exception("Invalid layout structure: %s" % str(ap_info))

                self.form_mesh(rap_list, map_list)

        # confiure global txpower to minimus
        if os.path.exists('RAT_TXPOWER_MIN'):
            logging.info('Configure global txpower to minimus')
            txpwr = {'2.4G':'Min', '5G':'Min'}
            AP.cfg_global_tx_power(self.zd, txpwr)
            
        # Initialize the Linux PC component
        if config.has_key('LinuxPCs') and config['LinuxPCs'] is not None:
            for linpc_conf in config['LinuxPCs']:
                self.linpc = create_linux_station_by_ip_addr(config['LinuxPCs'][linpc_conf]['ip_addr'])
                self.components[linpc_conf] = self.linpc   
        else:
            self.components['LinuxPC1'] = None
            logging.info("Testbed '%s' does not have LinuxServer configured." % \
                         testbedinfo.name)
        
    def verify_testbed(self):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        logging.info("Testbed %s Verifying component" % (self.testbed_info.name))
        self.zd.verify_component()
        for station in self.components['Station']:
            station.verify_component()

        for ap in self.components['AP']:
            ap.verify_component()

        if self.components.has_key('L3Switch') and self.components['L3Switch']:
            self.components['L3Switch'].verify_component()
    
    def init_aps_sym_dict(self, ap_sym_dict):
        self.ap_sym_dict = ap_sym_dict

    def get_zd_shell_key(self):
        '''
        Return zd shell key which come from testbed setting.
        '''
        return self.shell_key 
    
    def get_ap_mac_addr_by_sym_name(self, ap_sym_name):
        if re.match(r'^[0-9A-Fa-f:]+$', ap_sym_name):
            return ap_sym_name
        if self.ap_sym_dict and self.ap_sym_dict.has_key(ap_sym_name):
            return self.ap_sym_dict[ap_sym_name]['mac']
        raise "AP symbolic name '%s' does not defined at testbed's attr 'ap_sym_dict'" % ap_sym_name

    def get_aps_mac_list(self):
        if len(self.ap_mac_list) > 0: return self.ap_mac_list
        return self.get_aps_sym_dict_as_mac_addr_list()

    def get_aps_sym_dict_as_mac_addr_list(self):
        if not self.ap_sym_dict: return []
        mac_list = []
        for ap in self.ap_sym_dict.itervalues():
            mac_list.append(ap['mac'])
        return mac_list
    
    def get_aps_sym_dict(self):
        return self.ap_sym_dict