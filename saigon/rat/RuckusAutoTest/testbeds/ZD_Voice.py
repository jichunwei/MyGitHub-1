# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
ZD_Voice Testbed consists of the following components:

1) Zone Director
2) Ruckus APs
3) Linux Server
4) Netgear Switch
5) Spectralink Gateway
6) Spectralink SVP

This testbed understands the following config parameters:
{'L3Switch': {'enable_password': '',
            'ip_addr': '192.168.0.253',
            'password': '',
            'username': 'admin'},
'ZD': {'browser_type': 'firefox',
      'ip_addr': '192.168.0.2',
      'password': 'admin',
      'username': 'admin'},
'ap_mac_list': [u'00:25:c4:19:8e:00', u'00:22:7f:02:49:40'],
'ap_sym_dict': {'AP_01': {'mac': u'00:22:7f:02:49:40',
                        'model': u'zf2942',
                        'status': u'Connected (Root AP)'},
               'AP_02': {'mac': u'00:25:c4:19:8e:00',
                        'model': u'zf7962',
                        'status': u'Connected (Root AP)'}},
'server': {'ipaddr': '192.168.0.252',
          'passwd': 'lab4man1',
          'root_passwd': 'lab4man1',
          'user': 'lab'},
'splk_server': {'enabled': True,
               'gw_cfg': {'ip_addr': '192.168.0.220',
                         'password': 'admin',
                         'username': 'admin'},
               'svp_cfg': {'ip_addr': '192.168.0.230',
                          'password': 'admin',
                          'username': 'admin'}},
'push_keypad_device': {'dev': 'COM1',
                       'baudrate': 9600 }                          
                          }
config['ZD']: a sub-dictionary contains all the config for the Zone Director
config['ap_mac_list']: a sub-list contains all APs's mac 
config['server']: a sub-dictionary contains all the config for the Linux PC 
config['splk_server']: a sub-dictionary contains all the config for the spectralink gateway and server
config['L3Switch']: a sub-dictionary contains all the config for the netgear l3 switch
"""

from RuckusAutoTest.models     import TestbedBase

from RuckusAutoTest.components import RemoteStationWinPC
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import SpectralinkGW
from RuckusAutoTest.components import SpectralinkSVP
from RuckusAutoTest.components import RuckusAP
from RuckusAutoTest.components import NetgearL3Switch
from RuckusAutoTest.components import LinuxPC
from RuckusAutoTest.components.lib.zd import access_points_zd as ZDAP
from RuckusAutoTest.components import PushKeypadDevice

from RuckusAutoTest.common          import lib_Debug as bugme
from RuckusAutoTest.common          import Ratutils as utils
from RatLogger import RatLogger

import logging, time, re, os
from pprint import pformat
from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_station_by_ip_addr,
    create_server_by_ip_addr,
    create_ruckus_ap_by_ip_addr,
    clean_up_rat_env,
)
# Note that the name of the testbed class must match the name of this file for ease of runtime-reference
class ZD_Voice(TestbedBase):
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
            
        if config.has_key('splk_server') and config['splk_server']['enabled']:
            if config['splk_server'].has_key('gw_cfg') and config['splk_server'].has_key('svp_cfg'):
                self.components['SpectralinkGW'] = SpectralinkGW.SpectralinkGW(config['splk_server']['gw_cfg'])
                self.components['SpectralinkSVP'] = SpectralinkSVP.SpectralinkSVP(config['splk_server']['svp_cfg'])
            else:
                logging.info("Testbed '%s' does not have Spectralink Gateway and SVP configured" % testbedinfo.name)
        else:
            logging.info("Testbed '%s' does not have Spectralink enabled" % testbedinfo.name)

        # Install AP symbolic dictionary
        ap_sym_dict = config['ap_sym_dict'] if config.has_key('ap_sym_dict') else None
        self.init_aps_sym_dict(ap_sym_dict)

        # Initialize station components
        if config.has_key('sta_ip_list'):
            self.components['Station']=[]
            ip_list = self.config['sta_ip_list']
            for i in range(len(ip_list)):
                sta_dict = config['sta_conf'].copy()
                sta_dict['sta_ip_addr'] = ip_list[i]
                station = create_station_by_ip_addr(ip_addr = sta_dict.pop('sta_ip_addr'))
                self.components['Station'].append(station)

        # Initialize the DUT component
        cfg = dict(
            ip_addr = '192.168.0.2',
            username = 'admin',
            password = 'admin',
            model = 'zd',
            browser_type = 'firefox',
        )
        cfg.update(config['ZD'])
        self.zd_cli = create_zd_cli_by_ip_addr(config['ZD']['ip_addr'],
                                               config['ZD']['username'],
                                               config['ZD']['password'],
                                               config['ZD'].pop('shell_key'))
        self.components['ZoneDirectorCLI'] = self.zd_cli

        # Initialize the DUT component
        self.zd = create_zd_by_ip_addr(ip_addr = config['ZD'].pop('ip_addr'),
                                       username = config['ZD'].pop('username'),
                                       password = config['ZD'].pop('password'))
        self.zd.init_messages_bundled(self.zd_cli)
        self.components['ZoneDirector'] = self.zd
        self.dut = self.zd
#        sm = SeleniumManager()
#        cfg['selenium_mgr'] = sm
#        self.components['ZoneDirector'] = ZoneDirector.ZoneDirector(cfg)
#        #self.components['ZoneDirector'].start()
#        self.dut = self.components['ZoneDirector']

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
        self.aps_info_list = [time.asctime(time.localtime(tm0)), tm0, int(tm1-tm0), all_aps_info]

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

        # Initialize L3 switch component if its configuration is given
        if config.has_key('L3Switch') and config['L3Switch']:
            self.components['L3Switch'] = NetgearL3Switch.NetgearL3Switch(config['L3Switch'])
            logging.info("Detect the switch ports connect to the APs")
            
        if config.has_key('push_keypad_device') and config['push_keypad_device']:
            self.components['PushKeypadDevice'] = PushKeypadDevice.PushKeypadDevice(config['push_keypad_device'])
            logging.info("The push keypad device connected")

        # Set up the APs to a particular connection mode if requested
        if config.has_key("APConnMode"):
            logging.info("Configure all the AP in the testbed to '%s'" % config["APConnMode"])
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
                self.enableMesh()
            if config['Mesh']['enable'] and config['Mesh']['layout']:
                # Convert info stored in config['Mesh']['layout'] to the structures
                # that are used by the formMesh() function
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
                self.formMesh(rap_list, map_list)
        # confiure global txpower to minimus        
        #if os.path.exists('RAT_TXPOWER_MIN'):
        #    logging.info('Configure global txpower to minimus')
        #    txpwr = {'2.4G':'Min', '5G':'Min'}
        #    ZDAP.configGlobalTxPower(self.components['ZoneDirector'], txpwr)
            
        if config.has_key('super_ruca_id') and config['super_ruca_id']:
            for id in config['super_ruca_id']:
                logging.info("Reset super ruca [id %s] to 0 db" % id) 
                utils.set_super_ruca_attenuation(id, '0')
                
    def verify_testbed(self):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        logging.info("Testbed %s Verifying component" % (self.testbed_info.name))
        self.components['ZoneDirector'].verify_component()

        if self.components.has_key('L3Switch') and self.components['L3Switch']:
            self.components['L3Switch'].verify_component()
            
        self.components['SpectralinkGW'].verify_component()
        self.components['SpectralinkSVP'].verify_component()       

    def init_aps_sym_dict(self, ap_sym_dict):
        self.ap_sym_dict = ap_sym_dict

    def get_ap_mac_addr_by_sym_name(self, ap_sym_name):
        if re.match(r'^[0-9A-Fa-f:]+$', ap_sym_name):
            return ap_sym_name
        if self.ap_sym_dict and self.ap_sym_dict.has_key(ap_sym_name):
            return self.ap_sym_dict[ap_sym_name]['mac']
        raise "AP symbolic name '%s' does not defined at testbed's attr 'ap_sym_dict'" % ap_sym_name

    def get_aps_mac_list(self, ap_mac_list):
        if len(ap_mac_list) > 0: return ap_mac_list
        return self.get_aps_sym_dict_as_mac_addr_list()

    def get_aps_sym_dict_as_mac_addr_list(self):
        if not self.ap_sym_dict: return []
        mac_list = []
        for ap in self.ap_sym_dict.itervalues():
            mac_list.append(ap['mac'])
        return mac_list
    
    def configure_ap_connection_mode(self, ap_mac, mode, discovery_method = ""):
        """
        Configure the connection mode of the AP with given MAC address.
        This can be done by specifying the IP address of the ZD or moving the AP to/from the VLAN of the ZD
        @param ap_mac: MAC address of the AP object
        @param mode: new connection mode to be configured for the AP
        @param discovery_method: the method used by the AP to discover the ZD after changing to new mode
        """
        if not self.components.has_key("L3Switch"):
            raise Exception("There was not any managed switch present in the testbed")

        logging.debug("The AP '%s' VLAN: %s" % (ap_mac, self.mac_to_vlan[ap_mac]))
        logging.debug("The ZD VLAN: %s" % self.zd_vlan)
        logging.debug("Expected connection mode: %s" % mode.upper())

        ap_obj = self.mac_to_ap[ap_mac]
        mode = mode.lower()
        discovery_method = discovery_method.lower()
        rebooted = False
        logging.info("New connection mode: '%s' - discovery method: '%s'" % (mode, discovery_method))
        if discovery_method in ["fixed-pri", "fixed-sec"]:
            if discovery_method == "fixed-pri":
                ip1 = self.components["ZoneDirector"].ip_addr
                ip2 = ""
            else:
                ip1 = "1.1.1.1"
                ip2 = self.components["ZoneDirector"].ip_addr
            logging.info("Configure director info on the AP '%s' to '%s' and '%s'" % (ap_mac, ip1, ip2))
            ap_obj.set_director_info(ip1, ip2)
            logging.info("Reboot the AP to make the new change take effect")
            ap_obj.reboot()
            rebooted = True
        else:
            if discovery_method in ["dns", "dhcp"]:
                logging.info("Reset AP's configuration to factory default in order to clear the ZD record")
                ap_obj.set_factory()
            logging.info("Get current director information on the AP")
            zd_cfg_on_ap = ap_obj.get_director_cfg()
            if zd_cfg_on_ap["pri_zd_ip"] or zd_cfg_on_ap["sec_zd_ip"]:
                logging.info("Clear director information on the AP")
                ap_obj.set_director_info(ip1 = "", ip2 = "")
                ap_obj.reboot()
                rebooted = True
            if discovery_method and not rebooted:
                logging.info("Reboot the AP")
                ap_obj.reboot()
                rebooted = True

        if mode == "l3" and self.mac_to_vlan[ap_mac] == self.zd_vlan:
            if not rebooted:
                logging.info("Reboot the AP")
                ap_obj.reboot()
                rebooted = True
            logging.info("Move the AP from VLAN %s to VLAN %s" % (self.mac_to_vlan[ap_mac], self.remote_vlan))
            self.components["L3Switch"].remove_interface_from_vlan(self.mac_to_port[ap_mac],
                                                             self.mac_to_vlan[ap_mac])
            self.components["L3Switch"].add_interface_to_vlan(self.mac_to_port[ap_mac], self.remote_vlan)
            self.mac_to_vlan[ap_mac] = self.remote_vlan
        elif mode == 'l2':
            if self.mac_to_vlan[ap_mac] != self.zd_vlan:
                if not rebooted:
                    logging.info("Reboot the AP")
                    ap_obj.reboot()
                    rebooted = True
                logging.info("Move the AP from VLAN %s to VLAN %s" % (self.mac_to_vlan[ap_mac], self.zd_vlan))
                self.components["L3Switch"].remove_interface_from_vlan(self.mac_to_port[ap_mac], self.mac_to_vlan[ap_mac])
                self.components["L3Switch"].add_interface_to_vlan(self.mac_to_port[ap_mac], self.zd_vlan)
                self.mac_to_vlan[ap_mac] = self.zd_vlan
            else:
                rebooted = self.reboot_ap_if_not_l2_mode(ap_mac)

        if rebooted:
            logging.info("Try to reconnect to the AP after it is rebooted")
#            idx = self.components['AP'].index(ap_obj)
#            old_ip = ap_obj.ip_addr
#            logging.info("The AP's current IP address: %s" % old_ip)
#            logging.debug("Index of the AP object: %s" % idx)
#            old_log_file = ap_obj.log_file
#            del self.components['AP'][idx]
            base_time = time.time()
            while True:
                try:
                    logging.info("Detect the new IP leased of the AP at new VLAN")
                    self._detect_ap_dynamic_addresses([ap_mac])
                    logging.debug("MAC to IP table: %s" % self.mac_to_ip)
#                    if self.mac_to_ip[ap_mac] == old_ip:
#                        if time.time() - base_time > 360:
#                            msg = "The AP didn't get new IP address after moving into new VLAN"
#                            raise Exception(msg)
#                        time.sleep(10)
#                        continue

#                    ap_conf = {'username':self.components['ZoneDirector'].username,
#                               'password':self.components['ZoneDirector'].password,
#                               'ip_addr':self.mac_to_ip[ap_mac],
#                               'log_file':old_log_file}
                    ap_obj.ip_addr = self.mac_to_ip[ap_mac]
                    logging.info("Try to connect to the AP at new IP %s" % self.mac_to_ip[ap_mac])
                    ap_obj.verify_component()
#                    ap_obj = RuckusAP(ap_conf)
#                    self.components['AP'].append(ap_obj)
#                    self.mac_to_ap[ap_mac] = ap_obj
                    break
                except:
                    if time.time() - base_time > 360:
                        msg = "Unable to reconnect to the AP '%s' after making it become %s AP" % (ap_mac, mode)
                        raise Exception(msg)
                    time.sleep(10)
                    logging.info("Fail. Give it another try")

    def reboot_ap_if_not_l2_mode(self, ap_mac):
        ap_obj = self.mac_to_ap[ap_mac]
        apmgrinfo = ap_obj.get_ap_mgr_info()
        if (re.search('^l2', apmgrinfo['Tunnel/Sec Mode'], re.I) and
            re.search('^l2', apmgrinfo['ZoneDir found thru'], re.I)):
                return False
        logging.info("[AP %s] [mode '%s'] not in L2. Reboot it." % (ap_mac, apmgrinfo['Tunnel/Sec Mode']))
        ap_obj.reboot()
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
            if apmgrinfo and apmgrinfo["State"] == "RUN": break
            time.sleep(2)
            if time.time() - start_time > 120:
                raise Exception("AP '%s' was not in RUN state" % ap_mac)
        logging.debug("Obtained info: %s" % apmgrinfo)
        if apmgrinfo.has_key("ZoneDir found thru"):
            v = apmgrinfo["ZoneDir found thru"]
            apmgrinfo.pop("ZoneDir found thru")
            apmgrinfo["Discover Director By"] = v

        logging.info("Get detailed information in ZD's webui about the AP %s" % ap_mac)
        ap_info = self.components['ZoneDirector'].get_ap_info_ex(ap_mac)
        logging.debug("Obtained infor: %s" % ap_info)

        # Verify if the connection mode shown on AP's CLI and ZD are the same and correct
        conn_mode_in_zd = ap_info['info']['tunnel_mode'].lower()
        conn_mode_in_ap = apmgrinfo['Tunnel/Sec Mode'].split("/")[0].strip().lower()
        if conn_mode_in_ap != conn_mode_in_zd:
            msg = "The connection mode shown on AP's CLI was '%s'" % conn_mode_in_ap
            msg += ", which was different from the mode shown on ZD's webui '%s'" % conn_mode_in_zd
            return msg

        discovery_reason = {"fixed-pri": "Preferred Primary", "fixed-sec": "Preferred Secondary",
                            "dns": "DNS", "dhcp": "DHCP", "record": "Last ZoneDir Joined", "l2": "L2 Discovery"}
        if discovery_method in ["fixed-pri", "fixed-sec", "dns", "dhcp"]:
            if conn_mode_in_ap != "l3":
                msg = ("The connection mode was %s instead of L3 [AP %s] [dmode %s]" %
                      (conn_mode_in_ap.upper(), ap_mac, discovery_method))
                return msg
            if apmgrinfo['Discover Director By'] != discovery_reason[discovery_method]:
                msg = "The discover method showed on AP's CLI was '%s'" % apmgrinfo['Discover Director By']
                msg += ", it should have been '%s'" % discovery_reason[discovery_method]
                return msg
        elif discovery_method == "record":
            if apmgrinfo['Discover Director By'] != discovery_reason[discovery_method]:
                msg = "The discover method showed on AP's CLI was '%s'" % apmgrinfo['Discover Director By']
                msg += ", it should have been '%s'" % discovery_reason[discovery_method]
                return msg
        else:
            if self.mac_to_vlan[ap_mac] == self.zd_vlan:
                if conn_mode_in_ap != "l2":
                    msg = ("The connection mode was %s instead of L2 [AP %s] [dmode %s]" %
                          (conn_mode_in_ap.upper(), ap_mac, discovery_method))
                    return msg
                if apmgrinfo['Discover Director By'] not in discovery_reason["l2"]:
                    msg = "The discover method showed on AP's CLI was '%s'" % apmgrinfo['Discover Director By']
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
            logging.info("There was no L3Switch in the testbed. Unable to verify station MAC address")
            return ""

        if "zd_mac" not in dir(self):
            self.zd_mac = self.components["ZoneDirector"].get_mac_address().lower()

        mac_table = self.components["L3Switch"].get_mac_table()
        logging.debug("MAC address table: %s" % mac_table)
        logging.debug("AP MAC: %s - ZD MAC: %s - STA MAC: %s" % (active_ap_mac, self.zd_mac, sta_mac))

        zd_port = ap_port = sta_port = ""
        for mac_entry in mac_table:
            if mac_entry["mac"].lower() == self.zd_mac: zd_port = mac_entry["inf"]
            elif mac_entry["mac"].lower() == active_ap_mac: ap_port = mac_entry["inf"]
            elif mac_entry["mac"].lower() == sta_mac: sta_port = mac_entry["inf"]
        if not zd_port:
            raise Exception("Not found MAC address of the ZD '%s' on the L3 switch" % self.zd_mac)
        if not ap_port:
            raise Exception("Not found MAC address of the active AP '%s' on the L3 switch" % active_ap_mac)
        if not sta_port:
            raise Exception("Not found MAC address of the station '%s' on the L3 switch" % sta_mac)

        logging.debug("AP port: %s - ZD port: %s - STA port: %s" % (ap_port, zd_port, sta_port))
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
                
