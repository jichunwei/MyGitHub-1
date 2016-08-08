# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
NetgearL3Switch interfaces with NETGEAR L3 managed switch via telnet CLI.

Example:

    from ratenv import *
    ng = NetgearL3Switch.NetgearL3Switch(dict(init=False))
    ng.initialize()
    d1 = ng.do_cmd('show mac-addr-table')
    print d1

"""

import logging
import re
import telnetlib
import socket
import time

from RuckusAutoTest.models import TestbedComponent, ComponentBase

class NetgearL3Switch(ComponentBase):
    def __init__(self, config):
        """
        Component's constructor
        Initialized configuration should include the following values:
        - ip_addr: IP address of the switch
        - username/password: user credential to login to user EXEC mode
        - enable_password: password to enter privileged EXEC mode
        - prompt: the based prompt on the CLI of the switch
        - timeout: default timeout value to be used in expect commands
        """
        component_info = TestbedComponent.objects.get(name = "NetgearL3Switch")
        ComponentBase.__init__(self, component_info, config)
        self.conf = dict(ip_addr = '192.168.0.253',
                         username = 'admin',
                         password = '',
                         enable_password = '',
                         prompt = "\([a-zA-Z0-9]+\)\s*", #jluh updated 2013-10-29 An Nguyen: change to use the regex to cover all Netgear Switch name
                         timeout = 15,
                         init = True,
                         debug = 0
                         )
        self.conf.update(config)
        if self.conf['init']: self.initialize()

    def initialize(self):
        self.branch = 'netgear'
        self.ip_addr = self.conf['ip_addr']
        self.username = self.conf["username"]
        self.password = self.conf["password"]
        self.prompt = self.conf['prompt']
        self.enable_password = self.conf["enable_password"]
        self.user_exec_prompt = "%s >" % self.prompt
        self.priv_exec_prompt = "%s #" % self.prompt
        self.global_cfg_prompt = "%s \(Config\)#" % self.prompt
        self.interface_cfg_prompt = "%s \(Interface [0-9/]+\)#" % self.prompt
        self.interface_range_cfg_prompt = "%s \(conf-if-range-[0-9/\-]+\)#" % self.prompt
        self.timeout = int(self.conf["timeout"])

        self.more_or_quit_prompt = re.escape("--More-- or (q)uit")

        self.login()
        logging.info("Created NetgearL3Switch %s" % self.ip_addr)

    def _expect(self, expect_list, timeout = 0):
        """
        A wrapper around the telnetlib expect().
        This uses the configured timeout value.
        Returns the same tuple as telnetlib expect()
        """
        if not timeout:
            timeout = self.timeout
        ix, mobj, rx = self.telnet_client.expect(expect_list, timeout)
        return (ix, mobj, rx)

    def _expect_prompt(self, prompt = "", timeout = 0):
        """Expect a prompt and raise an exception if we don't get one. Returns only input."""
        if self.conf['debug']:
            import pdb
            pdb.set_trace()
        if not prompt:
            target_prompts = [self.prompt, self.more_or_quit_prompt]
        elif type(prompt) is list:
            target_prompts = prompt[:]
            target_prompts.append(re.compile(self.more_or_quit_prompt, re.M | re.I))
        else:
            target_prompts = [prompt, self.more_or_quit_prompt]
        mqp_pos = len(target_prompts) - 1

        buf = ""
        while True:
            ix, mobj, rx = self._expect(target_prompts, timeout)
            if ix == -1:
                raise Exception("Prompt %s not found" % target_prompts)
            buf += rx
            # Quit the loop if the prompt is found
            if ix != mqp_pos: break
            # Otherwise, press Enter to continue showing
            self.telnet_client.write("\n")

        return buf

    def close(self):
        """Terminate the telnet session"""
        try:
            self.telnet_client.close()
        except:
            pass

    def login(self):
        """
        Login to the switch and enter privileged exec mode.
        If a telnet session is already active this will close that session and create a new one.
        """
        self.close()
        self.telnet_client = telnetlib.Telnet(self.ip_addr)

        # Try to login user exec mode
        ix, mobj, rx = self._expect(["User:"])
        if ix:
            raise Exception("'User:' prompt not found")
        self.telnet_client.write(self.username + "\n")
        ix, mobj, rx = self._expect(["Password:"])
        if ix:
            raise Exception("'Password:' prompt not found")
        self.telnet_client.write(self.password + "\n")
        self._expect_prompt(self.user_exec_prompt)

        # Try to login privileged exec mode
        self.step_into_priv_exec_mode()

    def step_into_priv_exec_mode(self):
        self.telnet_client.write("enable\n")
        ix, mobj, rx = self._expect(["Password:"])
        if ix:
            raise Exception("'Password:' prompt not found")
        self.telnet_client.write(self.enable_password + "\n")
        self._expect_prompt(self.priv_exec_prompt)

    def do_cmd(self, cmd_text, prompt = "", timeout = 0):
        return self._do_cmd(cmd_text, prompt = prompt, timeout = timeout, return_raw = True)

    def _do_cmd(self, cmd_text, prompt = "", timeout = 0, return_raw = False):
        """
        Issue the specified cmd_text and return the complete response
        as a list of lines stripped of the following:
           Echo'd cmd_text
           CR and LR from each line
           Final prompt line
        A timeout value of 0 means use the default configured timeout.
        """
        #time.sleep(10) don't use sleep, please use timeout
        if not prompt:
            # Default to privileged exec mode
            prompt = self.priv_exec_prompt
        if not timeout:
            timeout = self.timeout

        try:
            # Empty input buffer
            self.telnet_client.read_very_eager()
            # Issue command
            logging.debug('[NGSW CMD INPUT] %s' % cmd_text)
            self.telnet_client.write(cmd_text + "\n")
            # Read data
            r = self._expect_prompt(prompt, timeout)
            logging.debug('[NGSW CMD OUTPUT] %s' % r)
        except (EOFError, socket.error):
            logging.info("Telnet session had been disconnected. Try to relogin")
            self.login()
            # Try to issue the command one more time
            self.telnet_client.write(cmd_text + "\n")
            # Read data
            r = self._expect_prompt(prompt, timeout)

        if return_raw: return r

        # Split at newlines
        rl = r.split("\n")
        # Remove any trailing \r
        rl = [x.rstrip('\r') for x in rl]
        # Filter empty lines and prompt
        rl = [x for x in rl if x and not x.startswith(prompt)]

        # Remove cmd_text from output and return the rest
        return rl[1:]

    def _goto_global_cfg_mode(self):
        """ Jump into global configuration mode """
        self._do_cmd("configure terminal", self.global_cfg_prompt)

    def _goto_interface_cfg_mode(self, inf):
        """ Jump into interface configuration mode """
        self._do_cmd("interface %s" % inf, self.interface_cfg_prompt)

    def _goto_interface_range_cfg_mode(self, inf_range):
        """ Jump into range interface configuration mode """
        self._do_cmd("interface range %s" % inf_range, self.interface_range_cfg_prompt)

    def _goto_priv_exec_mode(self):
        time.sleep(10)
        """ Jump back to privileged exec mode from any modes except user exec mode """
        try:
            self.telnet_client.write("\032")
        except socket.error:
            logging.info("Telnet session has been disconnected. Try to relogin")
            self.login()
        self._expect_prompt(self.priv_exec_prompt)

    def ping(self, target_addr):
        """ Perform a ping from the switch to a target device """
        res = self._do_cmd("ping %s" % target_addr)

        mobj = re.search("Receive count=([0-9]+)", res[0])
        if mobj and int(mobj.group(1)) > 0:
            return True
        return False

    def get_mac_table(self):
        """ Return the MAC table on the switch """
        res = self._do_cmd("show mac-addr-table")
        pattern = r"([0-9A-F:]{17}) +([0-9/]+) +[0-9]+ +([0-9]+) +([a-zA-Z]+)"
        mac_table = []
        for line in res:
            mobj = re.match(pattern, line)
            if not mobj: continue
            mac_table.append({"mac":mobj.group(1), "inf":mobj.group(2),
                              "vlan":mobj.group(3), "status":mobj.group(4)})
        return mac_table

#@author: chen.tao 2013-12-19 to add new function, according to ZF-6565
    def get_mac_by_interface(self, interface = '1/0/3'):
 
        res = self._do_cmd("show mac-addr-table interface %s" %interface )
        pattern = "(\S*\:+\S*)\s"
        mac = ""
        for line in res:
            mobj = re.search(pattern, line)
            if not mobj: continue 
            mac = mobj.group(1)
            break
        
        return mac
#@author: chen.tao 2013-12-19 to add new function, according to ZF-6565

    def get_vlan_ip_table(self):
        """ Return the show ip vlan on the switch"""
        res = self._do_cmd("show ip vlan")
        pattern = r"([0-9]+) +([0-9/]+) +([0-9.]+) +([0-9.]+)"
        vlan_ip_table = []
        for line in res:
            mobj = re.match(pattern, line)
            if not mobj: continue
            vlan_ip_table.append({"vlan_id":mobj.group(1), "inf":mobj.group(2),
                                  "ip_addr":mobj.group(3), "subnet_mask":mobj.group(4)})
        return vlan_ip_table

    def mac_to_interface(self, mac_addr):
        """ Detect the switch port that the device with given MAC address connects to """
        mac_table = self.get_mac_table()
        for device in mac_table:
            if device["mac"].upper() == mac_addr.upper():
                return device["inf"]
        return ""

    def enable_interface(self, inf):
        """
        Enable the given switch port. Use this function with care. Disable the port that connects
        to the test controller will terminate the telnet session
        """
        self._goto_global_cfg_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("no shutdown", self.interface_cfg_prompt)
        self._goto_priv_exec_mode()
        
        
    def enable_range_interface(self, inf):
        """
        Enable the given switch port. Use this function with care. Disable the port that connects
        to the test controller will terminate the telnet session
        """
        self._goto_global_cfg_mode()
        self._goto_interface_range_cfg_mode(inf)
        self._do_cmd("no shutdown", self.interface_range_cfg_prompt)
        self._goto_priv_exec_mode()
        
    def disable_interface(self, inf):
        """
        Disable the given switch port.
        """
        self._goto_global_cfg_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("shutdown", self.interface_cfg_prompt)
        self._goto_priv_exec_mode()

    def verify_component(self):
        """ Device should already be logged in. """
        try:
            self._goto_global_cfg_mode()
            self._goto_priv_exec_mode()
        except:
            pass

    def add_interface_to_vlan(self, inf, vlan, set_pvid = True, tagging = False):
        self._goto_global_cfg_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("vlan participation include %s" % vlan, self.interface_cfg_prompt)
        if set_pvid:
            self._do_cmd("vlan pvid %s" % vlan, self.interface_cfg_prompt)
        if tagging:
            self._do_cmd("vlan tagging %s" % vlan, self.interface_cfg_prompt)
        self._goto_priv_exec_mode()

    def remove_interface_from_vlan(self, inf, vlan):
        self._goto_global_cfg_mode()
        self._goto_interface_cfg_mode(inf)
        self._do_cmd("vlan participation exclude %s" % vlan, self.interface_cfg_prompt)
        self._goto_priv_exec_mode()

    def get_vlan_interfaces(self):
        vlan_if_list = []
        res = self._do_cmd("show ip vlan", self.priv_exec_prompt)
        pattern = r"(?P<vlan_id>\d+) +(?P<inf>[\d/]+) +(?P<ip_addr>[\d\.]+) +(?P<mask>[\d\.]+)"
        for line in res:
            mobj = re.match(pattern, line)
            if mobj:
                vlan_if_list.append({"vlan_id": mobj.group("vlan_id"),
                                     "inf": mobj.group("inf"),
                                     "ip_addr": mobj.group("ip_addr"),
                                     "mask": mobj.group("mask")})
        return vlan_if_list

    def set_bandwidth(self, inf, bandwidth):
        self._goto_global_cfg_mode()
        self._goto_interface_range_cfg_mode(inf)
        self._do_cmd("traffic-shape %s" % bandwidth, self.interface_range_cfg_prompt)
        self._goto_priv_exec_mode()
    
    # An Nguyen, Mar 2013
    # Add the function to support execute the set of command (Reference to the NetgearSwitchRouter)
    def do_cfg(self, cmd_block, print_out = True):
        self._goto_global_cfg_mode()
        for cmd in cmd_block.split('\n'):
            lresp = self.do_cmd(cmd.strip(), prompt=[self.prompt, self.user_exec_prompt, self.priv_exec_prompt,
                                                     self.priv_exec_prompt, self.global_cfg_prompt, 
                                                     self.interface_cfg_prompt, self.interface_range_cfg_prompt,
                                                     self.more_or_quit_prompt])
            if print_out:
                print lresp
        self._goto_priv_exec_mode()
            
    def clear_mac_table(self):
        self._do_cmd("clear mac-addr-table all")
    
    def configure_dhcp_relay(self, **kwargs):
        """
        This function is added to configure the dhcp relay option on Netgear Switch
        @author: An Nguyen, Jul 2013
        """
        relay_cfg = {'enable': True,
                     'dhcp_srv_ip': '192.168.0.252'}
        relay_cfg.update(kwargs)
        
        if relay_cfg['enable']:
            cmd_block = "bootpdhcprelay\nbootpdhcprelay serverip %s" % relay_cfg['dhcp_srv_ip']
        else:
            cmd_block = "no bootpdhcprelay"
        
        self.do_cfg(cmd_block)
        
    def __del__(self):
        self.close()

if __name__ == "__main__":
    cfg = {"ip_addr":"192.168.0.253", "username":"admin", "password":"", "enable_password":""}
    sw = NetgearL3Switch(cfg)

    print "Ping to 192.168.0.198", sw.ping("192.168.0.198")
    port = sw.mac_to_interface("00:13:92:20:cd:40")
    sw.disable_interface(port)
    print "Ping to 192.168.0.198", sw.ping("192.168.0.198")
    sw.enable_interface(port)
    print "Ping to 192.168.0.198", sw.ping("192.168.0.198")

