'''
Description: 
    Create a test bed for ZD smart redundancy.
        Support: Scaling + Smart redundancy.
Created on 2011-11-3
@author: cwang@ruckuswireless.com    
'''
import logging
import re
import time
import telnetlib
from copy import deepcopy

from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.common import lib_Constant as const

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_station_by_ip_addr,
    create_server_by_ip_addr,   
    create_ruckus_ap_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.components.lib.zd import (
    system_zd as sys,
)

from RuckusAutoTest.components.lib.zdcli import (
    smart_redundancy_info as sr,
)

#from RuckusAutoTest.components import NetgearSwitchRouter
from RuckusAutoTest.components.NetgearL3Switch import NetgearL3Switch
from RuckusAutoTest.components.HuaweiL3Switch import HuaweiL3Switch

class ZD_SM(TestbedBase):
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
            
        # Initialize the Linux IPV6 server component
        if config.has_key('ipv6_server') and config['ipv6_server'] is not None:
            self.components['LinuxServerIPV6'] = create_server_by_ip_addr(
                ip_addr = config['ipv6_server']['ip_addr'],
                username = config['ipv6_server']['user'],
                password = config['ipv6_server']['password'],
                root_password = config['ipv6_server']['root_password'])
        else:
            self.components['LinuxServerIPV6'] = None
            logging.info("Testbed '%s' does not have LinuxServerIPV6 configured." % \
                         testbedinfo.name)

        # Install AP symbolic dictionary
        if config.has_key('ap_sym_dict'):
            ap_sym_dict = config['ap_sym_dict']

        else:
            ap_sym_dict = None
            
        self.mac_to_ip = {}
        # This dictionary holds the references to the AP objects using their MAC address as key
        self.mac_to_ap = {}
        # This dictionary holds the list of MAC addresses of the APs of models using model name as key
        self.model_to_mac_list = {}
        
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


        tm0 = time.time()
        tm1 = time.time()        
        self.aps_info_list = [time.asctime(time.localtime(tm0)), tm0, int(tm1 - tm0),
                      []]
        
        #Create primary zd ipv4 components (gui and cli).
        zd1_ipv4_tag = "ZD1" 
        zd2_ipv4_tag = "ZD2"
      
        logging.info("Creating GUI and CLI Primary ZD components for %s" % self.config[zd1_ipv4_tag])  
        pri_zd_gui = self.create_zd_gui(config[zd1_ipv4_tag])
        pri_zd_cli = self.create_zd_cli(config[zd1_ipv4_tag])
        pri_zd_gui.init_messages_bundled(pri_zd_cli)
        
        logging.info("Creating GUI and CLI Secondary ZD components for %s" % self.config[zd2_ipv4_tag])
        sec_zd_gui = self.create_zd_gui(config[zd2_ipv4_tag])
        sec_zd_cli = self.create_zd_cli(config[zd2_ipv4_tag])
        sec_zd_gui.init_messages_bundled(sec_zd_cli)
        
        #create switch
        l3sw = None
        if config.has_key('L3Switch') and config['L3Switch']:
            #detect the device branch to support huawei switch
            #An Nguyen, an.nguyen@ruckuswireless.com @since: Jul, 2013            
            telnet_to_device = telnetlib.Telnet(config['L3Switch']['ip_addr'])
            ix, mobj, rx = telnet_to_device.expect(['<Quidway>', 'FSM.*'])
            if not ix:
                self.components['L3Switch'] = HuaweiL3Switch(config['L3Switch'])
            else: 
                self.components['L3Switch'] = NetgearL3Switch(config['L3Switch'])
                
            l3sw = self.components['L3Switch']
                
        self.zd = pri_zd_gui
        self.dut = pri_zd_gui
        self.zdcli = pri_zd_cli
        
        self.components['ZoneDirectorCLI'] = pri_zd_cli
        self.components['ZoneDirector'] = pri_zd_gui
        
        self.components['zd1'] = pri_zd_gui
        self.components['ZDCLI1'] = pri_zd_cli
        self.components['zd2'] = sec_zd_gui
        self.components['ZDCLI2'] = sec_zd_cli
        
        self.zd2 = sec_zd_gui
        
        #Disable smart redundancy if disable_sr is True in testbed configuraiton.
        if config.has_key('disable_sr') and config['disable_sr'] == True:
            logging.info("Disable Smart Redundancy in ZD1:%s" % pri_zd_cli.ip_addr)
            sr.set_no_sr(pri_zd_cli)
            logging.info("Disable Smart Redundancy in ZD2:%s" % sec_zd_cli.ip_addr)
            sr.set_no_sr(sec_zd_cli)
            
        #Set ZD1 and ZD2 as dual mode and set ipv6 settings.
        zd1_ipv6_tag = "ZD1IPV6"
        zd2_ipv6_tag = "ZD2IPV6"
        if self.config.has_key(zd1_ipv6_tag) and self.config.has_key(zd2_ipv6_tag):
            zd_ip_cfg = {'ip_version': const.DUAL_STACK,
#                         'ipv4': {'ip_alloc': 'dhcp',},
                         'ipv6': {'ipv6_addr': '',
                                  'ipv6_alloc': 'manual',
                                  'ipv6_gateway': config['ipv6_server']['gateway'],
                                  'ipv6_prefix_len': '64',
                                  'ipv6_pri_dns': config['ipv6_server']['ip_addr'],
                                  },
                         }
            
            zd1_ip_cfg = deepcopy(zd_ip_cfg)
            zd1_ip_cfg['ipv6']['ipv6_addr'] = config[zd1_ipv6_tag]['ip_addr']                               
            
            zd2_ip_cfg = deepcopy(zd_ip_cfg)
            zd2_ip_cfg['ipv6']['ipv6_addr'] = config[zd2_ipv6_tag]['ip_addr']
            
            zd_ip_cfg = {}
            logging.info("Set ZD1 IP configuration as %s" % zd1_ip_cfg)
            sys.set_device_ip_settings(pri_zd_gui, zd1_ip_cfg, const.DUAL_STACK, l3sw)
            logging.info("Set ZD2 IP configuration as %s" % zd2_ip_cfg)    
            sys.set_device_ip_settings(sec_zd_gui, zd2_ip_cfg, const.DUAL_STACK, l3sw)
                
            #Create primary and secondary ipv6 components (gui and cli).
            logging.info("Creating IPV6 GUI and CLI Primary ZD components for %s" % self.config[zd1_ipv6_tag])
            pri_zd_gui_ipv6 = self.create_zd_gui(config[zd1_ipv6_tag])
            pri_zd_gui_ipv6.init_messages_bundled(pri_zd_cli)                
            self.components['ZD1IPV6'] = pri_zd_gui_ipv6     
                   
            logging.info("Creating IPV6 GUI and CLI Secondary ZD components for %s" % self.config[zd2_ipv6_tag])
            sec_zd_gui_ipv6 = self.create_zd_gui(config[zd2_ipv6_tag])
            sec_zd_gui_ipv6.init_messages_bundled(sec_zd_cli)                
            self.components['ZD2IPV6'] = sec_zd_gui_ipv6     
        
        ap_conf = {'username': self.zd.username,
                   'password': self.zd.password}
                
        self.components['AP'] = []
#        for ap_info in all_aps_info:
        for ap_mac in self.get_aps_mac_list(config['ap_mac_list']):
            ap_info = self.zd.get_all_ap_info(ap_mac)
            ap_info2 = self.zd2.get_all_ap_info(ap_mac)
            if ap_info and ap_info['status'].lower().startswith('connected') \
            or ap_info2 and ap_info2['status'].lower().startswith('connected'):
                if ap_info and ap_info['status'].lower().startswith('connected'):
                    ap_conf['ip_addr'] = ap_info['ip_addr']
                if ap_info2 and ap_info2['status'].lower().startswith('connected'):
                    ap_conf['ip_addr'] = ap_info2['ip_addr']

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
    
    def cleanup(self):
        #make sure all APs connected to low MAC ZD
        ap_mac_list = self.config['ap_mac_list']
        
        zdcli1 = self.components['ZDCLI1']
        zdcli2 = self.components['ZDCLI2']
        
        from RuckusAutoTest.components.lib.zdcli import config_ap_policy as ap_policy
        from RuckusAutoTest.components.lib.zdcli import configure_ap as config_ap
        from RuckusAutoTest.components.lib.zdcli import ap_info_cli
        
        ap_policy._set_ap_auto_approve(zdcli1, {'auto_approve':True})
        ap_policy._remove_ap_auto_approve(zdcli2)
        
        config_ap.del_aps_by_mac(zdcli1, ap_mac_list)
        config_ap.del_aps_by_mac(zdcli2, ap_mac_list)
        logging.info("sleep 60 s")
        time.sleep(60)
        
        count = 3
        while count > 0:
            all_connected = True
            for ap_mac in ap_mac_list:
                status = ap_info_cli.get_ap_status(zdcli1, ap_mac)
                if 'connected' != status:
                    all_connected = False
                    logging.info("AP[%s] has not been connected yet!" % ap_mac)
                    break
            
            if all_connected:
                break
            
            logging.info("sleep 60 s")
            time.sleep(60)
            count -= 1
        
        
    def create_zd_gui(self, zd_cfg):
        '''
        Create zd gui and cli components.
        '''
        # Initialize the DUT component
        zd_gui = create_zd_by_ip_addr(ip_addr = zd_cfg['ip_addr'],
                                      username = zd_cfg['username'],
                                      password = zd_cfg['password'])
        
        return zd_gui
    
    def create_zd_cli(self, zd_cfg):
        '''
        Create zd gui and cli components.
        '''
        zd_cli = create_zd_cli_by_ip_addr(zd_cfg['ip_addr'],
                                          zd_cfg['username'],
                                          zd_cfg['password'],
                                          zd_cfg['shell_key'])
        
        return zd_cli

    def configure_ap_connection_mode(self, ap_mac, mode, discovery_method = "", undo_reboot = False):
        pass

        
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
        if re.match(r'^([0-9A-Fa-f][0-9A-Fa-f]:)+[0-9A-Fa-f][0-9A-Fa-f]$', ap_sym_name):
            return ap_sym_name
        if self.ap_sym_dict and self.ap_sym_dict.has_key(ap_sym_name):
            return self.ap_sym_dict[ap_sym_name]['mac']
        raise "AP symbolic name '%s' does not defined at testbed's attr 'ap_sym_dict'" % ap_sym_name

    #@author: Anzuo, I think the 2nd param "mac_list" is useless
    def get_aps_mac_list(self,mac_list=[]):
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