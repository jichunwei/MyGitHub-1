# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
RemoteStationWinPC is a remote 'Windows PC (aka XP, Vista)' Station TestbedComponent (not the Test Controller)
"""
import os
import re
import time
import subprocess
import logging
import socket

from RuckusAutoTest.models import TestbedComponent
from RuckusAutoTest.components.Station import Station
from RuckusAutoTest.common.Ratutils import ping
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.common import utils
from RuckusAutoTest.common import lib_Constant as CONST

# Note that the name of the component class must match the name of this file for ease of runtime-reference
class RemoteStationWinPC(Station):

    _agent_port = 10010
    bufsize = 4096

    def __init__(self, config):
        """
        The constructor of the class is responsible for establishing a telnet connection
        to the remote station, then map the shared folder which contains all the tools to
        a local driver (Z:)
        Input:
        - sta_ip_addr: IP address of the remote station
        - username/password: security credential to access the remote PC and tool server
        - tool_ip_addr: IP address of the station that share the tool folder
        - tool_folder: the share name of the tool folder
        """
        component_info = TestbedComponent.objects.get(name = 'RemoteStationWinPC')
        Station.__init__(self, component_info, config)
        self.conf = dict(init = True, debug = 0)
        self.conf.update(config)
        try:
            self.ip_addr = self.sta_ip_addr = self.conf['sta_ip_addr']
        except:
            raise Exception ("RemoteStationWinPC config missing field 'sta_ip_addr'")
        self.eth_mac = None
        try:
            self.eth_mac = self.get_eth_mac(self.sta_ip_addr)
        except:
            raise Exception ("Cannot get the ethernet port mac address of station %s"%self.sta_ip_addr)
        
        if not self.eth_mac:
            raise Exception ("Cannot get the ethernet port mac address of station %s"%self.sta_ip_addr)
        logging.info("station[%s]'s eth_mac is %s"%(self.sta_ip_addr,self.eth_mac))
        if self.conf['init']: self.initialize()
        
    def get_eth_mac(self,target_ip):
        os.system('ping '+target_ip)
        time.sleep(5)
        output = subprocess.Popen('arp -a', stdout = subprocess.PIPE).communicate()[0]
        output=output.split('\r\n')
        pattern = r"((\d+\.){3}\d+)\s*([0-9a-f\-]{17})\s*dynamic"
        arp_dict={}
        for line in output:
            m=re.search(pattern,line)
            if m:
                ip = m.group(1)
                mac = m.group(3)
                mac=mac.replace('-',':')
                arp_dict[ip]=mac
        
        return arp_dict.get(target_ip)
    def verify_component(self):
        """ Perform sanity check on the component: It is there """
        logging.info("Sanity check: Verify that RemoteStationWinPC %s is working" % self.sta_ip_addr)
        try:
            ping(self.sta_ip_addr)
        except:
            pass

    def _read_data(self):
        """
        Try to read some data from the client socket and parse into two parts: a command string
        and its data
        @return: a tuple of command and data
        """
        res = self.client.recv(self.bufsize)             
        lres = res.strip().split(';;')
        cmd = lres[0]
        if cmd == 'ok':
            data = ';;'.join(lres[1:])
        else:
            data = lres[1]
            utils.log(';;'.join(lres[2:]))
        return (cmd, data)
    
    


    def initialize(self):
        """
        Initialize the client socket. Create it if it has not been initialized.
        """
        try:
            self.client.close()
        except:
            pass

        logging.debug("Open connection to the remote peer(%s %s)" % (str(self.sta_ip_addr), str(self._agent_port)))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.sta_ip_addr, self._agent_port))
        code, msg = self._read_data()
        if code == "error":
            raise Exception(msg)

    def do_cmd(self, cmd, arg = ""):
        """
        Send a command with argument given in the arg parameter over the client socket.
        After that wait to receive response from the server about the execution of the command.
        @param cmd: the command that will be executed on the remote station; it should be the name
                    of the functions that are implemented on the Rat Tool Agent
        @param arg: argument passed to the function; it must be a string in format of a dictionary
        @return: the output of the remote execution
        """
        bugme.do_trace_on('TRACE_RPC_DO_CMD')
        try:
            self.client.send("%s;%s\r\n" % (cmd, arg))
            logging.debug("Sent data: %s - %s" % (cmd, arg))
            code, msg = self._read_data()
            logging.debug("Receive result: %s - %s" % (code, msg))
            if code == "ok":
                return msg

            raise Exception(msg)

        except socket.error, (err_code, err_msg):
            if err_code == 10054:
                logging.debug("Socket reset by peer")
                # Connection reset by peer
                self.initialize()

            raise

    def get_ip_addr(self):
        """
        Return the IP address of the Ethernet interface of the remote station
        @return: IP address of the Ethernet interface (management interface)
        """
        return self.sta_ip_addr

    
    def restart_adapter(self):
        """
        Restart adapter from windows.
        """        
        return self.do_cmd("restart_adapter")
    
    def disable_adapter(self):
        """
        Disable adapter from windows.
        """
        return self.do_cmd("disable_adapter")
    
    def enable_adapter(self):
        """
        Enable adapter from windows.
        """
        return self.do_cmd("enable_adapter")
    
    def auth_wire_sta(self, username, password, domain = None):
        """
        Authenticate wire station.
        """
        if domain:
            param_str = "{'username':'%s', 'password':'%s', 'domain': '%s'}" \
            % (username, password, domain)
        else:
            param_str = "{'username':'%s', 'password':'%s'}" \
            % (username, password)
        
        return self.do_cmd("auth_wire_sta", param_str)
    
    
    def remove_all_wlan(self, adapter_name = ''):
        """
        Remove all SSIDs from windows prefered wireless network list.
        """
        param_str = "{'adapter_name':'%s'}" % adapter_name
        return self.do_cmd("remove_all_wlan", param_str)


    def cfg_wlan(self, wlan_conf):
        """
        Configure the station to associate with the specified SSID
        using the supplied security parameters.
        The security parameters are the same that wpstool expects.
        All other prefered networks will be removed to ensure this is the
        only SSID with which the PC will associate.
        @param wlan_conf: a dictionary define a security setting
        - wlan_conf['ssid']: a string represents the SSID of the WLAN
        - wlan_conf['auth']: authentication method, can be "open", "shared", "PSK", or "EAP"
        - wlan_conf['wpa_ver']: WPA version, can be "WPA" or "WPA2"
        - wlan_conf['encryption']: encryption method, can be "WEP64", "WEB128", "TKIP" or "AES"
        - wlan_conf['key_string']: key material, can be a string of ASCII characters or string of hexadecimal characters
        - wlan_conf['key_index']: WEP key index, can be 1, 2, 3 or 4
        - wlan_conf['username'] and wlan_conf['password']: Radius username/password
        """
        bugme.do_trace_on('TRACE_RPC_CFG_WLAN')
        param_str = str(self.convert_to_wlan_profile_syntax(wlan_conf))
        return self.do_cmd("set_wlan_profile", param_str)
    
    def ping6(self, target_ip, timeout_ms = 1000):
        """
        Execute a ping6 from the remote host to the target IP address
        @param target_ip: destination of the ping6
        @param tries: number of tries
        @param timeout_ms: maximum time for a ping to be done
        @return: "ok" if ping is done successfully or a message explains the failure
        """
        param_str = "{'target_ip':'%s', 'timeout_ms':%s}" % (target_ip, timeout_ms)
        return self.do_cmd("ping6", param_str)

    def ping(self, target_ip, timeout_ms = 1000):
        """
        Execute a ping from the remote host to the target IP address
        @param target_ip: destination of the ping
        @param tries: number of tries
        @param timeout_ms: maximum time for a ping to be done
        @return: "ok" if ping is done successfully or a message explains the failure
        """
        param_str = "{'target_ip':'%s', 'timeout_ms':%s}" % (target_ip, timeout_ms)
        return self.do_cmd("ping", param_str)

    def ping2(self, target_ip, timeout_ms = 1000, size = 32, disfragment = False, allow_loss = False):
        """
        Execute a ping from the remote host to the target IP address
        @param target_ip: destination of the ping
        @param tries: number of tries
        @param timeout_ms: maximum time for a ping to be done
        @param size: data size needed in pint
        @param disfragment: whether allow to make fragment in ping packet
        @return: "ok" if ping is done successfully or a message explains the failure
        """
        param_str = "{'target_ip':'%s', 'timeout_ms':%s, 'size':%s, 'disfragment':%s, 'allow_loss':%s}" %(target_ip, timeout_ms, size, disfragment, allow_loss)
        return self.do_cmd("ping2", param_str)
    
    def clean_arp(self):
        """
        Clean all arp info recorded on station.
        """
        return self.do_cmd("clean_arp")
    
    def get_current_status(self, adapter_name = ''):
        """
        Obtain current status of the wireless adapter on the remote system
        @return: the status of the wireless adapter on the remote station
        """
        param_str = "{'adapter_name':'%s'}" % adapter_name
        return self.do_cmd("get_current_status", param_str)


    def perform_web_auth(self, arg):
        """
        Do the web authentication on the remote station
        Input:
        @param username/password: user credential to provide to the authentication server
        """
        bugme.do_trace_on('TRACE_RPC_PERFORM_WEB_AUTH')

        return self.do_cmd("perform_web_auth", "%(arg)s" % locals())


    def perform_guest_auth(self, arg):
        """
        Do the Guest Pass authentication on the remote station
        Input:
        @param guest_pass: The generated guest pass if required
        @param use_tou: Terms Of Use if required (True/False)
        @param redirect_url: The redirected URL if required
        """
        bugme.do_trace_on('TRACE_RPC_PERFORM GUEST_AUTH')
        #param = {'guest_pass':guest_pass, 'use_tou':use_tou, 'redirect_url':redirect_url}
        return self.do_cmd("perform_guest_auth", "%(arg)s" % locals())


    def perform_hotspot_auth(self, arg):
        """
        Do the Hotspot authentication on the remote station
        Input:
        @param username: authentication credential
        @param password: authentication credential
        @param redirect_url: The redirected URL if required
        @param original_url: The starting URL that is used to trigger the authentication process
        """
        bugme.do_trace_on('TRACE_RPC_PERFORM_HOTSPOT_AUTH')
        #params = {'username':'', 'password':'', 'redirect_url':'', 'original_url':'http://172.16.10.252'}
        return self.do_cmd("perform_hotspot_auth", "%(arg)s" % locals())


    def perform_hotspot_deauth(self, logout_url):
        """
        Do the Hotspot logout on the wireless station
        Input:
        @param logout_url: the URL that is used to trigger the logout process
        """
        bugme.do_trace_on('TRACE_RPC_PERFORM_HOTSPOT_DEAUTH')
        params = {'logout_url':logout_url}
        return self.do_cmd("perform_hotspot_deauth", str(params))


    def get_wifi_addresses(self, adapter_name = ''):
        """
        Return the MAC and IP address of the wireless adapter on the remote system
        @return: a tuple of MAC and IP address
        """
        param_str = "{'adapter_name':'%s'}" % adapter_name
        return eval(self.do_cmd("get_addresses", param_str))
    
    def get_local_addresses(self, adapter_name = ''):
        """
        Return the adapter Local Area Connection Mac Address.
        """
        param_str = "{'adapter_name':'%s'}" % adapter_name
        return eval(self.do_cmd("get_local_address", param_str))
    
    def get_wifi_addresses_ipv6(self, adapter_name = ''):
        """
        Return the MAC and IPv4 and ipv6 address of the wireless adapter on the remote system
        @return: a tuple of MAC and IP address
        """
        param_str = "{'adapter_name':'%s'}" % adapter_name
        return eval(self.do_cmd("get_addresses_ipv6", param_str))

    def get_ip_config(self, adapter_name = ''):
        """
        Return the IPConfig information of the wireless adapter on the remote system
        @return: a dictionary of ipconfig information, ex: IP address, Subnet Mask, Mac address
        """
        param_str = "{'adapter_name':'%s'}" % adapter_name
        return eval(self.do_cmd("get_ip_cfg", param_str))


    def get_ip_cfg(self, adapter_name='Local Area Connection'):
        """
        Return the IPConfig information of the wireless adapter on the remote system
        @return: a dictionary of ipconfig information, ex: IP address, Subnet Mask, Mac address
        """
        bugme.do_trace_on('TRACE_RPC_GET_IP_CFG')

        ret = self.do_cmd("get_ip_config", "{'adapter_name':'%s'}" % adapter_name)
        return eval(ret)
    
    def get_8021x_address(self):
        """
        Return the IPConfig information of the wireless adapter on the remote system
        @return: a dictionary of ipconfig information, ex: IP address, Subnet Mask, Mac address
        """
        bugme.do_trace_on('TRACE_RPC_GET_IP_CFG')
        ret = self.do_cmd("get_8021x_address")
        return eval(ret)

    def set_ip_if(self, source, addr="", mask="", gateway="", if_name=""):
        """
        Set IP interface to the Ethernet NIC
        @author: Jane.Guo
        @since: 2013-5-8
        Please refer to the corresponding function in WinRatToolAgent module for detail of parameters
        """
        param_str = "{'source':'%s', 'addr':'%s', 'mask':'%s', 'gateway':'%s', 'if_name':'%s'}" % (
                     source, addr, mask, gateway, if_name)
        return self.do_cmd("set_ip_if", param_str)

    def check_ssid(self, ssid, adapter_name = ''):
        """
        Verify if the specified SSID can be discovered over the air by the remote station
        @return: the SSID itself if it is found, otherwise return ""
        """
        param_str = "{'ssid':'%s', 'adapter_name':'%s'}" % (ssid, adapter_name)
        return self.do_cmd("check_ssid", param_str)


    def send_zap(self, **args):
        """
        Execute zap to transmit traffic on the remote station
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        @return: the dictionary returned by the function collect_data()
        """
        bugme.do_trace_on('TRACE_RPC_SEND_ZAP')
        return eval(self.do_cmd("send_zap", str(args)))

    def send_zing(self, **args):
        """
        Execute zing to transmit traffic on the remote station
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        @return: the dictionary returned by the function collect_data()
        """
        bugme.do_trace_on('TRACE_RPC_SEND_ZING')
        return eval(self.do_cmd("send_zing", str(args)))

    def get_win_version(self):
        """
        Get Windows version of the remote station
        @return: "51" if it is running XP or "60" if Vista
        """
        return self.do_cmd("get_win_version")
    
    def get_os_platform(self):
        """
        Get Windows system, release, hostname of the remote station
        @return: a string such as "Windows,XP,tb32-sta1"
        """
        return self.do_cmd("get_os_platform")

    def cfg_wlan_with_zero_it(self, eth_if_ip_addr, ip_addr, net_mask, auth_method,
                             use_radius, activate_url, username, password, ssid):
        """
        Command the remote station to download Zero-IT tool and run it
        @param eth_if_ip_addr: IP address of the Ethernet interface on the remote station
        @param ip_addr: An IP address that is on the same subnet with ZD will be assigned to the Ethernet NIC
        @param net_mask: Subnet mask of the given IP address
        @param auth_method: Authentication method
        @param use_radius: Indicates that EAP is using Radius to authenticate or not
        @param activate_url: Activation URL to download zero-it tool on ZD
        @param username: Credential to download the tool
        @param password: Credential to download the tool
        @param ssid: Name of the SSID stored in the zero-it tool
        """
        bugme.do_trace_on('TRACE_RPC_CFG_WLAN_WITH_ZERO_IT')
        params = {'eth_if_ip_addr':eth_if_ip_addr, 'ip_addr':ip_addr, 'net_mask':net_mask,
                  'auth_method': auth_method, 'use_radius':use_radius, 'activate_url':activate_url,
                  'username':username, 'password':password, 'ssid':ssid}
        return self.do_cmd("cfg_wlan_with_zero_it", str(params))

    def download_zero_it(self, eth_if_ip_addr, ip_addr, net_mask, activate_url, username, password, ip_type = CONST.IPV4):
        """
        Command the remote station to download Zero-IT tool
        @param eth_if_ip_addr: IP address of the Ethernet interface on the remote station
        @param ip_addr: An IP address that is on the same subnet with ZD will be assigned to the Ethernet NIC
        @param net_mask: Subnet mask of the given IP address
        @param activate_url: Activation URL to download zero-it tool on ZD
        @param username: Credential to download the tool
        @param password: Credential to download the tool
        @param version: ip version, value is 4 and 6.
        """
        bugme.do_trace_on('TRACE_RPC_DOWNLOAD_ZERO_IT')
        params = {'eth_if_ip_addr':eth_if_ip_addr, 'ip_addr':ip_addr, 'net_mask':net_mask,
                  'activate_url':activate_url, 'username':username, 'password':password,
                  'ip_type': ip_type}
        return self.do_cmd("download_zero_it", str(params))

    def execute_zero_it(self, tool_path, ssid, auth_method, use_radius):
        """
        Execute the ZeroIT tool stored at the given path
        @param tool_path: Full path to the tool
        @param ssid: SSID of the WLAN
        @param use_radius: a boolean value indicates Radius is used or not
        @param auth_method: Authentication method
        """
        bugme.do_trace_on('TRACE_RPC_EXECUTE_ZERO_IT')
        params = {'tool_path':tool_path, 'ssid':ssid, 'auth_method':auth_method, 'use_radius':use_radius}
        return self.do_cmd("execute_zero_it", str(params))
    
    def login_ap_cli_and_exec_command(self,cmd_text,username,password,port,ip_addr):
        bugme.do_trace_on('TRACE_RPC_LOGIN_AP_CLI_SEND')
        params = {'text':cmd_text,'username':username,'password':password,'port':port,'ip_addr':ip_addr}
        return self.do_cmd("login_ap_cli_send", str(params))
        

    def get_wlan_profile_list(self):
        """
        This function returns the list of the existing wireless profiles on a wireless adapter of station
        """
        bugme.do_trace_on('TRACE_RPC_GET_WLAN_PROFILE_LIST')
        return eval(self.do_cmd("get_wlan_profile_list"))

    def connect_to_wlan(self, ssid, bssid = ""):
        """
        This function forces a station to connect to a specified WLAN
        """
        bugme.do_trace_on('TRACE_RPC_CONNECT_TO_WLAN')
        if bssid and self.get_win_version() == '51':
            raise Exception ("Connect to Wlan with BSSID support for Windows Vista Only")
        return self.do_cmd("connect_to_wlan", "{'ssid':'%s', 'bssid': '%s'}" % (ssid, bssid))

    def disconnect_from_wlan(self):
        """
        This function forces a station to disconnect to the currently associated WLAN
        """
        bugme.do_trace_on('TRACE_RPC_DISCONNECT_FROM_WLAN')
        return self.do_cmd("disconnect_from_wlan", "{}")

    def do_release_wifi_ip_address(self):
        """
        Release IP address of the wireless adapter on the remote station
        """
        bugme.do_trace_on('TRACE_RPC_DO_RELEASE_WIFI_IP_ADDRESS')
        return self.do_cmd("do_release_wifi_ip_address")
    
    def do_renew_wifi_ip_address(self):
        """
        Renew IP address of the wireless adapter on the remote station
        """
        bugme.do_trace_on('TRACE_RPC_DO_RENEW_WIFI_IP_ADDRESS')
        return self.do_cmd("do_renew_wifi_ip_address")

    def renew_wifi_ip_address(self):
        """
        Release and renew IP address of the wireless adapter on the remote station
        """
        bugme.do_trace_on('TRACE_RPC_RENEW_WIFI_IP_ADDRESS')
        return self.do_cmd("renew_wifi_ip_address")

    def set_eth_mtu(self, mtu = 1500, iptype = 'ipv4', eth_inf = 'Local Area Connection'):
        bugme.do_trace_on('TRACE_RPC_SET_ETH_MTU')
        param_str = "{'mtu':'%s', 'iptype':'%s', 'eth_inf':'%s'}" %(mtu, iptype, eth_inf)
        return self.do_cmd("set_eth_mtu", param_str)

    def transmit_traffic(self, dst_addr, protocol, dst_port):
        """
        This function is designed to verify traffic transmission against the L3/L4 ACL rules.
        The paramters therefore are copied from the corresponding keys of those rules
        @param dst_addr: the destination address, can be in format net-addr/mask-in-bit-length or the address alone
        @param protocol: the IP protocol, can be 'Any', '1', '6', or '17'
        @param dst_port: the destination port
        """
        addr = dst_addr.split('/')[0]
        bugme.do_trace_on('TRACE_RPC_TRANSMIT_TRAFFIC')
        s = "{'dst_addr':'%s', 'protocol':'%s', 'dst_port':'%s'}" % (addr, protocol, dst_port)
        self.do_cmd("transmit_traffic", s)

    def start_zapd(self, path = '', pause = 1.0):
        bugme.do_trace_on('TRACE_RPC_START_ZAPD')
        path = "".join([c.replace("\\", "\\\\") for c in path])
        return self.do_cmd("start_zapd", "{'path': '%s', 'pause': '%s'}" % (path, pause))

    def stop_zapd(self):
        bugme.do_trace_on('TRACE_RPC_STOP_ZAPD')
        return self.do_cmd("stop_zapd", "{}")

    def start_speedflex(self, path = '', pause = 1.0):
        bugme.do_trace_on('TRACE_RPC_START_SPEEDFLEX')
        path = "".join([c.replace("\\", "\\\\") for c in path])
        return self.do_cmd("start_speedflex", "{'path': '%s', 'pause': '%s'}" % (path, pause))

    def stop_speedflex(self, filename):
        bugme.do_trace_on('TRACE_RPC_STOP_SPEEDFLEX')
        return self.do_cmd("stop_speedflex", "{'filename': '%s'}" % filename)

    def download_speedflex(self, speedflex_url):
        bugme.do_trace_on('TRACE_RPC_DOWNLOAD_SPEEDFLEX')
        return self.do_cmd("download_speedflex", "{'speedflex_url':'%s'}" % speedflex_url)


    def start_tshark(self, **args):
        """
        Start capture traffic on the remote station using tshark tool
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        @return: the file path that save information of captured traffic
        """
        return self.do_cmd("start_tshark", str(args))
    
    
#    def read_tshark(self, params = ""):
#        """
#        Read tshark traffic on the remote station using tshark tool
#        Please refer to the corresponding function in the RatToolAgent module for details of parameters
#        @params: read format or filter        
#        """
#        params = "{'params':'%s'}" % (params)
#        return self.do_cmd("read_tshark", params)
    
    def analyze_tshark_traffic(self, params = "", expr = ""):
        """
        Analyze package via function filter
        """     
        args = "{'params':'%s', 'expr':'%s'}" % (params, expr)
        return self.do_cmd("analyze_tshark_traffic", args)
        
    
    def stop_tshark(self):
        return self.do_cmd("stop_tshark")
    
    def start_windump(self, ip_addr = "", params = ""):
        bugme.do_trace_on('TRACE_RPC_START_WINDUMP')
        return self.do_cmd("start_windump", "{'ip_addr':'%s', 'params':'%s'}" % (ip_addr, params))

    def start_windump_for_ap(self, ip_addr = "", count = "", proto = "", file_path = "", host = ""):
        bugme.do_trace_on('TRACE_RPC_START_WINDUMP')
        return self.do_cmd("start_windump_for_ap", "{'ip_addr':'%s', 'count':'%s', 'proto':'%s', 'file_path':'%s', 'host':'%s'}" %
                                                     (ip_addr, count, proto, file_path, host))

    def stop_windump(self):
        bugme.do_trace_on('TRACE_RPC_STOP_WINDUMP')
        return self.do_cmd("stop_windump", "{}")

    def parse_traffic(self):
        bugme.do_trace_on('TRACE_RPC_PARSE_TRAFFIC')
        return self.do_cmd("parse_traffic", "{}")

    def start_iperf(self, serv_addr = "", test_udp = True, packet_len = "", bw = "", timeout = "", tos = "", multicast_srv = False,port = 0):
        bugme.do_trace_on('TRACE_RPC_START_IPERF')
        return self.do_cmd("start_iperf", "{'serv_addr': '%s', 'test_udp':%s, 'packet_len':'%s', 'bw': '%s', 'timeout':'%s', 'tos':'%s', 'multicast_srv':%s,'port':%s}" %
                          (serv_addr, test_udp, packet_len, bw, timeout, tos, multicast_srv,port))

    def start_iperf_server(self, serv_addr = "", test_udp = True):
        bugme.do_trace_on('TRACE_RPC_START_IPERF_SERVER')
        return self.do_cmd("start_iperf", "{'serv_addr': '%s', 'test_udp':%s}" % (serv_addr, test_udp))

    def start_iperf_client(self, stream_srv = "", test_udp = True, packet_len = "", bw = "", timeout = "", tos = ""):
        bugme.do_trace_on('TRACE_RPC_START_IPERF_CLIENT')
        return self.do_cmd("start_iperf", "{'stream_srv': '%s', 'test_udp':%s, 'packet_len':'%s', 'bw': '%s', 'timeout':'%s', 'tos':'%s'}" %
                          (stream_srv, test_udp, packet_len, bw, timeout, tos))

    def stop_iperf(self):
        bugme.do_trace_on('TRACE_RPC_STOP_IPERF')
        return self.do_cmd("stop_iperf", "{}")

    def add_route(self, route = "", net_mask = "", gateway = ""):
        bugme.do_trace_on('TRACE_RPC_ADD_ROUTE')
        return self.do_cmd("add_route", "{'route': '%s', 'net_mask':'%s', 'gateway':'%s'}" % (route, net_mask, gateway))

    def delete_route(self, route):
        bugme.do_trace_on('TRACE_RPC_DELETE_ROUTE')
        return self.do_cmd("delete_route", "{'route': '%s'}" % route)

    def get_visible_ssid(self, adapter_name=""):
        bugme.do_trace_on('TRACE_RPC_GET_VISIBLE_SSID')
        return self.do_cmd("get_visible_ssid", "{'adapter_name': '%s'}" % adapter_name)


    def perform_web_auth_using_browser(self, browser_id, arg, **kwargs):
        '''
        Do the web authentication on the remote station using browser
        '''
        params = {
            'browser_id': browser_id,
            'web_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("perform_web_auth_using_browser", str(params))


    def perform_guest_auth_using_browser(self, browser_id, arg, **kwargs):
        '''
        Do the Guest Pass authentication on the remote station using browser
        '''
        params = {
            'browser_id': browser_id,
            'guest_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("perform_guest_auth_using_browser", str(params))
    
    #@author:yanan.yu @since:2015-4-16 @change:adapt to 9.10 self-service guestpass
    def get_selfservice_contact_using_browser(self, browser_id, arg, **kwargs):
        '''
        Generate the Guest pass via self-service on the remote station using browser
        '''
        params = {
            'browser_id': browser_id,
            'guest_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("get_selfservice_contact_using_browser", str(params))
        
    #@author:yanan.yu @since:2015-4-16 @change:adapt to 9.10 self-service guestpass
    def update_selfservice_contact_using_browser(self, browser_id, arg, **kwargs):
        '''
        Generate the Guest pass via self-service on the remote station using browser
        '''
        params = {
            'browser_id': browser_id,
            'guest_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("update_selfservice_contact_using_browser", str(params))
    
    #@author:yanan.yu @since:2015-4-16 @change:adapt to 9.10 self-service guestpass
    def generate_guestpass_with_selfservice_using_browser(self, browser_id, arg, **kwargs):
        '''
        Generate the Guest pass via self-service on the remote station using browser
        '''
        params = {
            'browser_id': browser_id,
            'guest_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("generate_guestpass_with_selfservice_using_browser", str(params))
    
    #@author:yanan.yu @since:2015-4-16 @change:adapt to 9.10 self-service guestpass
    def generate_multi_guestpass_with_selfservice_using_command(self, arg, **kwargs):
        '''
        Generate the Guest pass via self-service on the remote station using browser
        '''
        params = {
            'guest_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("generate_multi_guestpass_with_selfservice_using_command", str(params))

    #@author:yanan.yu @since:2015-4-16 @change:adapt to 9.10 self-service guestpass
    def perform_self_service_guest_auth_using_browser(self, browser_id, arg, **kwargs):
        '''
        Do the Guest Pass authentication on the remote station using browser
        '''
        params = {
            'browser_id': browser_id,
            'guest_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("perform_self_service_guest_auth_using_browser", str(params))

    def perform_hotspot_auth_using_browser(self, browser_id, arg, **kwargs):
        '''
        Do the Hotspot authentication on the remote station using browser
        '''
        params = {
            'browser_id': browser_id,
            'hotspot_auth_arg': arg,
        }
        params.update(kwargs)

        return self.do_cmd("perform_hotspot_auth_using_browser", str(params))


    def download_file_on_web_server(
            self, browser_id, validation_url, download_loc, file_name, **kwargs
        ):
        '''
        '''
        params = {
            'browser_id': browser_id,
            'validation_url': validation_url,
            'download_loc': download_loc,
            'file_name': file_name,
        }
        params.update(kwargs)

        return self.do_cmd("download_file_on_web_server", str(params))


    def init_and_start_browser(
            self, browser = "firefox", tries = 3, timeout = 15, **kwargs
        ):
        '''
        '''
        params = {
            'browser': browser,
            'tries': tries,
            'timeout': timeout,
        }
        params.update(kwargs)

        return eval(self.do_cmd("init_and_start_browser", str(params)))


    def close_browser(self, browser_id):
        '''
        '''
        params = {
            'browser_id': browser_id,
        }

        return self.do_cmd("close_browser", str(params))


    def send_arping(self, **kwargs):
        """
        @author: An Nguyen, an.nguyen@ruckuswireless.com
        The hardping is used to generate the broadcast arping packets
        """
        params = {'dest_ip': ''}
        params.update(kwargs)
        
        return eval(self.do_cmd("send_arping", str(params)))
    #######################yesongnan add for bonjour gateway
    def browse_bonjour_service(self, serv_type):
        """
        Browsing for _airplay._tcp
        Timestamp     A/R Flags if Domain                    Service Type              Instance Name
        16:39:48.346  Add     3 13 local.                    _airplay._tcp.            t5
        16:39:48.346  Add     3 13 local.                    _airplay._tcp.            t6
        
        output:
        [{'name': 't5', 'type': '_airplay._tcp.'},
        {'name': 't6', 'type': '_airplay._tcp.'}]
    
        ---ye.songnan
        """      
        params = "{'serv_type':'%s'}" % serv_type
        return self.do_cmd("browse_bonjour_service", params)
    
    def register_bonjour_service(self, serv_name, serv_type, port):
        """
        Use this function to register a bonjour service.
            serv_name can not contain spaces when register service.
            
        ---ye.songnan
        """     
        serv_name = serv_name.strip().replace(" ", "")    
        params = "{'serv_name':'%s', 'serv_type':'%s', 'port':'%s'}" % (serv_name, serv_type, port)
        return self.do_cmd("register_bonjour_service", params)
    def connect_to_server_port(self, server_ip, port):
        """
        To test if station could connect to the server's port.
        """
        
        params = "{'server_ip':'%s', 'port':'%s'}" % (server_ip, port)
        return self.do_cmd("connect_to_server_port", params)
    def kill_proc(self, proc_name):
        """
        Use this function to kill subprocess's process by process name.
    
        ---ye.songnan
        """        
        params = "{'proc_name':'%s'}" % proc_name
        return self.do_cmd("kill_proc", params)
###############################################################       

    def __del__(self):
        """ Destructor: close the client socket """
        try:
            [logging.getLogger('').removeHandler(handler) for handler in logging.getLogger('').handlers
            if isinstance(handler, logging.FileHandler)]

            self.do_cmd("quit")
            self.client.close()

        except:
            pass

