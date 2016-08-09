# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
StationWinPC is 'Windows PC (aka XP, Vista)' Station TestbedComponent.
"""
import sys
import os
import logging
import socket

from RuckusAutoTest.models import TestbedComponent, ComponentBase
from RuckusAutoTest.components.Station import Station
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import WlanTool

# Note that the name of the component class must match the name of this file for ease of runtime-reference
class StationWinPC(Station):
    _agent_port = 10010

    def __init__(self, config):
        """
        The constructor of the class is responsible for establishing a telnet connection
        to the remote station, then map the shared folder which contains all the tools to
        a local driver (Z:)
        Input:
        - sta_ip_addr: IP address of the remote station
        """
        component_info = TestbedComponent.objects.get(name='StationWinPC')
        Station.__init__(self, component_info, config)

        try:
            self.sta_ip_addr = config['sta_ip_addr']
        except:
            raise Exception ("StationWinPC config missing field")

        self._initialize()

    def remove_all_wlan(self):
        """
        Remove all SSIDs from windows prefered wireless network list.
        """
        return WlanTool.remove_all_wlan()

    def verify_component(self):
        """ Perform sanity check on the component: StationWinPC is there """
        logging.info("Sanity check: Verify Test engine can ping StationWinPC")
        try:
            utils.ping(self.sta_ip_addr)
        except:
            pass
        # Can ping
        #if "Timeout" in ping(self.ip_addr):
        #   raise Exception("RuckusAP sanity check fails: cannot ping AP %s " % self.ip_addr)

    def _read_data(self):
        """
        Try to read some data from the client socket and parse into two parts: a command string
        and its data
        @return: a tuple of command and data
        """
        res = self.client.recv(4096)
        lres = res.strip().split(';;')
        cmd = lres[0]
        data = ';'.join(lres[1:])
        return (cmd, data)

    def _initialize(self):
        """
        Initialize the client socket. Create it if it has not been initialized.
        """
        try:
            self.client.close()
        except:
            pass
        self.client = utils.socket.socket(utils.socket.AF_INET, utils.socket.SOCK_STREAM)
        self.client.connect((self.sta_ip_addr, self._agent_port))
        logging.debug("Open connection to the station %s" % self.sta_ip_addr)
        code, msg = self._read_data()
        if code == "error":
            raise Exception(msg)

    def do_cmd(self, cmd, arg=""):
        """
        Send a command with argument given in the arg parameter over the client socket.
        After that wait to receive response from the server about the execution of the command.
        @param cmd: the command that will be executed on the remote station; it should be the name
                    of the functions that are implemented on the Rat Tool Agent
        @param arg: argument passed to the function; it must be a string in format of a dictionary
        @return: the output of the remote execution
        """
        try:
            self.client.send("%s;%s\r\n" % (cmd, arg))
            logging.debug("Sent data: %s - %s" % (cmd, arg))
            code, msg = self._read_data()
            logging.debug("Receive result: %s - %s" % (code, msg))
            if code == "ok":
                return msg
            raise Exception(msg)
        except utils.socket.error, (err_code, err_msg):
            if err_code == 10054:
                logging.debug("Socket reset by peer")
                # Connection reset by peer
                self._initialize()
            raise

    def get_ip_addr(self):
        """ Return the Ip address of station."""
        return self.sta_ip_addr

    def cfg_wlan(self, wlan_conf, ap_conf = None):
        """
        WARNING:
        - The parameters' name does represent the expected param as it seams. Instead:
        - If the caller is originated from AP:
            + the 1st param is the 'config'
            + the 2nd param is the 'wlan_cfg'
        - If the caller is originated from ZD or FM:
            + only the 1st param is used, and it is the 'wlan_conf'
        
        ORIGINAL METHOD DOCSTRING:
        Configure the station to associate with the specified SSID
        using the supplied security parameters.
        The security parameters are the same that wpstool expects.
        All other prefered networks will be removed to ensure this is the
        only SSID with which the PC will associate.
        Input:
        - wlan_conf['ssid']: a string represents the SSID of the WLAN
        - wlan_conf['auth']: authentication method, can be "open", "shared", "PSK", or "EAP"
        - wlan_conf['wpa_ver']: WPA version, can be "WPA" or "WPA2"
        - wlan_conf['encryption']: encryption method, can be "WEP64", "WEB128", "TKIP" or "AES"
        - wlan_conf['key_string']: key material, can be a string of ASCII characters or string of hexadecimal characters
        - wlan_conf['key_index']: WEP key index, can be 1, 2, 3 or 4
        - wlan_conf['username'] and wlan_conf['password']: Radius username/password
        """
        if ap_conf is None:
            param = self.convert_to_wlan_profile_syntax(wlan_conf)
            return WlanTool.set_wlan_profile(**param)
        
        else:
            config = wlan_conf
            wlan_cfg = ap_conf
            return self.cfg_wlan_for_ap(config, wlan_cfg)


    def cfg_wlan_for_ap(self, config, wlan_cfg):
        """
        Create a wlan on the adapter
        """
        params = "{'config':%s, 'wlan_cfg':%s}" % (config, wlan_cfg)
        return self.do_cmd("config_wlan", params)


    def ping(self, target_ip, timeout_ms = 1000):
        """
        Execute a ping from the local host to the target IP address
        """
        param_str = "{'target_ip':'%s', 'timeout_ms':%s}" % (target_ip, timeout_ms)
        return self.do_cmd("ping", param_str)

    def add_ip_if(self, if_name, addr, mask):
        """
        Add an ip address to the specific interface
        Please refer to the corresponding function in WinRatToolAgent module for detail of parameters
        """
        param_str = "{'if_name':'%s', 'addr':'%s', 'mask':'%s'}" % (if_name, addr, mask)
        return self.do_cmd("add_ip_if", param_str)

    def get_if_info(self):
        """
        Get information of specific interface
        Refer to the corresponding function in WinRatToolAgent module for detail of input parameter and output result
        """
        return eval(self.do_cmd("get_if_info"))

    def get_ip_cfg(self, adapter_name = 'Local Area Connection'):
        """
        """
        return eval(self.do_cmd("get_ip_cfg", "{'adapter_name':'%s'}" % adapter_name))

    def verify_if(self, addr):
        """
        Verify configuration information of specific interface
        """
        return self.do_cmd("verify_if", "{'addr':'%s'}" % addr)

    def login_ap_web_ui(self, username, password, ip_addr):
        """
        Login to AP WebUI
        """
        params = "{'username':'%s', 'password':'%s', 'ip_addr':'%s'}" % (username, password, ip_addr)
        return self.do_cmd("login_ap_web_ui", params)

    def logout_ap_web_ui(self, ip_addr):
        """
        Logout from AP WebUI
        """
        return self.do_cmd("logout_ap_web_ui", "{'ip_addr':'%s'}" % ip_addr)

    def get_ap_wireless_status(self, ip_addr):
        """
        Get information of wireless status from AP WebUI
        Refer to the corresponding function in WinRatToolAgent for detail of input paramenter and output result
        """
        return eval(self.do_cmd("get_ap_wireless_status", "{'ip_addr':'%s'}" % ip_addr))

    def verify_station_mgmt(self, ap_ip_addr, aid, sta_mac_addr):
        """
        Verify that if STA-Management information is shown on the AP WebUI
        """
        params = "{'ap_ip_addr':'%s', 'aid':%s, 'sta_mac_addr':'%s'}" % (ap_ip_addr, aid, sta_mac_addr)
        return eval(self.do_cmd("verify_station_mgmt", params))

    def login_ad_web_ui(self, ap_ip_addr, aid):
        """
        Login to adapter WebUI
        """
        params = "{'ap_ip_addr':'%s', 'aid':%s}" % (ap_ip_addr, aid)
        return self.do_cmd("login_ad_web_ui", params)

    def get_ad_encryption(self, config, wlan_if):
        """
        Get wlan configuration information on the adapter
        """
        params = "{'config':%s, 'wlan_if':'%s'}" % (config, wlan_if)
        return eval(self.do_cmd("get_ad_encryption", params))


    def set_ruckus_ad_state(self, config, state, wlan_if):
        """
        Telnet to adapter CLI and set state for specified interface
        """
        params = "{'config':%s, 'state':'%s', 'wlan_if':'%s'}" % (config, state, wlan_if)
        return eval(self.do_cmd("set_ruckus_ad_state", params))

    def get_ruckus_ad_state(self, config, wlan_if):
        """
        Telnet to adapter CLI and get state of specified interface
        """
        params = "{'config': %s, 'wlan_if':'%s'}" % (config, wlan_if)
        return self.do_cmd("get_ruckus_ad_state", params)

    def get_ad_wireless_mac(self, config):
        """
        Telnet to adapter CLI and get mac address of wireless network
        """
        params = "{'config':%s}" % config
        return self.do_cmd("get_ad_wireless_mac", params)

    def set_ad_ssid_web_ui(self, config, ssid, is_vf7111):
        """
        Set SSID for adapter from its WebUI
        @param ssid: new ssid value
        @is_vf7111: This is the bool value to determine if adapter's model is vf7111 or not
        """
        params = "{'config':%s, 'ssid':'%s', 'is_vf7111':%s}" % (config, ssid, is_vf7111)
        return self.do_cmd("set_ad_ssid_web_ui", params)

    def set_ad_encryption_web_ui(self, config, encryption_cfg, is_vf7111):
        """
        Set encryption method for adapter from its WebUI
        @param encryption_cfg: new encryption method
        @is_vf7111: This is the bool value to determine if adapter's model is vf7111 or not
        """
        params = "{'config':%s, 'encryption_cfg':%s, 'is_vf7111':%s}" % (config, encryption_cfg, is_vf7111)
        return self.do_cmd("set_ad_encryption_web_ui", params)

    def get_ad_device_status_web_ui(self, config):
        """
        Get device status of adapter from its webui
        """
        params = "{'config':%s}" % config
        return eval(self.do_cmd("get_ad_device_status_web_ui", params))

    def set_ad_system_name_web_ui(self, config, system_name):
        """
        Set System name for adapter from its WebUI
        """
        params = "{'config':%s, 'system_name':'%s'}" % (config, system_name)
        return self.do_cmd("set_ad_system_name_web_ui", params)

    def set_ad_home_protection_web_ui(self, config, enable):
        """
        Enable/Disable Home Setting Protection feature for adapter
        """
        params = "{'config':%s, 'enable':%s}" % (config, enable)
        return self.do_cmd("set_ad_home_protection_web_ui", params)

    def set_ad_ssid(self, config, wlan_if, ssid):
        """
        Set SSID for adapter
        """
        params = "{'config':%s, 'wlan_if':'%s', 'ssid':'%s'}" % (config, wlan_if, ssid)
        return self.do_cmd("set_ad_ssid", params)

    def get_ad_home_login_info(self, config):
        """
        Get Home Login infor (username/password) of adapter from WebUI
        """
        params = "{'config':%s}" % config
        return eval(self.do_cmd("get_ad_home_login_info", params))

    def start_windump(self, **args):
        """
        Start capture traffic on the remote station using tcpdump tool
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        @return: the file path that save information of captured traffic
        """
        return self.do_cmd("start_windump", str(args))

    #add by serena tan 2010.9.10
    def start_windump_for_ap(self, **args):
        """
        Start capture traffic on the remote station using tcpdump tool
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        @return: the file path that save information of captured traffic
        """
        return self.do_cmd("start_windump_for_ap", str(args))

    def stop_windump(self):
        return self.do_cmd("stop_windump")

    def analyze_traffic(self, filename, proto = "UDP", get_qos = True):
        """
        Analyze traffic after capturing it by tcpdump tool
        @filename: name of file that saves traffic information
        @return: A list of dictionaries in there each dictionary include information of each packet (source ip address
        destination ip address, tos value)
        """
        params = "{'file_path':'%s', 'proto':'%s', 'get_qos':%s}" % (filename, proto, get_qos)
        return eval(self.do_cmd("analyze_traffic", params))

    def start_iperf(self, **args):
        return self.do_cmd("start_iperf", str(args))

    def stop_iperf(self):
        return self.do_cmd("stop_iperf")

    def add_route(self, route, net_mask, gateway):
        params = "{'route': '%s', 'net_mask': '%s', 'gateway':'%s'}" % (route, net_mask, gateway)
        return self.do_cmd("add_route", params)

    def delete_route(self, route):
        return self.do_cmd("delete_route", "{'route':'%s'}" % route)

    def __del__(self):
        """ Destructor: close the client socket """
        try:
            [logging.getLogger('').removeHandler(handler) for handler in logging.getLogger('').handlers
            if isinstance(handler, logging.FileHandler)]
            self.do_cmd("quit")
            self.client.close()
        except:
            pass

    def get_current_status(self):
        """
        Obtain current status of the wireless adapter on the local system
        """
        return WlanTool.get_current_status()

# Module test
if __name__ == "__main__":
    import time
    sta = StationWinPC()
    sta.remove_all_wlan()
    print "All wlan have been removed"

    start_time = time.time()
    while True:
        res = sta.get_current_status()
        if res == "disconnected":
            print "Status: disconnected"
            break
        if time.time() - start_time > 20:
            print "Timeout when trying to get status"
            exit()
            break

    wlan_conf = {'ssid':'thaiwlan', 'auth':'EAP', 'wpa_ver':'WPA', 'encryption':'AES', 'key_string':'', 'key_index':'',
                 'use_onex':True, 'username':'localuser', 'password':'localuser'}

    sta.cfg_wlan(wlan_conf)

    start_time = time.time()
    while True:
        res = sta.get_current_status()
        if res == "connected":
            print "Status: connected"
            break
        if time.time() - start_time > 20:
            print "Timeout when trying to get status"
            exit()
            break

    start_time = time.time()
    while True:
        res = sta.ping("192.168.0.20", 1, 1000)
        if res == "ok":
            print "ping done"
            exit()
        if time.time() - start_time > 20:
            print "Timeout when pinging"
            exit()

