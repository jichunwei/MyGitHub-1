# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
StationLinuxPC is a remote or local 'Linux PC' Station TestbedComponent (not the Test Controller)
"""

import logging
import socket

from RuckusAutoTest.models import TestbedComponent
from RuckusAutoTest.components.Station import Station
from RuckusAutoTest.common.Ratutils import ping


# Note that the name of the component class must match the name of this file for ease of runtime-reference
class StationLinuxPC(Station):

    _agent_port = 10010

    def __init__(self, config):
        """
        The constructor of the class is responsible for establishing a telnet connection
        to the remote station, then map the shared folder which contains all the tools to
        a local driver (Z:)
        Input:
        - sta_ip_addr: IP address of the remote station
        """
        component_info = TestbedComponent.objects.get(name = 'StationLinuxPC')
        Station.__init__(self, component_info, config)

        try:
            self.sta_ip_addr = config['sta_ip_addr']

        except:
            raise Exception ("StationLinuxPC config missing fields")

        self._initialize()


    def verify_component(self):
        """ Perform sanity check on the component: It is there """
        logging.info("Sanity check: Verify that StationLinuxPC %s is working" % self.sta_ip_addr)
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
        res = self.client.recv(4096)
        lres = res.strip().split(';')
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

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.sta_ip_addr, self._agent_port))
        logging.debug("Open connection to the station %s" % self.sta_ip_addr)
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
                self._initialize()

            raise


    def get_ip_addr(self):
        """
        Return the IP address of the Ethernet interface of the remote station
        @return: IP address of the Ethernet interface (management interface)
        """
        return self.sta_ip_addr


    def ping(self, target_ip, timeout_ms = 1000, ping_params = ""):
        """
        Execute a ping from the remote host to the target IP address
        @param target_ip: destination of the ping
        @param tries: number of tries
        @param timeout_ms: maximum time for a ping to be done
        @param ping_params: additional ping params to the default, for e.g. from which eth
        @return: "ok" if ping is done successfully or a message explains the failure
        """
        param_str = "{'target_ip': '%s', 'timeout_ms': %s, 'ping_params': '%s'}" % \
                    (target_ip, timeout_ms, ping_params)

        return self.do_cmd("ping", param_str)


    def start_iperf(self, **args):
        """
        Execute iperf to transmit traffic on the remote/local station
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        """
        return self.do_cmd("start_iperf", str(args))


    def stop_iperf(self):
        """
        Stop the running iperf on the remote/local station
        """
        return self.do_cmd("stop_iperf")


    def start_tcp_dump(self, **args):
        """
        Start capture traffic on the remote station using tcpdump tool
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        @return: the file path that save information of captured traffic
        """
        return self.do_cmd("start_tcp_dump", str(args))


    def stop_tcp_dump(self):
        return self.do_cmd("stop_tcp_dump")


    def analyze_traffic(self, filename, proto = "UDP", get_qos = True):
        """
        Analyze traffic after capturing it by tcpdump tool
        @filename: name of file that saves traffic information
        @return: A list of dictionaries in there each dictionary include information of each packet (source ip address
        destination ip address, tos value)
        """
        params = "{'file':'%s', 'proto':'%s', 'get_qos':%s}" % (filename, proto, get_qos)
        return eval(self.do_cmd("analyze_traffic", params))


    def set_ruckus_ad_state(self, config, state, wlan_if):
        params = "{'config':%s, 'state':'%s', 'wlan_if':'%s'}" % (config, state, wlan_if)
        return eval(self.do_cmd("set_ruckus_ad_state", params))


    def get_ruckus_ad_state(self, config, wlan_if):
        params = "{'config': %s, 'wlan_if':'%s'}" % (config, wlan_if)
        return self.do_cmd("getRuckusADState", params)


    def get_ad_wireless_mac(self, config):
        params = "{'config':%s}" % config
        return self.do_cmd("get_ad_wireless_mac", params)


    def get_if_config(self):
        return eval(self.do_cmd("get_ip_cfg"))


    def set_route(self, option = "", ip_addr = "", net_mask = "", if_name = ""):
        params = "{'option': '%s', 'ip_addr': '%s', 'net_mask': '%s', 'if_name':'%s'}" % (option, ip_addr, net_mask, if_name)
        return eval(self.do_cmd("set_route", params))


    def get_ad_sta_mgmt(self, config, wlan_if):
        """
        Get the status of sta-mgmt on the adapter
        """
        params = "{'config':%s, 'wlan_if':'%s'}" % (config, wlan_if)
        return eval(self.do_cmd("get_ad_sta_mgmt", params))


    def set_ad_sta_mgmt(self, config, wlan_if, enabled):
        """
        Please refer to the corresponding function in RatToolAgent module for details of parameters
        """
        params = "{'config':%s, 'wlan_if':'%s', 'enabled':%s}" % (config, wlan_if, enabled)
        return self.do_cmd("set_ad_sta_mgmt", params)


    def get_ad_if_brd_config(self, config):
        """
        Get interface configuration information at linux shell of the adapter
        """
        return eval(self.do_cmd("get_ad_if_brd_config", "{'config':%s}" % config))


    def ping_from_ad(self, config, target_ip, timeout_ms):
        """
        Do a ping from the adapter to the target ip address
        """
        params = "{'config':%s, 'target_ip':'%s', 'timeout_ms':%s}" % (config, target_ip, timeout_ms)
        return self.do_cmd("ping_from_ad", params)


    def get_ad_encryption(self, config, wlan_if):
        """
        Get wlan configuration information on the adapter
        """
        params = "{'config':%s, 'wlan_if':'%s'}" % (config, wlan_if)
        return eval(self.do_cmd("get_ad_encryption", params))


    def cfg_wlan(self, config, wlan_cfg):
        """
        Create a wlan on the adapter
        """
        params = "{'config':%s, 'wlan_cfg':%s}" % (config, wlan_cfg)
        return self.do_cmd("cfg_wlan", params)


    def set_ad_ssid(self, config, wlan_if, ssid):
        """
        Set SSID for adapter
        """
        params = "{'config':%s, 'wlan_if':'%s', 'ssid':'%s'}" % (config, wlan_if, ssid)
        return self.do_cmd("set_ad_ssid", params)


    def get_ad_ssid(self, config, wlan_if):
        """
        Get SSID value for the adapter
        """
        params = "{'config':%s, 'wlan_if':'%s'}" % (config, wlan_if)
        return self.do_cmd("get_ad_ssid", params)


    def get_ad_serial_num(self, config):
        """
        Get serial number of an adapter
        """
        params = "{'config':%s}" % config
        return self.do_cmd("get_ad_serial_num", params)


    def get_ad_version(self, config):
        """
        Get software version of an adapter
        """
        params = "{'config':%s}" % config
        return self.do_cmd("get_ad_version", params)


    def get_ad_device_type(self, config):
        """
        Get model of an adapter
        """
        params = "{'config':%s}" % config
        return self.do_cmd("get_ad_device_type", params)


    def get_ad_base_mac(self, config):
        """
        Get model of an adapter
        """
        params = "{'config':%s}" % config
        return self.do_cmd("get_ad_base_mac", params)


    def start_tcp_replay(self, **args):
        """
        send pcap packet using tcpreplay
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        """
        return self.do_cmd("start_tcp_replay", str(args))


    def capture_traffic_ota(self, **args):
        """
        Start capture traffic over the air on the remote station using tshark tool
        Please refer to the corresponding function on the LinuxRatToolAgent module for details of parameters
        """
        return self.do_cmd("capture_traffic_ota", str(args))


    def cfg_wlan_if(self, ip_addr = "", channel = ""):
        params = "{'ip_addr': '%s', 'channel': '%s'}" % (ip_addr, channel)
        return self.do_cmd("cfg_wlan_if", params)


    def analyze_traffic_ota(self, filename, dest_ip, src_ip):
        params = "{'filename':'%s', 'dest_ip':'%s', 'src_ip':'%s'}" % (filename, dest_ip, src_ip)
        return eval(self.do_cmd('analyze_traffic_ota', params))


    def start_zing(self, **args):
        """
        Execute zing to transmit traffic on the remote/local station
        Please refer to the corresponding function in the RatToolAgent module for details of parameters
        """
        return self.do_cmd("start_zing", str(args))


    def stop_zing(self):
        """
        Stop the running zing on the remote/local station
        """
        return self.do_cmd("stop_zing")


    def get_ad_channel(self, config, wlan_if):
        params = "{'config':%s, 'wlan_if':'%s'}" % (config, wlan_if)
        return eval(self.do_cmd("get_ad_channel", params))


    def set_ad_channel(self, config, wlan_if, channel):
        params = "{'config':%s, 'wlan_if':%s, 'channel':%s}" % (config, wlan_if, channel)
        return self.do_cmd("set_ad_channel", params)


    def stop_tshark(self):
        return self.do_cmd("stop_tshark")


    def add_vlan(self, interface, vlan_id, ip_addr):
        params = "{'interface':'%s', 'vlan_id':'%s', 'ip_addr':'%s'}" % (interface, vlan_id, ip_addr)
        return self.do_cmd("add_vlan", params)


    def rem_vlan(self, vlan_interface):
        return self.do_cmd("rem_vlan", "{'vlan_interface':'%s'}" % vlan_interface)


    def add_sub_intf(self, interface, ip_addr, subid):
        params = "{'interface':'%s', 'ip_addr':'%s', 'subid':'%s'}" % (interface, ip_addr, subid)
        return self.do_cmd("add_sub_intf", params)


    def rem_sub_intf(self, sub_if):
        return self.do_cmd("rem_sub_intf", "{'subif':'%s'}" % sub_if)


    def set_ip_addr (self, interface, ip_addr):
        params = "{'interface':'%s', 'ip_addr':'%s'}" % (interface, ip_addr)
        return self.do_cmd('set_ip_addr', params)


    def get_ftp_data(self, pcapfile, src_ip, dst_ip):
        params = "{'pcapfile':'%s', 'src_ip':'%s', 'dst_ip':'%s'}" % (pcapfile, src_ip, dst_ip)
        return eval(self.do_cmd("get_ftp_data", params))


    def create_copy_image(self, build, path = "/home/ftp/", name = "test.Bl7"):
        params = "{'build':'%s', 'path':'%s', 'name':'%s'}" % (build, path, name)
        self.do_cmd('create_copy_image', params)

        return name


    def __del__(self):
        """ Destructor: close the client socket """
        try:
            [logging.getLogger('').removeHandler(handler) for handler in logging.getLogger('').handlers
            if isinstance(handler, logging.FileHandler)]

            self.do_cmd("quit")
            self.client.close()

        except:
            pass

