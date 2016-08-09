'''
Description:
Created on 2010-8-2
@author: cwang@ruckuswireless.com    
'''
import logging
import re
import time

from RuckusAutoTest.models import TestbedBase

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_station_by_ip_addr,
    create_server_by_ip_addr,   
)

class ZD_Scaling(TestbedBase):
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
        
        self.components['AP'] = []
        tm0 = time.time()
        tm1 = time.time()        
        self.aps_info_list = [time.asctime(time.localtime(tm0)), tm0, int(tm1 - tm0),
                      []]
        
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